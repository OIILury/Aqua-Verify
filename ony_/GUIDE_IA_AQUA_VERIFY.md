## 🧠 Stratégie IA & législation pour Aqua Verify

Ce guide résume **la vision globale** pour l’IA dans Aqua Verify et donne un **démarrage concret** pour :

- connecter un modèle local via **Jan.ai**,
- structurer les **règles légales** dans le moteur de conformité,
- poser les bases d’un **pipeline RAG** (Retrieval-Augmented Generation),
- définir des **prompts** clairs et sûrs.

---

## 1. Rôles : qui fait quoi entre règles et IA ?

- **DocumentAnalyzer** (déjà en place)  
  - Identifie les types de documents (PC1–PC8, PA1–PA4, CERFA, AVIS_EP…).  
  - Extrait les infos projet (`ProjectInfo` : surface, adresse, volumes, débits, etc.).

- **ComplianceEngine + `rules.yml` = “la loi”**  
  - Traduit la réglementation en **règles explicites** et auditables.  
  - Compare `ProjectInfo` + types de documents détectés → produit des `ComplianceIssue` structurés.

- **Chatbot / IA = “le prof qui explique”**  
  - Ne décide pas ce qui est conforme.  
  - Explique : pourquoi une règle est en erreur, quels documents / infos manquent, quelles corrections faire.  
  - S’appuie sur :
    - le **rapport d’analyse** (`AnalysisReport`),  
    - les **issues** du `ComplianceEngine`,  
    - éventuellement des **extraits du règlement** via RAG.

> **Principe clé** : la conformité est décidée par du **code + YAML** (maîtrisé), l’IA ne fait que **commenter / expliquer**.

---

## 2. Structurer la législation dans `rules.yml`

Fichier : `backend/app/data/rules.yml`  
Moteur : `backend/app/services/compliance.py`

### 2.1. Profils de projet

Déjà en place : `base`, `small`, `big`.  
Évolution possible : ajouter la notion de **type de dossier** (PC / PA) et/ou de **zone**.

Exemple d’extension possible (schéma) :

```yaml
profiles:
  base:
    required_fields: []
    required_documents: []

  small:
    required_fields:
      - impermeabilized_area_m2
    required_documents: []

  big:
    required_fields:
      - impermeabilized_area_m2
      - retention_volume_m3
      - discharge_flow_l_s
    required_documents:
      - AVIS_EP
```

> Tu peux décliner selon ta réglementation réelle (seuils, zones, obligations AVIS_EP, etc.).

### 2.2. Types de règles à encoder

- **Présence d’informations** :  
  - champs obligatoires dans `ProjectInfo` (`surface_m2`, `impermeabilized_area_m2`, `retention_volume_m3`, `discharge_flow_l_s`…).  
  - Si un champ est `None` alors qu’il est dans `required_fields` → `ComplianceIssue` “Information manquante”.

- **Présence de documents** :  
  - `required_documents` contient des `DocumentType` (ex. `AVIS_EP`, `AVIS_DEA`).  
  - Si un type n’est pas dans les `detected_types` → `ComplianceIssue` “Document attendu manquant”.

- **Règles chiffrées (seuils)** :  
  - Encodées directement dans `ComplianceEngine.evaluate()` avec des `if` bien commentés, par ex. :
    - si `impermeabilized_area_m2 > 240` ET pas de `retention_volume_m3` → warning / error.  
    - si `surface_m2 > X` alors `AVIS_EP` obligatoire, etc.

> Recommandation : garder **tous les seuils** (240 m², débits, volumes) dans des constantes ou dans le YAML, pas “en dur” partout.

---

## 3. Extraire les règles à partir de la législation réelle

Tu n’auras pas de “dump JSON magique” de la loi. Le workflow réaliste :

1. **Repérer les articles clés** dans les documents officiels (PLUi, règlement EP, guides internes).  
2. Pour chaque article utile, noter dans un tableau (Excel / Notion / YAML) :
   - condition (ex. `surface_impermeabilisée > 240 m²`),  
   - exigence (doc obligatoire, volume minimum, débit max…),  
   - contexte (PC/PA, type de zone),  
   - référence (code, article, page).
3. Encoder ces règles dans :
   - `rules.yml` (présence de champs / docs),  
   - `ComplianceEngine.evaluate()` (seuils, formules).

