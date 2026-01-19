# 📚 Explication complète du projet Aqua Verify

## 🤔 Pourquoi plusieurs dossiers (hxl, jqc, klq, ony, pej, poq, wtr) ?

Ces dossiers sont des **worktrees Git** créés automatiquement par Cursor (ton IDE). 

### Qu'est-ce qu'un worktree ?
Un worktree Git permet d'avoir plusieurs copies d'un même dépôt Git dans des dossiers différents. C'est utile pour :
- Tester différentes versions du code
- Travailler sur plusieurs branches en parallèle
- Garder des versions de sauvegarde

### Dans notre cas
- **`ony/`** = **Le vrai projet** ✅ (c'est celui-ci qu'on utilise !)
- `hxl/`, `jqc/`, `klq/`, `pej/`, `poq/`, `wtr/` = Dossiers temporaires/vides créés par Cursor

**👉 Tu peux ignorer tous les autres dossiers et te concentrer sur `ony/` !**

---

## 📁 Arborescence du projet (dans `ony/`)

```
ony/
├── backend/                    # 🐍 API Python (serveur)
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py       # 📡 Endpoints HTTP (analyse, chat)
│   │   ├── core/
│   │   │   └── config.py       # ⚙️ Configuration (ports, CORS, etc.)
│   │   ├── models/
│   │   │   └── document.py     # 📋 Modèles de données (Document, Report)
│   │   └── services/
│   │       ├── extractor.py    # 📄 Extraction texte PDF/Word
│   │       ├── analyzer.py    # 🔍 Analyse rule-based des documents
│   │       └── chatbot.py     # 💬 Chatbot FAQ
│   ├── main.py                 # 🚀 Point d'entrée (lance le serveur)
│   └── requirements.txt        # 📦 Dépendances Python
│
├── frontend/                   # ⚛️ Interface React (client)
│   ├── src/
│   │   ├── components/
│   │   │   ├── DropZone.tsx    # 📤 Zone de dépôt de fichiers
│   │   │   ├── Report.tsx      # 📊 Affichage du rapport
│   │   │   └── Chatbot.tsx     # 💬 Interface du chatbot
│   │   ├── services/
│   │   │   └── api.ts          # 🔌 Client API (appels HTTP)
│   │   ├── types/
│   │   │   └── index.ts        # 📝 Types TypeScript
│   │   ├── App.tsx             # 🎨 Composant principal
│   │   └── main.tsx            # 🚀 Point d'entrée React
│   ├── package.json            # 📦 Dépendances Node.js
│   └── vite.config.ts          # ⚡ Configuration Vite
│
└── README.md                   # 📖 Documentation
```

---

## 🏗️ Pourquoi cette structure ?

### Séparation Backend/Frontend
- **Backend** = Logique métier, traitement des données
- **Frontend** = Interface utilisateur, affichage

### Organisation modulaire (Backend)
```
app/
├── api/        → Routes HTTP (ce que le frontend appelle)
├── core/       → Configuration globale
├── models/     → Structures de données
└── services/  → Logique métier (extraction, analyse, chatbot)
```

**Avantages** :
- ✅ Code organisé et maintenable
- ✅ Facile de trouver où modifier quelque chose
- ✅ Réutilisable (services indépendants)

---

## 🔄 Comment fonctionne l'application ? (Flux complet)

### 1️⃣ **L'utilisateur ouvre l'application**

```
Frontend (React) → http://localhost:5173
```

L'utilisateur voit :
- Une zone de dépôt de fichiers
- Des instructions

---

### 2️⃣ **L'utilisateur dépose des documents**

```
Utilisateur glisse des fichiers PDF/Word
    ↓
DropZone.tsx (composant React)
    ↓
App.tsx appelle analyzeDocuments() (services/api.ts)
    ↓
Requête HTTP POST vers /api/analyze
```

**Code concerné** :
- `frontend/src/components/DropZone.tsx` → Interface drag & drop
- `frontend/src/services/api.ts` → Envoie les fichiers au backend

---

### 3️⃣ **Le backend reçoit les fichiers**

```
Backend reçoit les fichiers (routes.py)
    ↓
Pour chaque fichier :
    ├─ TextExtractor.extract() → Extrait le texte
    └─ DocumentAnalyzer.analyze_documents() → Identifie le type
    ↓
Génère un AnalysisReport
```

**Code concerné** :
- `backend/app/api/routes.py` → Endpoint `/api/analyze`
- `backend/app/services/extractor.py` → Lit PDF/Word
- `backend/app/services/analyzer.py` → Identifie PC1, PC2, etc.

---

### 4️⃣ **Analyse des documents (détaillée)**

#### A. Extraction du texte
```python
# extractor.py
PDF → PyMuPDF → Texte brut
Word → python-docx → Texte brut
```

#### B. Identification du type de document
```python
# analyzer.py
Pour chaque document :
    1. Cherche des mots-clés dans le nom de fichier
       Ex: "masse" → PC2
    2. Cherche des mots-clés dans le contenu
       Ex: "plan de masse" → PC2
    3. Calcule un score de confiance
    4. Détermine le type (PC1, PC2, CERFA, etc.)
```

