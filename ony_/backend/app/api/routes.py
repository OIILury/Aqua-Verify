"""
Routes API pour Aqua Verify
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from ..models.document import AnalysisReport, ChatRequest, ChatMessage
from ..services.extractor import TextExtractor
from ..services.analyzer import DocumentAnalyzer
from ..services.chatbot import ChatbotService


router = APIRouter()

# Instance du chatbot (stateful pour garder le contexte)
chatbot = ChatbotService()


@router.post("/analyze", response_model=AnalysisReport)
async def analyze_documents(files: List[UploadFile] = File(...)):
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
    analyzer = DocumentAnalyzer()
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
    
    # Générer la réponse
    response = chatbot.get_response(request.message)
    
    return ChatMessage(role="assistant", content=response)


@router.get("/health")
async def health_check():
    """Vérifie que l'API est fonctionnelle"""
    return {"status": "ok", "service": "Aqua Verify API"}

