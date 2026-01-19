# 🌊 Aqua Verify

Application web de vérification de conformité des dossiers d'aménagement avec le zonage des eaux pluviales du Grand Chalon.

## 🚀 Démarrage rapide

### Prérequis

- **Python 3.10+** - [Télécharger](https://www.python.org/downloads/)
- **Node.js 18+** - [Télécharger](https://nodejs.org/)

### Installation

#### 1. Backend (Python/FastAPI)

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py
```

Le backend sera accessible sur `http://localhost:8000`

#### 2. Frontend (React/TypeScript)

```bash
# Dans un autre terminal, aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

## 📁 Structure du projet

```
aqua-verify/
├── backend/
│   ├── app/
│   │   ├── api/          # Routes API
│   │   ├── core/         # Configuration
│   │   ├── models/       # Modèles de données
│   │   └── services/     # Logique métier
│   ├── main.py           # Point d'entrée
│   └── requirements.txt  # Dépendances Python
├── frontend/
│   ├── src/
│   │   ├── components/   # Composants React
│   │   ├── services/     # API client
│   │   └── types/        # Types TypeScript
│   └── package.json      # Dépendances Node
└── README.md
```

## 🎯 Fonctionnalités

- **Upload de documents** : Glisser-déposer de fichiers PDF et Word
- **Analyse automatique** : Identification des documents PC1-PC8 et CERFA
- **Rapport de conformité** : Score et liste des documents présents/manquants
- **Chatbot** : Assistant pour répondre aux questions sur le dossier

## 📄 Documents vérifiés

| Code | Document |
|------|----------|
| PC1 | Plan de situation du terrain |
| PC2 | Plan de masse des constructions |
| PC3 | Plan en coupe du terrain |
| PC4 | Notice descriptive |
| PC5 | Plan des façades et toitures |
| PC6 | Document graphique d'insertion |
| PC7 | Photographie environnement proche |
| PC8 | Photographie paysage lointain |
| CERFA | Formulaire officiel |

## 🛠️ Technologies

- **Frontend** : React 18, TypeScript, Tailwind CSS, Vite
- **Backend** : Python, FastAPI, PyMuPDF
- **IA** : Système rule-based (sans LLM externe)

## 📝 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/analyze` | Analyse les documents uploadés |
| POST | `/api/chat` | Envoie un message au chatbot |
| GET | `/api/health` | Vérifie l'état de l'API |

## 📜 Licence

Projet développé pour le Grand Chalon - Décembre 2024
