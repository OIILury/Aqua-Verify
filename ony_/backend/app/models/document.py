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


class AnalysisReport(BaseModel):
    """Rapport d'analyse complet"""
    project_info: ProjectInfo
    documents_conformes: List[Document]
    documents_non_conformes: List[Document]
    documents_manquants: List[str]
    total_documents: int
    conformity_score: float  # Pourcentage de conformité


class ChatMessage(BaseModel):
    """Message du chatbot"""
    role: str  # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    """Requête au chatbot"""
    message: str
    report: Optional[AnalysisReport] = None

