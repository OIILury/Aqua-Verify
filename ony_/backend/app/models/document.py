"""
Modèles de données pour les documents
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class DocumentType(str, Enum):
    """Types de documents reconnus"""
    PC1 = "PC1"  # Plan de situation
    PC2 = "PC2"  # Plan de masse
    PC3 = "PC3"  # Plan en coupe
    PC4 = "PC4"  # Notice descriptive
    PC5 = "PC5"  # Plan des façades
    PC6 = "PC6"  # Document graphique d'insertion
    PC7 = "PC7"  # Photo environnement proche
    PC8 = "PC8"  # Photo paysage lointain
    CERFA = "CERFA"  # Formulaire CERFA
    AVIS_EP = "AVIS_EP"  # Avis Eaux Pluviales
    AVIS_DEA = "AVIS_DEA"  # Avis DEA
    DPC = "DPC"  # Document de présentation du projet
    COUPE_BASSIN = "COUPE_BASSIN"  # Coupe bassin
    AUTRE = "AUTRE"  # Document non identifié


class DocumentStatus(str, Enum):
    """Statut de conformité d'un document"""
    CONFORME = "conforme"
    NON_CONFORME = "non_conforme"
    MANQUANT = "manquant"


class Document(BaseModel):
    """Représentation d'un document analysé"""
    filename: str
    document_type: DocumentType
    status: DocumentStatus
    confidence: float  # Score de confiance de l'identification (0-1)
    extracted_text: Optional[str] = None
    issues: List[str] = []  # Problèmes détectés


class ProjectInfo(BaseModel):
    """Informations sur le projet extrait des documents"""
    surface_m2: Optional[float] = None
    is_small_project: Optional[bool] = None  # < 240 m²
    address: Optional[str] = None
    reference: Optional[str] = None

    # Infos utiles à la conformité "eaux pluviales" (à enrichir progressivement)
    impermeabilized_area_m2: Optional[float] = None  # surface imperméabilisée (m²)
    retention_volume_m3: Optional[float] = None  # volume de rétention/stockage (m³)
    discharge_flow_l_s: Optional[float] = None  # débit de fuite (L/s)
    infiltration: Optional[bool] = None  # infiltration mentionnée / prévue
    retention: Optional[bool] = None  # rétention/stockage mentionné / prévu


class ComplianceIssue(BaseModel):
    """Écart / non-conformité détectée par rapport aux règles (niveau dossier)"""
    code: str  # identifiant stable (ex: "MISSING_SURFACE")
    title: str
    severity: str = "warning"  # "info" | "warning" | "error"
    message: str
    evidence: Optional[str] = None  # extrait de preuve (texte court)
    related_documents: List[str] = []  # noms de fichiers ou types (ex: "CERFA", "PC2")


class AnalysisReport(BaseModel):
    """Rapport d'analyse complet"""
    project_info: ProjectInfo
    documents_conformes: List[Document]
    documents_non_conformes: List[Document]
    documents_manquants: List[str]
    total_documents: int
    conformity_score: float  # Pourcentage de conformité
    compliance_issues: List[ComplianceIssue] = []  # écarts réglementaires (au-delà de la complétude)


class ChatMessage(BaseModel):
    """Message du chatbot"""
    role: str  # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    """Requête au chatbot"""
    message: str
    report: Optional[AnalysisReport] = None

