"""
Moteur de conformité (règles explicites) - niveau dossier.

Objectif "pro" :
- règles auditables (pas de décision "magique")
- sortie structurée (liste d'écarts / actions)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import os

import yaml

from ..models.document import ProjectInfo, ComplianceIssue, Document, DocumentType


@dataclass(frozen=True)
class _RuleConfig:
    required_fields: List[str]
    required_documents: List[str]


class ComplianceEngine:
    """
    Évalue un dossier par rapport à un jeu de règles paramétré (YAML).
    """

    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            # app/services/ -> app/data/rules.yml
            base_dir = os.path.dirname(os.path.dirname(__file__))
            rules_path = os.path.join(base_dir, "data", "rules.yml")
        self.rules_path = rules_path
        self._rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def _get_profile(self, project_info: ProjectInfo) -> _RuleConfig:
        profiles = (self._rules.get("profiles") or {}) if isinstance(self._rules, dict) else {}
        # Par défaut : "base"
        profile_name = "base"
        if project_info.is_small_project is True:
            profile_name = "small"
        elif project_info.is_small_project is False:
            profile_name = "big"

        profile = profiles.get(profile_name) or profiles.get("base") or {}
        return _RuleConfig(
            required_fields=list(profile.get("required_fields") or []),
            required_documents=list(profile.get("required_documents") or []),
        )

    def evaluate(
        self,
        project_info: ProjectInfo,
        documents: List[Document],
        detected_types: Optional[List[DocumentType]] = None,
    ) -> List[ComplianceIssue]:
        """
        Retourne la liste d'écarts détectés.
        """
        issues: List[ComplianceIssue] = []

        # Règles de base sur champs essentiels
        if project_info.surface_m2 is None:
            issues.append(
                ComplianceIssue(
                    code="MISSING_SURFACE",
                    title="Surface du projet non détectée",
                    severity="warning",
                    message="Je n'ai pas trouvé la surface (m²). Ajoutez/clarifiez la surface dans le CERFA ou une notice.",
                    related_documents=["CERFA", "PC4"],
                )
            )

        # Construire l'ensemble des types détectés
        if detected_types is None:
            detected_types = [d.document_type for d in documents]

        detected_type_values = {t.value for t in detected_types if t}

        cfg = self._get_profile(project_info)

        # Règles fortes métier : certaines pièces doivent absolument être présentes
        for critical_code in ("PC3", "PC4"):
            if critical_code not in detected_type_values:
                issues.append(
                    ComplianceIssue(
                        code=f"CRITICAL_MISSING_{critical_code}",
                        title=f"Pièce indispensable manquante : {critical_code}",
                        severity="error",
                        message=(
                            f"La pièce {critical_code} est considérée comme indispensable dans le dossier. "
                            "Elle doit être présente et correctement identifiée dans les documents fournis."
                        ),
                        related_documents=[critical_code],
                    )
                )

        # Documents supplémentaires attendus selon profil (small/big)
        for doc_type in cfg.required_documents:
            if doc_type not in detected_type_values:
                issues.append(
                    ComplianceIssue(
                        code=f"MISSING_DOC_{doc_type}",
                        title=f"Document attendu manquant : {doc_type}",
                        severity="warning",
                        message=f"Le document {doc_type} est attendu pour ce type de projet, mais il n'a pas été détecté.",
                        related_documents=[doc_type],
                    )
                )

        # Champs supplémentaires attendus selon profil
        for field_name in cfg.required_fields:
            if getattr(project_info, field_name, None) is None:
                issues.append(
                    ComplianceIssue(
                        code=f"MISSING_FIELD_{field_name.upper()}",
                        title=f"Information manquante : {field_name}",
                        severity="warning",
                        message=f"L'information '{field_name}' n'a pas été détectée dans les documents. Ajoutez-la ou rendez-la plus explicite.",
                    )
                )

        # ===== RÈGLES SPÉCIFIQUES SELON LE FICHIER "Untitled" =====
        
        # Calculer le volume selon les formules réglementaires
        calculated_volume = self._calculate_required_volume(project_info)
        if calculated_volume is not None:
            project_info.calculated_volume_m3 = calculated_volume
        
        # Règles pour projets < 240 m²
        if project_info.is_small_project is True:
            issues.extend(self._evaluate_small_project_rules(project_info, detected_type_values))
        
        # Règles pour projets >= 240 m²
        elif project_info.is_small_project is False:
            issues.extend(self._evaluate_big_project_rules(project_info, detected_type_values))
        
        return issues

    def _calculate_required_volume(self, project_info: ProjectInfo) -> Optional[float]:
        """
        Calcule le volume à mettre en œuvre selon les formules réglementaires.
        
        Formules selon le fichier "Untitled" :
        - Si test d'infiltration OUI : Volume = Surface imperméable × 0,045 – Surface d'infiltration × Vitesse × 0,002
        - Si test d'infiltration NON : Volume = Surface imperméable × 0,045
        """
        if project_info.impermeabilized_area_m2 is None:
            return None
        
        surface_impermeable = project_info.impermeabilized_area_m2
        
        # Vérifier si test d'infiltration présent
        has_test = project_info.has_infiltration_test is True
        
        if has_test and project_info.infiltration_area_m2 is not None and project_info.infiltration_rate_mm_h is not None:
            # Formule avec test d'infiltration
            volume = (surface_impermeable * 0.045) - (project_info.infiltration_area_m2 * project_info.infiltration_rate_mm_h * 0.002)
        else:
            # Formule sans test d'infiltration
            volume = surface_impermeable * 0.045
        
        return max(0.0, volume)  # Volume ne peut pas être négatif

    def _evaluate_small_project_rules(self, project_info: ProjectInfo, detected_types: set) -> List[ComplianceIssue]:
        """
        Évalue les règles spécifiques aux projets < 240 m² selon le fichier "Untitled".
        """
        issues: List[ComplianceIssue] = []
        
        # Vérifier présence du formulaire d'instruction (CERFA)
        if "CERFA" not in detected_types:
            issues.append(
                ComplianceIssue(
                    code="SMALL_MISSING_CERFA",
                    title="Formulaire d'instruction manquant",
                    severity="error",
                    message="Un formulaire d'instruction des projets (CERFA) doit être présent et complété pour les projets < 240 m².",
                    related_documents=["CERFA"],
                )
            )
        
        # Vérifier présence du plan de masse (PC2)
        if "PC2" not in detected_types:
            issues.append(
                ComplianceIssue(
                    code="SMALL_MISSING_PC2",
                    title="Plan de masse manquant",
                    severity="error",
                    message="Un plan de masse doit être présent pour les projets < 240 m².",
                    related_documents=["PC2"],
                )
            )
        
        # Vérifier calcul de surface imperméabilisée
        if project_info.impermeabilized_area_m2 is None:
            issues.append(
                ComplianceIssue(
                    code="SMALL_MISSING_IMPERMEABILIZED_AREA",
                    title="Calcul de surface imperméabilisée manquant",
                    severity="warning",
                    message="Le calcul de la surface imperméabilisée doit être présent. "
                            "Surface imperméabilisée = surface des toitures non végétalisées + "
                            "surface des stationnements, voiries et accès imperméabilisés + "
                            "surface des terrasses sur support imperméable + "
                            "surface des stationnements perméables sur support imperméables.",
                )
            )
        
        # Vérifier volume calculé et minimum réglementaire
        if project_info.calculated_volume_m3 is not None and project_info.impermeabilized_area_m2 is not None:
            volume_minimum = 0.015 * project_info.impermeabilized_area_m2  # 0,015 m³/m²
            if project_info.calculated_volume_m3 < volume_minimum:
                issues.append(
                    ComplianceIssue(
                        code="SMALL_VOLUME_INSUFFICIENT",
                        title="Volume à mettre en œuvre insuffisant",
                        severity="error",
                        message=f"Le volume calculé ({project_info.calculated_volume_m3:.2f} m³) est inférieur au minimum réglementaire "
                                f"({volume_minimum:.2f} m³, soit 0,015 m³/m² imperméabilisé).",
                        evidence=f"Volume calculé: {project_info.calculated_volume_m3:.2f} m³ | Minimum requis: {volume_minimum:.2f} m³",
                    )
                )
        
        return issues

    def _evaluate_big_project_rules(self, project_info: ProjectInfo, detected_types: set) -> List[ComplianceIssue]:
        """
        Évalue les règles spécifiques aux projets >= 240 m² selon le fichier "Untitled".
        """
        issues: List[ComplianceIssue] = []
        
        # Vérifier présence de la note de calcul DEA
        if "NOTE_CALCUL_DEA" not in detected_types:
            issues.append(
                ComplianceIssue(
                    code="BIG_MISSING_NOTE_CALCUL_DEA",
                    title="Note de calcul DEA manquante",
                    severity="error",
                    message="Une note de calcul justifiant du dimensionnement du dispositif de rétention des eaux pluviales (DEA) "
                            "doit être présente pour les projets >= 240 m².",
                    related_documents=["NOTE_CALCUL_DEA"],
                )
            )
        
        # Vérifier présence du plan de masse (PC2)
        if "PC2" not in detected_types:
            issues.append(
                ComplianceIssue(
                    code="BIG_MISSING_PC2",
                    title="Plan de masse manquant",
                    severity="error",
                    message="Un plan de masse doit être présent pour les projets >= 240 m².",
                    related_documents=["PC2"],
                )
            )
        
        # Vérifier présence du test de perméabilité Matsuo
        if "TEST_MATSUO" not in detected_types:
            issues.append(
                ComplianceIssue(
                    code="BIG_MISSING_TEST_MATSUO",
                    title="Test de perméabilité Matsuo manquant",
                    severity="error",
                    message="Un test de perméabilité de type Matsuo doit être présent pour les projets >= 240 m².",
                    related_documents=["TEST_MATSUO"],
                )
            )
        
        # Vérifier rétention pluie courante > 15 mm
        if project_info.retention_rain_15mm is False:
            issues.append(
                ComplianceIssue(
                    code="BIG_RETENTION_15MM_INSUFFICIENT",
                    title="Rétention pluie courante insuffisante",
                    severity="error",
                    message="La rétention de pluie pour les pluies courantes doit être supérieure à 15 mm.",
                )
            )
        
        # Vérifier rétention pluie moyenne/forte > 45 mm
        if project_info.retention_rain_45mm is False:
            issues.append(
                ComplianceIssue(
                    code="BIG_RETENTION_45MM_INSUFFICIENT",
                    title="Rétention pluie moyenne/forte insuffisante",
                    severity="error",
                    message="La rétention de pluie pour les pluies moyennes à fortes doit être supérieure à 45 mm.",
                )
            )
        
        # Vérifier volume calculé et minimum réglementaire
        if project_info.calculated_volume_m3 is not None and project_info.impermeabilized_area_m2 is not None:
            volume_minimum = 0.015 * project_info.impermeabilized_area_m2  # 0,015 m³/m²
            if project_info.calculated_volume_m3 < volume_minimum:
                issues.append(
                    ComplianceIssue(
                        code="BIG_VOLUME_INSUFFICIENT",
                        title="Volume à mettre en œuvre insuffisant",
                        severity="error",
                        message=f"Le volume calculé ({project_info.calculated_volume_m3:.2f} m³) est inférieur au minimum réglementaire "
                                f"({volume_minimum:.2f} m³, soit 0,015 m³/m² imperméabilisé).",
                        evidence=f"Volume calculé: {project_info.calculated_volume_m3:.2f} m³ | Minimum requis: {volume_minimum:.2f} m³",
                    )
                )
        
        return issues


