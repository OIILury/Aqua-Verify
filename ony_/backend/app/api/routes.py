"""
Routes API pour Aqua Verify
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List
from ..models.document import AnalysisReport, ChatRequest, ChatMessage
from ..services.extractor import TextExtractor
from ..services.analyzer import DocumentAnalyzer
from ..services.chatbot import ChatbotService
from ..services.jan_client import JanAIClient
from ..services.rag_service import RAGService


router = APIRouter()
logger = logging.getLogger("aqua_verify")

# Instance du chatbot (stateful pour garder le contexte)
chatbot = ChatbotService()
# Client IA Jan.ai (utilisé pour les réponses enrichies)
jan_client = JanAIClient()
rag_service = RAGService(jan_client=jan_client)


@router.post("/analyze", response_model=AnalysisReport)
async def analyze_documents(
    files: List[UploadFile] = File(...),
    case_type: str = Query("PC", description="Type de dossier: PC (permis de construire) ou PA (permis d'aménager)"),
):
    """
    Analyse une liste de documents uploadés.
    
    Args:
        files: Liste des fichiers uploadés
        
    Returns:
        Rapport d'analyse complet
    """
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")
    
    # Extraire le texte de chaque document
    extracted_files = []
    extractor = TextExtractor()
    
    for file in files:
        # Vérifier l'extension
        filename = file.filename or "unknown"
        if not any(filename.lower().endswith(ext) for ext in [".pdf", ".docx", ".doc"]):
            continue
        
        # Lire le contenu du fichier
        content = await file.read()
        
        # Extraire le texte
        text, success = extractor.extract(content, filename)
        
        extracted_files.append((filename, text))
    
    if not extracted_files:
        raise HTTPException(
            status_code=400, 
            detail="Aucun fichier valide trouvé (formats acceptés: PDF, DOCX)"
        )
    
    # Analyser les documents
    analyzer = DocumentAnalyzer(case_type=case_type)
    report = analyzer.analyze_documents(extracted_files)
    
    # Mettre à jour le contexte du chatbot
    chatbot.set_report(report)
    
    return report


@router.post("/chat", response_model=ChatMessage)
async def chat(request: ChatRequest):
    """
    Endpoint du chatbot pour répondre aux questions.
    
    Args:
        request: Message de l'utilisateur et optionnellement le rapport
        
    Returns:
        Réponse du chatbot
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message vide")
    
    # Mettre à jour le rapport si fourni
    if request.report:
        chatbot.set_report(request.report)

    # Essayer d'abord d'utiliser Jan.ai via RAGService (même sans retrieval pour l'instant),
    # avec fallback sur le chatbot rule-based.
    report = request.report or getattr(chatbot, "report", None)

    if report:
        try:
            ai_response = await rag_service.answer(report=report, user_message=request.message)
            return ChatMessage(role="assistant", content=ai_response)
        except Exception as e:
            # En cas d'erreur d'appel Jan.ai, on retombe sur le chatbot rule-based
            logger.exception("Échec appel Jan.ai (fallback chatbot rule-based): %s", e)

    # Fallback : chatbot rule-based actuel
    response = chatbot.get_response(request.message)
    return ChatMessage(role="assistant", content=response)


@router.get("/jan/ping")
async def jan_ping():
    """
    Vérifie rapidement que Jan.ai répond.

    Utile pour diagnostiquer si le chatbot utilise bien Jan.ai ou s'il est en fallback.
    """
    try:
        content = await jan_client.chat(
            [
                {"role": "system", "content": "Tu réponds uniquement 'pong'."},
                {"role": "user", "content": "ping"},
            ]
        )
        return {"ok": True, "response": content}
    except Exception as e:
        logger.exception("Jan.ai ping failed: %s", e)
        return {"ok": False, "error": str(e)}


@router.get("/health")
async def health_check():
    """Vérifie que l'API est fonctionnelle"""
    return {"status": "ok", "service": "Aqua Verify API"}

