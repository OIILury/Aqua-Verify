"""
Service d'analyse rule-based des documents
Système fait maison sans LLM pré-entraîné
"""
import re
from typing import List, Dict, Optional, Tuple
from ..models.document import (
    Document, DocumentType, DocumentStatus, 
    AnalysisReport, ProjectInfo
)


class DocumentAnalyzer:
    """
    Analyseur de documents basé sur des règles (rule-based).
    Identifie les types de documents et vérifie leur conformité.
    """
    
    # Documents obligatoires pour un permis de construire
    REQUIRED_DOCUMENTS = [
        DocumentType.PC1,
        DocumentType.PC2,
        DocumentType.PC3,
        DocumentType.PC4,
        DocumentType.PC5,
        DocumentType.PC6,
        DocumentType.PC7,
        DocumentType.PC8,
        DocumentType.CERFA,
    ]
    
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
    }
    
    def __init__(self):
        """Initialise l'analyseur"""
        self.analyzed_documents: List[Document] = []
        self.project_info = ProjectInfo()
    
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
        
        for doc_type, rules in self.IDENTIFICATION_RULES.items():
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
            if doc.extracted_text:
                text = doc.extracted_text.lower()
                
                # Chercher la surface
                surface_patterns = [
                    r"surface\s*(?:de\s*plancher|totale)?\s*[:\s]*(\d+(?:[.,]\d+)?)\s*m",
                    r"(\d+(?:[.,]\d+)?)\s*m[²2]\s*(?:de\s*)?(?:surface|plancher)",
                    r"surface\s*[:\s]*(\d+(?:[.,]\d+)?)",
                ]
                
                for pattern in surface_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            surface = float(match.group(1).replace(",", "."))
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
                extracted_text=content[:1000] if content else None,  # Limiter la taille
                issues=[]
            )
            
            documents.append(doc)
        
        # Identifier les documents manquants
        missing_documents = []
        for required in self.REQUIRED_DOCUMENTS:
            if required not in found_types:
                missing_documents.append(required.value)
        
        # Séparer les documents conformes et non conformes
        conformes = [d for d in documents if d.status == DocumentStatus.CONFORME]
        non_conformes = [d for d in documents if d.status == DocumentStatus.NON_CONFORME]
        
        # Extraire les infos du projet
        project_info = self.extract_project_info(documents)
        
        # Calculer le score de conformité
        total_required = len(self.REQUIRED_DOCUMENTS)
        found_required = len([d for d in documents if d.document_type in self.REQUIRED_DOCUMENTS])
        conformity_score = (found_required / total_required) * 100 if total_required > 0 else 0
        
        return AnalysisReport(
            project_info=project_info,
            documents_conformes=conformes,
            documents_non_conformes=non_conformes,
            documents_manquants=missing_documents,
            total_documents=len(documents),
            conformity_score=round(conformity_score, 1)
        )