Option bonus : utiliser un LLM (même offline) pour **proposer une première version** de ces règles à partir d’un PDF, mais tu restes le décideur final.

---

## 4. Stratégie IA avec Jan.ai (modèle local)

### 4.1. Pourquoi Jan.ai / modèle local ?

**Forces :**

- Confidentialité : données et dossiers restent chez toi.  
- Coût prévisible : pas de facturation à l’usage par un gros cloud.  
- Contrôle : tu choisis la version du modèle et peux la tester/versionner.

**Faiblesses / points de vigilance :**

- Besoin d’une machine correcte (CPU/GPU) pour des réponses fluides.  
- Qualité souvent un peu en dessous des gros modèles cloud (mais suffisant pour **expliquer** des règles déjà calculées).  
- Tu dois concevoir un RAG strict et des prompts bien cadrés pour limiter les hallucinations.

### 4.2. Rôles du modèle Jan.ai

- **Expliquer** les `ComplianceIssue` (non‑conformités) au citoyen / instructeur.  
- **Répondre aux questions** sur : “Pourquoi ce document est-il manquant ?”, “Que dois-je corriger ?”.  
- Éventuellement **aider à résumer** un avis ou une notice avec contexte réglementaire.

> Jan.ai **ne remplace pas** `ComplianceEngine`. Il s’appuie sur lui.

---

## 5. Connexion à l’API Jan.ai (backend Python)

On part du principe que ton serveur Jan.ai expose une API **compatible OpenAI** (c’est le cas de beaucoup de distributions Jan).  

### 5.1. Variables d’environnement

Dans ton `.env` (ou variables système) :

```bash
JAN_API_BASE_URL=http://localhost:8080/v1
JAN_API_KEY=ta_cle_api
JAN_MODEL_NAME=jan-1 # ou le nom du modèle que tu utilises
```

### 5.2. Client minimal (fichier suggéré)

Fichier suggéré : `backend/app/services/jan_client.py`

> Ce fichier n’est pas encore créé dans le projet, mais tu peux t’en inspirer pour l’implémentation réelle.

Esquisse de code :

```python
import os
from typing import List, Dict, Any
import httpx

JAN_API_BASE_URL = os.getenv("JAN_API_BASE_URL", "http://localhost:8080/v1")
JAN_API_KEY = os.getenv("JAN_API_KEY", "changeme")
JAN_MODEL_NAME = os.getenv("JAN_MODEL_NAME", "jan-1")


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

        messages: liste de dicts {"role": "system"|"user"|"assistant", "content": "..."}
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }
        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
```

> À adapter selon la doc précise de ton serveur Jan (nom de chemin, modèle, auth). L’idée générale reste la même.

---

## 6. Début de pipeline RAG

Objectif : **donner au modèle seulement des extraits pertinents de la réglementation** + le rapport d’analyse, pour qu’il explique sans inventer.

### 6.1. Étapes conceptuelles

1. **Collecte / nettoyage des textes de loi**  
   - Extraire les textes pertinents (règlement EP, PLUi, guides) sous forme texte.  
   - Les découper en **paragraphes / articles** (chunks) avec métadonnées :
     - `id`, `source` (nom du doc), `article`, `page`, `texte`.

2. **Indexation vectorielle** (à choisir plus tard)  
   - Utiliser une base vectorielle (Qdrant, Chroma, etc.) ou même une structure maison au début.  
   - Pour chaque chunk : calculer un embedding (tu pourras éventuellement utiliser aussi Jan.ai pour ça) et l’enregistrer.

3. **Retrieval**  
   - Pour chaque question utilisateur ou chaque `ComplianceIssue`, formuler une requête texte :  
     - ex. “obligation AVIS_EP pour surface imperméabilisée > 240 m²”.  
   - Récupérer les **3–5 extraits les plus pertinents** (cosine similarity).

4. **Génération (avec Jan.ai)**  
   - Construire un prompt avec :
     - contexte dossier : `ProjectInfo`, `ComplianceIssue`, type de permis, etc.  
     - extraits de loi : texte + référence.  
     - consignes strictes (voir plus bas).
   - Appeler `JanAIClient.chat()` avec ces messages.

### 6.2. Squelette de service RAG (pseudo-code)

Fichier suggéré : `backend/app/services/rag_service.py`

