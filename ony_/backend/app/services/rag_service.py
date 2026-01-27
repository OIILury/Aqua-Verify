"""
Squelette de service RAG pour Aqua Verify.

Objectif : utiliser Jan.ai pour expliquer les non-conformités détectées
par le moteur de règles, en s'appuyant à terme sur des extraits de la
réglementation (retrieval à implémenter).
"""

from __future__ import annotations

from typing import List, Dict

from .jan_client import JanAIClient
from ..models.document import AnalysisReport, ComplianceIssue


class RAGService:
    """
    Service RAG (squelette) :
    - prendra en charge plus tard le retrieval d'extraits de la réglementation
    - appelle Jan.ai pour produire une explication pédagogique du rapport
    """

    def __init__(self, jan_client: JanAIClient) -> None:
        self.jan_client = jan_client
        # TODO: brancher ici la base vectorielle / index réglementaire

    async def explain_issues(self, report: AnalysisReport) -> str:
        """
        Produit une explication globale des non-conformités à partir du rapport.

        Pour l'instant, cette méthode se contente de reformuler les issues
        et d'y ajouter un peu de contexte projet.
        """
        issues: List[ComplianceIssue] = getattr(report, "compliance_issues", []) or []

        # 1) Résumé très court des issues
        if issues:
            issues_summary: List[str] = []
            for issue in issues:
                linked_docs = ", ".join(issue.related_documents or [])
                suffix = f" (documents liés: {linked_docs})" if linked_docs else ""
                issues_summary.append(
                    f"- [{issue.severity}] {issue.title}: {issue.message}{suffix}"
                )
            issues_text = "\n".join(issues_summary)
        else:
            issues_text = "Aucune non-conformité majeure détectée par le moteur de règles."

        # 2) TODO: utiliser les codes d'issues pour aller chercher
        #    les extraits de règlement pertinents (retrieval)
        law_snippets = "Extraits de règlement à intégrer ici (retrieval à implémenter)."

        # 3) Construire les messages pour Jan.ai
        surface = report.project_info.surface_m2
        address = report.project_info.address

        user_content = (
            "Contexte du dossier:\n"
            f"- Surface du projet: {surface} m²\n"
            f"- Adresse: {address}\n\n"
            "Non-conformités détectées par le moteur de règles:\n"
            f"{issues_text}\n\n"
            "Extraits de règlement potentiellement liés:\n"
            f"{law_snippets}\n\n"
            "Explique de façon pédagogique ce qui ne va pas dans le dossier, "
            "en te basant uniquement sur ces informations. "
            "Donne des conseils concrets pour corriger le dossier et indiquer "
            "quels documents ou informations ajouter."
        )

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant spécialisé en réglementation des eaux pluviales "
                    "et en urbanisme. Tu expliques les résultats d'un moteur de règles "
                    "déterministe. Si une information n'est pas présente dans les "
                    "extraits de règlement fournis, tu dis que tu ne sais pas."
                ),
            },
            {"role": "user", "content": user_content},
        ]

        return await self.jan_client.chat(messages)

    async def answer(self, report: AnalysisReport, user_message: str) -> str:
        """
        Répond à une question utilisateur en s'appuyant sur le rapport et (plus tard) le retrieval RAG.

        Pour le moment, on injecte :
        - un résumé du dossier (score, manquants, infos projet)
        - les non-conformités (ComplianceIssue)
        - la question de l'utilisateur
        """
        issues: List[ComplianceIssue] = getattr(report, "compliance_issues", []) or []

        if issues:
            issues_text = "\n".join([f"- [{i.severity}] {i.title}: {i.message}" for i in issues])
        else:
            issues_text = "Aucune non-conformité majeure détectée par le moteur de règles."

        missing_docs = ", ".join(report.documents_manquants) if report.documents_manquants else "aucun"

        # TODO: retrieval réel depuis une base vectorielle
        law_snippets = "Extraits de règlement à intégrer ici (retrieval à implémenter)."

        user_content = (
            "Résumé du dossier:\n"
            f"- Score de conformité: {report.conformity_score}%\n"
            f"- Documents manquants: {missing_docs}\n"
            f"- Surface du projet: {report.project_info.surface_m2} m²\n"
            f"- Adresse: {report.project_info.address}\n\n"
            "Non-conformités détectées par le moteur de règles:\n"
            f"{issues_text}\n\n"
            "Extraits de règlement potentiellement liés:\n"
            f"{law_snippets}\n\n"
            "Question de l'utilisateur:\n"
            f"{user_message}\n\n"
            "Réponds en français, clairement. Si l'information n'est pas dans le contexte "
            "ou les extraits, dis que tu ne sais pas et propose ce qu'il faudrait fournir."
        )

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant spécialisé en réglementation des eaux pluviales et urbanisme. "
                    "Tu expliques un rapport issu d'un moteur de règles déterministe. "
                    "Tu ne dois pas inventer de nouvelles règles ni de références. "
                    "Si une information manque, dis-le explicitement."
                ),
            },
            {"role": "user", "content": user_content},
        ]

        return await self.jan_client.chat(messages)


