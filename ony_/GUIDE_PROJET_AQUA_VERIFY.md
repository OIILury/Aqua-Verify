## 🧭 Guide de développement Aqua Verify (version “pro”)

Ce fichier te sert de **roadmap technique** pour faire évoluer Aqua Verify vers une version “pro”.  
Il est organisé par thèmes, avec pour chaque fois :
- **où** regarder dans le code,
- **quoi** modifier,
- **pistes d’amélioration** et **pièges à éviter**,
- quelques **commandes utiles**.

---

## 1. Lancer le projet en local

- **Backend (FastAPI + OCR)**  
  Dossier : `ony_/backend`

```powershell
cd ony_/backend
py -3.11 -m venv venv          # si pas déjà fait
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

- **Frontend (React + Vite)**  
  Dossier : `ony_/frontend`

```powershell
cd ony_/frontend
npm install
npm run dev
```

Le frontend proxy les appels vers `http://127.0.0.1:8000` (configuré dans `vite.config.ts`).

**Pièges :**
- Toujours utiliser le **venv Python 3.11** pour le backend.
- Vérifier que Tesseract est installé (`C:\Program Files\Tesseract-OCR\tesseract.exe`).

---

## 2. Améliorer la détection des pièces (PC1–PC8, CERFA, Avis, etc.)

### Où regarder
- Backend : `app/services/analyzer.py`
  - Constante `IDENTIFICATION_RULES`
  - Méthode `identify_document_type`
- Modèle : `app/models/document.py` (`DocumentType`)

### Ce qu’il faut faire
- **Ajouter/enrichir des mots-clés** pour chaque type de document :
  - Ex. pour `PC4` (Notice) : ajouter des variantes dans `filename` et `content`  
    (`"notice explicative"`, `"notice architecturale"`, `"notice PC4"`, etc.).
- **Booster l’importance du nom de fichier** quand il contient explicitement `pc4`, `pc3`, etc.
  - Piste : dans `identify_document_type`, si `filename_lower` contient `pc4`, ajouter un bonus de score.

### Pistes d’amélioration
- Utiliser des **patterns de cartouche** :
  - Dans les textes OCRisés, repérer des lignes type `PC4 - NOTICE` ou `Pièce PC4`.
  - Ajouter des mots-clés `content` ciblant ces formes.
- Gérer les abréviations et fautes classiques (`facades` vs `façades`, `retention` vs `rétention`).

### Erreurs à éviter
- Ne pas mettre des mots-clés **trop génériques** (ex. “plan”, “photo”) qui feraient matcher trop de documents.
- Ne pas dépasser un score de 1.0 (penser à la normalisation déjà en place).

---

## 3. Enrichir l’extraction d’infos projet (ProjectInfo)

### Où regarder
- Backend : `app/services/analyzer.py`
  - Méthode `extract_project_info`
- Modèles : `app/models/document.py`
  - `ProjectInfo` (surface, adresse, référence, … + champs “eaux pluviales”)

### Ce qu’il faut faire
- Ajouter des **regex** pour extraire :
  - **Surfaces imperméabilisées / surfaces totales** (m²),
  - **Volumes de rétention** (m³),
  - **Débits de fuite** (L/s),
  - Indices de **présence d’infiltration/rétention**.

### Pistes d’amélioration
- T’inspirer des patterns déjà présents pour la surface :
  - Copier la logique et adapter les expressions à tes formulations réelles.
- Tester d’abord sur les **documents CERFA / notices** de l’exemple `Exemple/117 ...`.

### Erreurs à éviter
- Éviter les regex trop “rigides” → privilégier plusieurs patterns plus souples.
- Toujours convertir les nombres avec `replace(",", ".")` avant `float()`.

---

## 4. Moteur de règles de conformité (ComplianceEngine)

### Où regarder
- Backend :
  - `app/services/compliance.py` : logique du moteur
  - `app/data/rules.yml` : configuration des règles
- Modèles :
  - `app/models/document.py` : `ComplianceIssue`, `AnalysisReport.compliance_issues`

### Ce qu’il faut faire
- **Configurer les profils** dans `rules.yml` :
  - `small` (<240 m²) et `big` (≥240 m²).
  - Pour chaque profil :
    - `required_fields` : champs de `ProjectInfo` obligatoires (ex. `impermeabilized_area_m2`, `retention_volume_m3`, `discharge_flow_l_s`).
    - `required_documents` : types de documents obligatoires en plus des PC1–PC8.