```python
from typing import List, Dict
from .jan_client import JanAIClient
from ..models.document import AnalysisReport, ComplianceIssue


class RAGService:
    """
    Service RAG (squelette) :
    - retrieval d'extraits de la réglementation
    - appel du modèle Jan.ai pour expliquer les non-conformités
    """

    def __init__(self, jan_client: JanAIClient) -> None:
        self.jan_client = jan_client
        # TODO: brancher ici ta base vectorielle / index réglementaire

    async def explain_issues(self, report: AnalysisReport) -> str:
        """
        Produit une explication globale des non-conformités à partir du rapport.
        """
        issues: List[ComplianceIssue] = getattr(report, "compliance_issues", []) or []

        # 1) Construire un résumé très court des issues
        issues_summary = []
        for issue in issues:
            issues_summary.append(
                f"- [{issue.severity}] {issue.title}: {issue.message} "
                f"(documents liés: {', '.join(issue.related_documents or [])})"
            )
        issues_text = "\n".join(issues_summary) if issues_summary else "Aucune non-conformité majeure détectée."

        # 2) TODO: utiliser les codes d'issues pour aller chercher
        #    les extraits de règlement pertinents (retrieval)
        law_snippets = "Extraits de règlement à intégrer ici (retrieval à implémenter)."

        # 3) Construire les messages pour Jan.ai
        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant spécialisé en réglementation des eaux pluviales et permis "
                    "d'urbanisme. Tu expliques les résultats d'un moteur de règles déterministe. "
                    "Si une information n'est pas présente dans les extraits de règlement fournis, "
                    "tu dis que tu ne sais pas."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Contexte du dossier:\n"
                    f"- Surface du projet: {report.project_info.surface_m2} m²\n"
                    f"- Adresse: {report.project_info.address}\n\n"
                    "Non-conformités détectées:\n"
                    f"{issues_text}\n\n"
                    "Extraits de règlement potentiellement liés:\n"
                    f"{law_snippets}\n\n"
                    "Explique de façon pédagogique ce qui ne va pas dans le dossier, "
                    "en te basant uniquement sur ces informations. "
                    "Donne des conseils concrets pour corriger le dossier."
                ),
            },
        ]

        return await self.jan_client.chat(messages)
```

> Ce squelette fonctionne déjà comme “IA qui reformule les issues”. Il faudra ensuite brancher **la vraie partie retrieval** (index des lois).

---

## 7. Bonnes pratiques de prompts (RAG “strict”)

- **Toujours rappeler le rôle** du modèle dans le `system` message :  
  - “Tu expliques les résultats, tu ne crées pas de nouvelles règles.”  
  - “Si l’info n’est pas dans les extraits, dis que tu ne sais pas.”

- **Limiter le contexte** aux extraits réellement pertinents (3–5).  
- **Demander des références explicites** (article, code, page) dans la réponse si disponibles.  
- **Encourager la prudence** : phrases du type “vérifier auprès du service urbanisme en cas de doute”.

Exemple de `system` message pour RAG :

> “Tu es un assistant juridique spécialisé en eaux pluviales pour les permis de construire et d’aménager.  
> Tu reçois : 1) des non‑conformités déjà calculées par un moteur de règles, 2) quelques extraits du règlement officiel.  
> Tu dois expliquer ces non‑conformités à un non‑expert, en te basant **uniquement** sur ces éléments.  
> Si une information n’est pas présente dans les extraits, tu dois répondre que tu ne sais pas ou que cela dépasse les informations fournies.”

---

## 8. Roadmap IA réaliste pour ton projet pro

1. **Stabiliser le cœur métier** (ce que tu as déjà bien avancé) :  
   - détection PC/PA, OCR, `ProjectInfo`, `ComplianceEngine` minimal.

2. **Encoder 2–3 vraies règles de ta réglementation** dans `rules.yml` + `ComplianceEngine`.  
3. **Brancher Jan.ai en mode “explication des issues”** (sans RAG au début).  
4. **Construire un petit index de 5–10 extraits de règlement** et implémenter un retrieval simple (même en mémoire) → première version de RAG.  
5. **Itérer** : ajouter des règles, des extraits, améliorer les prompts et l’UX du chatbot.

En suivant ce guide, tu auras une base **sérieuse et maîtrisée** pour ton mémoire / projet pro, avec un chemin clair pour aller vers une vraie IA réglementaire sans perdre le contrôle. 🚀


