"""
Service de chatbot rule-based
Système de FAQ dynamique basé sur le rapport d'analyse
"""
import re
from typing import Optional, List
from ..models.document import AnalysisReport, DocumentType


class ChatbotService:
    """
    Chatbot rule-based pour répondre aux questions sur le rapport.
    Utilise un système de patterns et de réponses prédéfinies.
    """
    
    # Descriptions des types de documents
    DOCUMENT_DESCRIPTIONS = {
        DocumentType.PC1: "Plan de situation du terrain - permet de localiser le terrain dans la commune",
        DocumentType.PC2: "Plan de masse - représente l'implantation du projet sur le terrain",
        DocumentType.PC3: "Plan en coupe - montre le profil du terrain et de la construction",
        DocumentType.PC4: "Notice descriptive - décrit le terrain et présente le projet",
        DocumentType.PC5: "Plan des façades et toitures - représente l'aspect extérieur du bâtiment",
        DocumentType.PC6: "Document graphique d'insertion - montre l'intégration du projet dans son environnement",
        DocumentType.PC7: "Photographie environnement proche - vue rapprochée du terrain et ses abords",
        DocumentType.PC8: "Photographie paysage lointain - vue éloignée situant le terrain dans le paysage",
        DocumentType.PA1: "PA1 - Plan de situation du terrain pour un permis d'aménager",
        DocumentType.PA2: "PA2 - Notice décrivant le terrain et le projet d'aménagement prévu",
        DocumentType.PA3: "PA3 - Plan de l'état actuel du terrain à aménager et de ses abords",
        DocumentType.PA4: "PA4 - Plan de composition d'ensemble du projet coté dans les trois dimensions",
        DocumentType.CERFA: "Formulaire CERFA - formulaire officiel de demande de permis de construire",
        DocumentType.AVIS_EP: "Avis Eaux Pluviales - document relatif à la gestion des eaux pluviales",
        DocumentType.AVIS_DEA: "Avis DEA - avis de la Direction de l'Eau et de l'Assainissement",
    }
    
    # Patterns de questions et leurs handlers
    QUESTION_PATTERNS = [
        # Questions sur les documents manquants
        (r"(?:quels?|quel)\s*(?:sont|est)?\s*(?:les?)?\s*documents?\s*manquants?", "get_missing_docs"),
        (r"(?:il\s*)?manque\s*(?:quoi|quelque chose)", "get_missing_docs"),
        (r"qu'?est.ce\s*(?:qui|qu'?il)\s*manque", "get_missing_docs"),
        (r"documents?\s*(?:à\s*)?fournir", "get_missing_docs"),
        
        # Questions sur la conformité
        (r"(?:suis.je|est.ce que je suis|je suis)\s*(?:en\s*)?(?:règle|conforme)", "get_conformity_status"),
        (r"(?:mon\s*)?dossier\s*(?:est.il)?\s*(?:complet|conforme|valide)", "get_conformity_status"),
        (r"(?:quel\s*est\s*)?(?:le\s*)?(?:score|taux|pourcentage)\s*(?:de\s*)?conformité", "get_conformity_status"),

        # Questions sur les non-conformités / corrections
        (r"(?:qu'?est.ce\s*qui)\s*(?:n'?est\s*)?pas\s*conforme", "get_compliance_issues"),
        (r"(?:quels?|quel)\s*(?:sont|est)?\s*(?:les?)?\s*(?:problèmes|erreurs|non.conformit[ée]s)", "get_compliance_issues"),
        (r"(?:que\s*)?dois.je\s*(?:corriger|modifier|faire)", "get_compliance_issues"),
        
        # Questions sur les documents présents
        (r"(?:quels?|quel)\s*(?:sont|est)?\s*(?:les?)?\s*documents?\s*(?:présents?|fournis?|ok)", "get_present_docs"),
        (r"documents?\s*(?:que\s*)?j'?ai\s*(?:fourni|déposé)", "get_present_docs"),
        
        # Questions sur un document spécifique
        (r"(?:qu'?est.ce\s*que?|c'?est\s*quoi)\s*(?:le\s*|un\s*)?(pc\d|cerfa)", "explain_document"),
        (r"(pc\d|cerfa)\s*(?:c'?est\s*quoi|qu'?est.ce)", "explain_document"),
        (r"(?:à\s*quoi\s*sert|pourquoi)\s*(?:le\s*)?(pc\d|cerfa)", "explain_document"),
        
        # Questions sur le projet
        (r"(?:quelle\s*est\s*)?(?:la\s*)?surface", "get_project_info"),
        (r"(?:quel\s*)?type\s*(?:de\s*)?projet", "get_project_info"),
        (r"(?:infos?|informations?)\s*(?:du\s*|sur\s*le\s*)?projet", "get_project_info"),
        
        # Salutations
        (r"^(?:bonjour|salut|hello|coucou|hey)", "greet"),
        (r"^(?:merci|thanks)", "thank"),
        (r"^(?:au revoir|bye|à bientôt)", "goodbye"),
        
        # Aide
        (r"(?:aide|help|comment|que\s*peux.tu)", "help"),
    ]
    
    def __init__(self):
        """Initialise le chatbot"""
        self.report: Optional[AnalysisReport] = None
    
    def set_report(self, report: AnalysisReport):
        """Définit le rapport d'analyse pour le contexte"""
        self.report = report
    
    def get_response(self, message: str, report: Optional[AnalysisReport] = None) -> str:
        """
        Génère une réponse à un message utilisateur.
        
        Args:
            message: Message de l'utilisateur
            report: Rapport d'analyse (optionnel)
            
        Returns:
            Réponse du chatbot
        """
        if report:
            self.report = report
        
        message_lower = message.lower().strip()
        
        # Chercher un pattern correspondant
        for pattern, handler_name in self.QUESTION_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                handler = getattr(self, f"_handle_{handler_name}", None)
                if handler:
                    return handler(match)
        
        # Réponse par défaut
        return self._handle_unknown()
    
    def _handle_get_missing_docs(self, match) -> str:
        """Répond sur les documents manquants"""
        if not self.report:
            return "Je n'ai pas encore de rapport d'analyse. Veuillez d'abord déposer vos documents."
        
        if not self.report.documents_manquants:
            return "✅ Bonne nouvelle ! Tous les documents obligatoires sont présents dans votre dossier."
        
        missing_list = []
        for doc_code in self.report.documents_manquants:
            try:
                doc_type = DocumentType(doc_code)
                desc = self.DOCUMENT_DESCRIPTIONS.get(doc_type, doc_code)
                missing_list.append(f"• **{doc_code}** : {desc}")
            except ValueError:
                missing_list.append(f"• **{doc_code}**")
        
        response = f"⚠️ Il manque **{len(self.report.documents_manquants)} document(s)** obligatoire(s) :\n\n"
        response += "\n".join(missing_list)
        return response
    
    def _handle_get_conformity_status(self, match) -> str:
        """Répond sur le statut de conformité"""
        if not self.report:
            return "Je n'ai pas encore de rapport d'analyse. Veuillez d'abord déposer vos documents."
        
        score = self.report.conformity_score
        
        if score >= 100:
            status = "✅ **Votre dossier est complet !**"
            advice = "Tous les documents obligatoires sont présents."
        elif score >= 75:
            status = f"⚠️ **Votre dossier est presque complet** ({score}%)"
            advice = "Il manque quelques documents pour être en règle."
        elif score >= 50:
            status = f"🟠 **Votre dossier est incomplet** ({score}%)"
            advice = "Plusieurs documents obligatoires sont manquants."
        else:
            status = f"❌ **Votre dossier est très incomplet** ({score}%)"
            advice = "De nombreux documents obligatoires sont manquants."
        
        response = f"{status}\n\n{advice}\n\n"
        response += f"• Documents présents : {len(self.report.documents_conformes)}\n"
        response += f"• Documents manquants : {len(self.report.documents_manquants)}"
        
        return response
    
    def _handle_get_present_docs(self, match) -> str:
        """Liste les documents présents"""
        if not self.report:
            return "Je n'ai pas encore de rapport d'analyse. Veuillez d'abord déposer vos documents."
        
        if not self.report.documents_conformes:
            return "Aucun document n'a été détecté dans votre dossier."
        
        docs_list = []
        for doc in self.report.documents_conformes:
            type_str = doc.document_type.value
            if doc.document_type != DocumentType.AUTRE:
                docs_list.append(f"• ✅ **{type_str}** : {doc.filename}")
            else:
                docs_list.append(f"• 📄 **Autre** : {doc.filename}")
        
        response = f"📋 **{len(self.report.documents_conformes)} document(s) détecté(s)** :\n\n"
        response += "\n".join(docs_list)
        return response
    
    def _handle_explain_document(self, match) -> str:
        """Explique ce qu'est un type de document"""
        doc_code = match.group(1).upper()
        
        try:
            doc_type = DocumentType(doc_code)
            desc = self.DOCUMENT_DESCRIPTIONS.get(doc_type)
            if desc:
                return f"📄 **{doc_code}** : {desc}"
        except ValueError:
            pass
        
        return f"Je ne connais pas le document '{doc_code}'. Les documents obligatoires sont PC1 à PC8 et le CERFA."
    
    def _handle_get_project_info(self, match) -> str:
        """Donne les informations du projet"""
        if not self.report or not self.report.project_info:
            return "Je n'ai pas pu extraire les informations du projet. Vérifiez que le CERFA est bien présent."
        
        info = self.report.project_info
        response_parts = ["📊 **Informations du projet** :\n"]
        
        if info.surface_m2:
            project_type = "petit projet (< 240 m²)" if info.is_small_project else "gros projet (≥ 240 m²)"
            response_parts.append(f"• Surface : {info.surface_m2} m² ({project_type})")
        
        if info.address:
            response_parts.append(f"• Adresse : {info.address}")
        
        if info.reference:
            response_parts.append(f"• Référence : {info.reference}")
        
        if len(response_parts) == 1:
            return "Aucune information détaillée n'a pu être extraite des documents."
        
        return "\n".join(response_parts)

    def _handle_get_compliance_issues(self, match) -> str:
        """Liste les non-conformités / points à corriger (niveau dossier)"""
        if not self.report:
            return "Je n'ai pas encore de rapport d'analyse. Veuillez d'abord déposer vos documents."

        issues = getattr(self.report, "compliance_issues", None) or []
        if not issues:
            return "✅ Je n'ai détecté aucun point réglementaire bloquant (au-delà des documents manquants)."

        lines = []
        for issue in issues:
            lines.append(f"• **{issue.title}** : {issue.message}")
        return "⚠️ Voici les points à corriger / compléter :\n\n" + "\n".join(lines)
    
    def _handle_greet(self, match) -> str:
        """Salutation"""
        return "👋 Bonjour ! Je suis l'assistant Aqua Verify. Comment puis-je vous aider avec votre dossier ?"
    
    def _handle_thank(self, match) -> str:
        """Remerciement"""
        return "De rien ! N'hésitez pas si vous avez d'autres questions sur votre dossier. 😊"
    
    def _handle_goodbye(self, match) -> str:
        """Au revoir"""
        return "Au revoir ! Bonne continuation avec votre projet. 👋"
    
    def _handle_help(self, match) -> str:
        """Aide"""
        return """🤖 **Je peux vous aider avec les questions suivantes** :

• **Documents manquants** : "Quels documents manquent ?"
• **Conformité** : "Est-ce que mon dossier est complet ?"
• **Documents présents** : "Quels documents ai-je fournis ?"
• **Explication** : "C'est quoi un PC2 ?"
• **Infos projet** : "Quelle est la surface du projet ?"

Posez-moi vos questions en français ! 🇫🇷"""
    
    def _handle_unknown(self) -> str:
        """Réponse par défaut"""
        if self.report:
            return """Je n'ai pas bien compris votre question. 🤔

Vous pouvez me demander :
• "Quels documents manquent ?"
• "Mon dossier est-il complet ?"
• "C'est quoi un PC2 ?"

Tapez "aide" pour voir toutes les possibilités."""
        else:
            return """Je n'ai pas encore de rapport d'analyse.

👉 Commencez par déposer vos documents dans la zone de dépôt, puis je pourrai répondre à vos questions sur votre dossier."""