- Adapter `ComplianceEngine.evaluate()` si tu ajoutes de nouvelles règles (seuils, formules, etc.).

### Pistes d’amélioration
- Ajouter des règles du style :
  - **Si** `project_info.is_small_project` est `False` (≥240 m²) **ET** pas de `AVIS_EP` → issue de type "error".
  - **Si** surface imperméabilisée > X **ET** pas de `retention_volume_m3` → issue de type "warning".
- Ajouter un champ `action` dans `ComplianceIssue` pour proposer une correction concrète (ex. “Fournir PC4”, “Mentionner le volume de bassin dans la notice”).

### Erreurs à éviter
- Ne pas coder les règles en “dur” dans beaucoup d’endroits : tout centraliser dans `ComplianceEngine` + `rules.yml`.
- Garder les `code` d’issue **stables** (utile si tu veux mapper vers de l’affichage spécifique plus tard).

---

## 5. UI du rapport & Explication par le chatbot

### Rapport (frontend)
- Fichiers :
  - `frontend/src/components/Report.tsx`
  - `frontend/src/types/index.ts`

### Ce qu’il faut faire
- **Types** : si tu ajoutes des champs / issues, les déclarer dans `types/index.ts`.
- **Affichage** :
  - Section “Infos projet” : afficher les nouveaux champs utiles (volume, débit, etc.) si présents.
  - Section “Non-conformités / points à corriger” : personnaliser le rendu des `ComplianceIssue` (icônes, couleurs selon `severity`, texte d’action).

### Chatbot (backend + frontend)
- Backend :
  - `app/services/chatbot.py`
- Frontend :
  - `frontend/src/components/Chatbot.tsx`

### Ce qu’il faut faire
- Ajouter de nouveaux **patterns de questions** dans `QUESTION_PATTERNS` pour :
  - “Que dois-je corriger ?”
  - “Explique-moi cette non-conformité…”
- Dans les handlers (`_handle_get_compliance_issues`, etc.), formater la réponse à partir de `self.report.compliance_issues`.

### Erreurs à éviter
- Ne pas rendre le chatbot “juge” : les décisions doivent venir du moteur de règles, le chatbot ne fait que **les expliquer**.
- Garder les réponses **courtes, claires, en français**, avec des listes à puces si besoin.

---

## 6. OCR & performance

### Où regarder
- Backend :
  - `app/services/extractor.py` (`TextExtractor`)

### Ce qu’il faut faire
- Optimiser l’OCR :
  - Ne lancer l’OCR que si `page.get_text()` ne retourne rien (ce qui est déjà le cas).
  - Éventuellement limiter le nombre de pages OCRisées (ex. pour des très gros PDF).
- (Optionnel) Ajouter du pré-traitement image (via OpenCV) pour améliorer la qualité OCR sur des scans très sombres ou inclinés.

### Erreurs à éviter
- Ne pas lancer l’OCR sur **toutes** les pages par défaut (trop lent).
- Surveiller les logs : si tu vois souvent `Erreur OCR Tesseract`, vérifier le binaire / la langue (`lang="fra+eng"`).

---

## 7. Commandes & debug utiles

- **Vérifier l’état du backend** :

```bash
GET http://127.0.0.1:8000/api/health
```

- **Logs FastAPI / Uvicorn** : regarder la console où tourne `python main.py`.
- **Tester l’analyse sans frontend** :
  - Utiliser `curl` ou un outil type Postman pour appeler `POST /api/analyze` avec des fichiers.

Exemple (PowerShell, très simplifié) :

```powershell
Invoke-WebRequest `
  -Uri http://127.0.0.1:8000/api/analyze `
  -Method POST `
  -InFile "Chemin\vers\ton\PDF.pdf" `
  -ContentType "multipart/form-data"
```

---

## 8. Stratégie globale pour aller vers un “pro” complet

1. **Fiabiliser la détection de pièces** (IDENTIFICATION_RULES + tests sur les exemples).
2. **Richir ProjectInfo** avec les vrais champs métier dont tu as besoin pour la réglementation.
3. **Modéliser les règles** dans `rules.yml` (cas <240 / ≥240, seuils, docs obligatoires).
4. **Soigner l’UX** du rapport (section “actions à faire”) et du chatbot (explications pédagogiques).
5. **Tester sur plusieurs vrais dossiers** et ajuster les regex / règles au fur et à mesure.

En suivant ce guide, tu peux itérer étape par étape sans te perdre dans le code, tout en gardant une architecture claire et évolutive. 🚀