**Exemple concret** :
- Fichier : `"117 Masse.pdf"`
- Contenu : `"Plan de masse des constructions..."`
- Résultat : **PC2** (score: 0.85)

#### C. Vérification de conformité
```python
# analyzer.py
Documents obligatoires = [PC1, PC2, PC3, PC4, PC5, PC6, PC7, PC8, CERFA]

Pour chaque document obligatoire :
    Si trouvé → ✅ Conforme
    Si manquant → ⚠️ Manquant

Score = (documents trouvés / documents obligatoires) × 100
```

---

### 5️⃣ **Retour du rapport au frontend**

```
Backend renvoie AnalysisReport (JSON)
    ↓
Frontend reçoit le rapport
    ↓
App.tsx met à jour l'état (setReport)
    ↓
Interface change : affiche le rapport
```

**Code concerné** :
- `frontend/src/App.tsx` → Gère l'état du rapport
- `frontend/src/components/Report.tsx` → Affiche le rapport

**Le rapport contient** :
- ✅ Documents conformes (présents)
- ❌ Documents non conformes
- ⚠️ Documents manquants
- 📊 Score de conformité (%)

---

### 6️⃣ **L'utilisateur pose une question au chatbot**

```
Utilisateur tape : "Quels documents manquent ?"
    ↓
Chatbot.tsx envoie la question
    ↓
POST /api/chat avec le message
    ↓
chatbot.py analyse la question
    ↓
Retourne une réponse
```

**Code concerné** :
- `frontend/src/components/Chatbot.tsx` → Interface chat
- `backend/app/services/chatbot.py` → Logique de réponse

---

### 7️⃣ **Le chatbot répond (système rule-based)**

```python
# chatbot.py
Le chatbot utilise des patterns (expressions régulières) :

Pattern : r"quels? documents? manquent?"
    ↓
Handler : _handle_get_missing_docs()
    ↓
Réponse : Liste des documents manquants depuis le rapport
```

**Exemples de questions supportées** :
- "Quels documents manquent ?" → Liste les manquants
- "Mon dossier est-il complet ?" → Donne le score
- "C'est quoi un PC2 ?" → Explique le document

---

## 🔍 Détails techniques

### Communication Frontend ↔ Backend

```
Frontend (port 5173)          Backend (port 8000)
     │                              │
     │  POST /api/analyze            │
     ├─────────────────────────────>│
     │  (fichiers PDF/Word)          │
     │                              │
     │                              │ Traitement...
     │                              │
     │  AnalysisReport (JSON)        │
     │<─────────────────────────────┤
     │                              │
```

### CORS (Cross-Origin Resource Sharing)

Le backend autorise le frontend à faire des requêtes :
```python
# config.py
CORS_ORIGINS = ["http://localhost:5173"]  # Frontend autorisé
```

---

## 🎯 Résumé du flux en 5 étapes

```
1. Upload
   Utilisateur → DropZone → Frontend envoie fichiers

2. Extraction
   Backend reçoit → Extrait texte PDF/Word

3. Analyse
   Identifie types de documents (PC1-PC8, CERFA)
   Vérifie conformité

4. Rapport
   Génère rapport → Envoie au frontend → Affiche

5. Chatbot
   Utilisateur pose question → Chatbot répond basé sur le rapport
```

---

## 🛠️ Technologies utilisées

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Frontend** | React + TypeScript | Interface utilisateur |
| **Frontend** | Tailwind CSS | Styles |
| **Frontend** | Vite | Build tool |
| **Backend** | FastAPI | Framework API Python |
| **Backend** | PyMuPDF | Extraction PDF |
| **Backend** | python-docx | Extraction Word |
| **IA** | Rule-based (fait maison) | Identification documents |

---

## 📝 Points clés à retenir

1. **Le dossier `ony/` contient le vrai projet** (ignore les autres)

2. **Backend = Traitement** (extraction, analyse, chatbot)

3. **Frontend = Affichage** (interface, upload, rapport)

4. **Pas de base de données** → Tout en mémoire (pas de persistance)

5. **Système rule-based** → Pas de LLM, juste des règles et patterns

6. **Deux serveurs** :
   - Frontend : `localhost:5173`
   - Backend : `localhost:8000`

---

## 🚀 Pour tester
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

1. **Lancer le backend** :
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

2. **Lancer le frontend** (nouveau terminal) :
```bash
cd frontend
npm install
npm run dev
```

3. **Ouvrir** : http://localhost:5173

---

## ❓ Questions fréquentes

**Q : Pourquoi séparer backend et frontend ?**
R : Pour pouvoir changer l'un sans toucher à l'autre. Aussi, on peut réutiliser le backend avec une autre interface (mobile, etc.).

**Q : Pourquoi autant de fichiers Python ?**
R : Pour organiser le code. Chaque fichier a un rôle précis (extraction, analyse, chatbot).

**Q : Comment le chatbot sait-il répondre ?**
R : Il utilise des patterns (expressions régulières) pour reconnaître les questions et répondre avec des templates basés sur le rapport.

**Q : Où sont stockées les données ?**
R : Nulle part ! Tout est en mémoire. Quand tu fermes l'app, tout est perdu (comme prévu dans les specs).

---

Voilà ! Tu as maintenant une vision complète du projet. 🎉

