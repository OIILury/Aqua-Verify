"""
Client Jan.ai pour Aqua Verify

Ce module fournit un client minimal pour appeler un modèle Jan.ai
exposé via une API compatible OpenAI (chat completions).

L'objectif est de pouvoir expliquer les résultats du moteur de règles
sans que Jan.ai ne prenne de décisions de conformité.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any

import httpx


JAN_API_BASE_URL = os.getenv("JAN_API_BASE_URL", "http://127.0.0.1:1337/v1")
JAN_API_KEY = os.getenv("JAN_API_KEY", "defichallenge")
JAN_MODEL_NAME = os.getenv("JAN_MODEL_NAME", "Qwen3-Zero-Coder-Reasoning-0_8B-NEO-EX-D_AU-IQ4_XS-imat")


class JanAIClient:
    """Client minimal pour appeler un modèle Jan.ai compatible OpenAI."""

    def __init__(self) -> None:
        self.base_url = JAN_API_BASE_URL.rstrip("/")
        self.api_key = JAN_API_KEY
        self.model = JAN_MODEL_NAME
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Envoie un échange de type chat au modèle Jan.ai et retourne le texte de réponse.

        Args:
            messages: liste de dicts {"role": "system"|"user"|"assistant", "content": "..."}
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }
        # Important : ne PAS commencer le chemin par "/" sinon on perd le préfixe /v1
        response = await self._client.post("chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        # Le format exact peut varier selon ta version de Jan.ai → à adapter si besoin
        return data["choices"][0]["message"]["content"]


