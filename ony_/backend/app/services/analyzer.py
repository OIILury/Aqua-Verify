"""
Service d'analyse rule-based des documents
Système fait maison sans LLM pré-entraîné
"""
import re
from typing import List, Dict, Optional, Tuple, Iterable
from ..models.document import (
    Document, DocumentType, DocumentStatus, 
    AnalysisReport, ProjectInfo
)
from ..services.compliance import ComplianceEngine


class DocumentAnalyzer:
    """
    Analyseur de documents basé sur des règles (rule-based).
    Identifie les types de documents et vérifie leur conformité.
    """
    
    # Documents obligatoires par type de dossier
    REQUIRED_DOCUMENTS_BY_CASE = {
        # Permis de construire
        "PC": [
            DocumentType.PC1,
            DocumentType.PC2,
            DocumentType.PC3,
            DocumentType.PC4,
            DocumentType.PC5,
            DocumentType.PC6,
            DocumentType.PC7,
            DocumentType.PC8,
            DocumentType.CERFA,
        ],
        # Permis d'aménager (préparé pour usage futur)
        "PA": [
            DocumentType.PA1,
            DocumentType.PA2,
            DocumentType.PA3,
            DocumentType.PA4,
        ],
    }
    
    # Mots-clés pour identifier chaque type de document
    # Format: {DocumentType: {"filename": [...], "content": [...]}}
    IDENTIFICATION_RULES: Dict[DocumentType, Dict[str, List[str]]] = {
        DocumentType.CERFA: {
            "filename": ["cerfa", "formulaire"],
            "content": [
                "cerfa", "demande de permis", "permis de construire",
                "code de l'urbanisme", "déclaration préalable",
                "n° 13406", "n° 13409"
            ]
        },
        DocumentType.PC1: {
            "filename": ["pc1", "situation", "localisation"],
            "content": [
                "plan de situation", "situation du terrain",
                "localisation", "extrait cadastral", "cadastre"
            ]
        },
        DocumentType.PC2: {
            "filename": ["pc2", "masse", "implantation"],
            "content": [
                "plan de masse", "plan masse", "implantation",
                "emprise au sol", "limites de propriété",
                "voirie", "réseaux"
            ]
        },
        DocumentType.PC3: {
            "filename": ["pc3", "coupe", "profil"],
            "content": [
                "plan en coupe", "coupe du terrain", "profil",
                "altimétrie", "niveau du sol", "terrain naturel"
            ]
        },
        DocumentType.PC4: {
            "filename": ["pc4", "notice", "descriptif", "description"],
            "content": [
                "notice descriptive", "notice explicative",
                "description du terrain", "présentation du projet",
                "état initial", "projet architectural"
            ]
        },
        DocumentType.PC5: {
            "filename": ["pc5", "facade", "façade", "toiture", "elevation"],
            "content": [
                "plan des façades", "façades", "toitures",
                "élévation", "vue de face", "pignon"
            ]
        },
        DocumentType.PC6: {
            "filename": ["pc6", "insertion", "integration", "3d", "perspective"],
            "content": [
                "insertion", "intégration", "document graphique",
                "perspective", "simulation", "photomontage"
            ]
        },
        DocumentType.PC7: {
            "filename": ["pc7", "photo", "environnement", "proche"],
            "content": [
                "photographie", "environnement proche",
                "vue rapprochée", "abords immédiats"
            ]
        },
        DocumentType.PC8: {
            "filename": ["pc8", "photo", "paysage", "lointain"],
            "content": [
                "photographie", "paysage lointain",
                "vue éloignée", "environnement large"
            ]
        },
        DocumentType.AVIS_EP: {
            "filename": ["ep", "eaux pluviales", "pluvial"],
            "content": [
                "eaux pluviales", "gestion des eaux",
                "infiltration", "rétention", "bassin"
            ]
        },
        DocumentType.AVIS_DEA: {
            "filename": ["dea", "assainissement"],
            "content": [
                "direction de l'eau", "assainissement",
                "raccordement", "eaux usées"
            ]
        },
        DocumentType.COUPE_BASSIN: {
            "filename": ["bassin", "coupe bassin", "retention"],
            "content": [
                "coupe bassin", "bassin de rétention",
                "ouvrage de stockage", "volume de stockage"
            ]
        },
        # Pièces pour permis d'aménager
        DocumentType.PA1: {
            "filename": ["pa1", "situation", "localisation", "cadastre"],
            "content": [
                "plan de situation", "situation du terrain",
                "extrait cadastral", "plan de cadastre"
            ]
        },
        DocumentType.PA2: {
            "filename": ["pa2", "notice", "description", "descriptif"],
            "content": [
                "notice descriptive", "notice d'aménagement",
                "description du terrain", "présentation du projet d'aménagement"
            ]
        },
        DocumentType.PA3: {
            "filename": ["pa3", "etat actuel", "etat des lieux", "existant"],
            "content": [
                "plan de l'état actuel", "état des lieux",
                "plan de l'état des lieux", "état actuel du terrain"
            ]
        },
        DocumentType.PA4: {
            "filename": ["pa4", "composition", "ensemble", "3d", "perspective"],
            "content": [
                "plan de composition d'ensemble", "composition d'ensemble",
                "vue 3d", "perspective du projet", "plan d'ensemble du projet"
            ]
        },
    }
    
    def __init__(self, case_type: str = "PC"):
        """Initialise l'analyseur
        
        Args:
            case_type: Type de dossier ("PC" pour permis de construire,
                       "PA" pour permis d'aménager, etc.).
        """
        self.analyzed_documents: List[Document] = []
        self.project_info = ProjectInfo()
        self.case_type = case_type.upper() if case_type else "PC"
        self._candidate_types = set(self._get_candidate_types(self.case_type))

    def _get_candidate_types(self, case_type: str) -> Iterable[DocumentType]:
        """
        Retourne les types de documents à considérer pour l'identification,
        afin d'éviter les confusions entre familles (PC vs PA).
        """
        common = [
            DocumentType.AVIS_EP,
            DocumentType.AVIS_DEA,
            DocumentType.DPC,
            DocumentType.COUPE_BASSIN,
        ]

        if case_type == "PA":
            return [
                DocumentType.PA1,
                DocumentType.PA2,
                DocumentType.PA3,
                DocumentType.PA4,
                *common,
            ]

        # Par défaut : PC
        return [
            DocumentType.PC1,
            DocumentType.PC2,
            DocumentType.PC3,
            DocumentType.PC4,
            DocumentType.PC5,
            DocumentType.PC6,
            DocumentType.PC7,
            DocumentType.PC8,
            DocumentType.CERFA,
            *common,
        ]
    
    def identify_document_type(
        self, 
        filename: str, 
        content: str
    ) -> Tuple[DocumentType, float]:
        """
        Identifie le type d'un document basé sur son nom et contenu.
        
        Args:
            filename: Nom du fichier
            content: Texte extrait du document
            
        Returns:
            Tuple (type de document, score de confiance)
        """
        filename_lower = filename.lower()
        content_lower = content.lower() if content else ""
        
        best_match = DocumentType.AUTRE
        best_score = 0.0

        # 1) Heuristique "cartouche" très forte : PC1..PC8 / PA1..PA4 explicite
        if content_lower:
            # On ne regarde que le début du document (cartouche / titre)
            header = content_lower[:600]
            cartouche_match = re.search(r"\b(pc\s*[1-8]|pa\s*[1-4])\b", header)
            if cartouche_match:
                raw_code = cartouche_match.group(1)
                piece_code = raw_code.replace(" ", "").upper()  # "pc 4" -> "PC4"
                try:
                    doc_type = DocumentType[piece_code]
                    # On respecte le filtre PC/PA pour éviter de tagger un PA en PC quand on est en mode PC
                    if doc_type in self._candidate_types:
                        return doc_type, 0.99
                except KeyError:
                    pass

        # 2) Scoring classique basé sur mots-clés
        for doc_type, rules in self.IDENTIFICATION_RULES.items():
            # Évite les confusions PC/PA : on ne compare que les types pertinents
            if doc_type not in self._candidate_types:
                continue
            score = 0.0
            matches = 0
            total_checks = 0
            
            # Vérifier les mots-clés dans le nom du fichier (poids: 40%)
            for keyword in rules.get("filename", []):
                total_checks += 1
                if keyword.lower() in filename_lower:
                    matches += 1
                    score += 0.4
            
            # Vérifier les mots-clés dans le contenu (poids: 60%)
            for keyword in rules.get("content", []):
                total_checks += 1
                if keyword.lower() in content_lower:
                    matches += 1
                    score += 0.6
            
            # Normaliser le score
            if total_checks > 0:
                normalized_score = min(score / (total_checks * 0.3), 1.0)

                # Bonus fort si le code de pièce apparaît clairement dans le nom du fichier (ex: "PC4_Notice.pdf")
                piece_code = doc_type.value.lower()
                if piece_code in filename_lower:
                    normalized_score = min(1.0, normalized_score + 0.4)

                if normalized_score > best_score:
                    best_score = normalized_score
                    best_match = doc_type
        
        # Si le score est trop bas, c'est un document non identifié
        if best_score < 0.2:
            return DocumentType.AUTRE, best_score
        
        return best_match, best_score
    
    def extract_project_info(self, documents: List[Document]) -> ProjectInfo:
        """
        Extrait les informations du projet depuis les documents.
        
        Args:
            documents: Liste des documents analysés
            
        Returns:
            Informations du projet
        """
        project_info = ProjectInfo()
        
        # Chercher dans le CERFA ou la notice pour les infos du projet
        for doc in documents:
            source_text = doc.full_text or doc.extracted_text
            if source_text:
                text = source_text.lower()
                
                # Chercher la surface
                surface_patterns = [
                    # CERFA (souvent: "Surface de plancher créée", "Surface de plancher : 123 m²", etc.)
                    r"surface\s*de\s*plancher\s*cr[ée]e\s*[:\s]*(\d[\d\s]*(?:[.,]\d+)?)\s*m\s*[²2]",
                    r"surface\s*de\s*plancher\s*(?:totale)?\s*[:\s]*(\d[\d\s]*(?:[.,]\d+)?)\s*m\s*[²2]",
                    r"surface\s*(?:de\s*plancher|totale)?\s*[:\s]*(\d+(?:[.,]\d+)?)\s*m",
                    r"(\d+(?:[.,]\d+)?)\s*m[²2]\s*(?:de\s*)?(?:surface|plancher)",
                    r"surface\s*[:\s]*(\d+(?:[.,]\d+)?)",
                ]
                
                for pattern in surface_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            raw = match.group(1).replace(" ", "").replace("\u00A0", "")
                            surface = float(raw.replace(",", "."))
                            project_info.surface_m2 = surface
                            project_info.is_small_project = surface < 240
                            break
                        except ValueError:
                            continue
                
                # Chercher l'adresse
                address_patterns = [
                    r"adresse\s*(?:du\s*terrain)?\s*[:\s]*([^\n]+)",
                    r"situé\s*(?:à|au)?\s*[:\s]*([^\n]+)",
                ]
                
                for pattern in address_patterns:
                    match = re.search(pattern, text)
                    if match and not project_info.address:
                        project_info.address = match.group(1).strip()[:200]
                        break
                
                # Chercher la référence du dossier
                ref_patterns = [
                    r"(?:n°|numéro|référence)\s*(?:de\s*dossier)?\s*[:\s]*([A-Z0-9\-]+)",
                    r"PC\s*(\d+[\s\-]?\d*)",
                ]
                
                for pattern in ref_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match and not project_info.reference:
                        project_info.reference = match.group(1).strip()
                        break

                # Indices "eaux pluviales" (heuristiques simples pour commencer)
                if "infiltration" in text and project_info.infiltration is None:
                    project_info.infiltration = True
                if ("rétention" in text or "retention" in text or "bassin" in text) and project_info.retention is None:
                    project_info.retention = True

                # Volumes (m3) - ex: "volume de stockage : 120 m3"
                volume_patterns = [
                    r"volume\s*(?:de\s*)?(?:stockage|rétention|retention)?\s*[:\s]*(\d+(?:[.,]\d+)?)\s*m3",
                    r"(\d+(?:[.,]\d+)?)\s*m3\s*(?:de\s*)?(?:stockage|rétention|retention)",
                ]
                for pattern in volume_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            v = float(match.group(1).replace(",", "."))
                            project_info.retention_volume_m3 = v
                            break
                        except ValueError:
                            continue

                # Débit de fuite (L/s) - ex: "débit de fuite: 5 l/s"
                flow_patterns = [
                    r"d[ée]bit\s*(?:de\s*)?fuite\s*[:\s]*(\d+(?:[.,]\d+)?)\s*l\s*/\s*s",
                    r"(\d+(?:[.,]\d+)?)\s*l\s*/\s*s\s*(?:d[ée]bit\s*de\s*fuite)?",
                ]
                for pattern in flow_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            q = float(match.group(1).replace(",", "."))
                            project_info.discharge_flow_l_s = q
                            break
                        except ValueError:
                            continue
        
        return project_info
    
    def analyze_documents(
        self, 
        files: List[Tuple[str, str]]
    ) -> AnalysisReport:
        """
        Analyse une liste de documents et génère un rapport.
        
        Args:
            files: Liste de tuples (nom_fichier, contenu_texte)
            
        Returns:
            Rapport d'analyse complet
        """
        documents: List[Document] = []
        found_types: set = set()
        
        # Analyser chaque document
        for filename, content in files:
            doc_type, confidence = self.identify_document_type(filename, content)
            
            # Déterminer le statut
            if doc_type != DocumentType.AUTRE:
                status = DocumentStatus.CONFORME
                found_types.add(doc_type)
            else:
                status = DocumentStatus.CONFORME  # Document non obligatoire mais présent
            
            doc = Document(
                filename=filename,
                document_type=doc_type,
                status=status,
                confidence=confidence,
                extracted_text=content[:1000] if content else None,  # Extrait court (UI)
                full_text=content if content else None,  # Texte complet (extraction interne)
                issues=[]
            )
            
            documents.append(doc)
        
        # Identifier les documents manquants en fonction du type de dossier
        required_list = self.REQUIRED_DOCUMENTS_BY_CASE.get(self.case_type, self.REQUIRED_DOCUMENTS_BY_CASE["PC"])
        missing_documents = []
        for required in required_list:
            if required not in found_types:
                missing_documents.append(required.value)
        
        # Séparer les documents conformes et non conformes
        conformes = [d for d in documents if d.status == DocumentStatus.CONFORME]
        non_conformes = [d for d in documents if d.status == DocumentStatus.NON_CONFORME]
        
        # Extraire les infos du projet
        project_info = self.extract_project_info(documents)

        # Évaluer les règles de conformité (niveau dossier)
        compliance_engine = ComplianceEngine()
        compliance_issues = compliance_engine.evaluate(
            project_info=project_info,
            documents=documents,
            detected_types=list(found_types),
        )
        
        # Calculer le score de conformité
        total_required = len(required_list)
        found_required = len([d for d in documents if d.document_type in required_list])
        conformity_score = (found_required / total_required) * 100 if total_required > 0 else 0
        
        return AnalysisReport(
            project_info=project_info,
            documents_conformes=conformes,
            documents_non_conformes=non_conformes,
            documents_manquants=missing_documents,
            total_documents=len(documents),
            conformity_score=round(conformity_score, 1),
            compliance_issues=compliance_issues,
        )

