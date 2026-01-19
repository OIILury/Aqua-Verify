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

        return issues


