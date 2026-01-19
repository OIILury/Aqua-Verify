# 🌊 Aqua Verify - Spécifications du Projet

## 📋 Contexte

### Commanditaire
**Le Grand Chalon** - Agglomération ayant adopté le 5 mars 2024 un zonage des eaux pluviales qui généralise la gestion locale des eaux pluviales par infiltration.

### Objectif
Développer une application web permettant de vérifier automatiquement la conformité des dossiers d'aménagement avec la réglementation du zonage des eaux pluviales du Grand Chalon.

### Problématique
Les prescriptions du zonage des eaux pluviales s'imposent à l'ensemble des aménageurs du Grand Chalon (adossé au PLUi). Il faut vérifier que les dossiers déposés contiennent tous les documents obligatoires.

---

## 🎯 Fonctionnalités

### Flux utilisateur
1. **Upload** : L'utilisateur dépose ses documents (PDF/Word, 5 à 30 fichiers)
2. **Extraction** : Extraction du texte des PDF (majoritairement générés numériquement)
3. **Analyse IA** : Identification et classification des documents (système rule-based)
4. **Rapport** : Génération d'un mini-rapport de conformité
5. **Chatbot** : Discussion pour expliquer les résultats (FAQ dynamique)

### Rapport de conformité
Le rapport doit indiquer :
- ✅ Documents conformes (présents)
- ❌ Documents non conformes
- ⚠️ Documents manquants

### Chatbot
- Niveau de technicité : **Basique**
- Rôle : Répondre aux questions sur le rapport et expliquer ce qui manque
- Langue : **Français uniquement**
- **Approche** : Système rule-based / FAQ dynamique (pas de LLM)

---

## 📄 Documents obligatoires (Permis de Construire)

| Code | Document | Référence légale |
|------|----------|------------------|
| PC1 | Plan de situation du terrain | Art. R. 431-7 a) du code de l'urbanisme |
| PC2 | Plan de masse des constructions | Art. R. 431-9 du code de l'urbanisme |
| PC3 | Plan en coupe du terrain et de la construction | Art. R. 431-10 b) du code de l'urbanisme |
| PC4 | Notice décrivant le terrain et présentant le projet | Art. R. 431-8 du code de l'urbanisme |
| PC5 | Plan des façades et des toitures | Art. R. 431-10 a) du code de l'urbanisme |
| PC6 | Document graphique d'insertion du projet | Art. R. 431-10 c) du code de l'urbanisme |
| PC7 | Photographie du terrain - environnement proche | Art. R. 431-10 d) du code de l'urbanisme |
| PC8 | Photographie du terrain - paysage lointain | Art. R. 431-10 d) du code de l'urbanisme |

### Autres documents possibles
- CERFA (formulaire officiel - contient la liste des pièces jointes)
- Avis EP (Eaux Pluviales)
- Avis DEA (Direction de l'Eau et de l'Assainissement)
- DPC
- Coupes bassin
- Situations
- Plans divers

### Stratégie d'identification des documents
1. **Analyse du nom de fichier** (mots-clés : "masse", "coupe", "façade", etc.)
2. **Extraction du texte** des PDF (générés numériquement)
3. **Croisement avec le CERFA** qui liste les pièces jointes déclarées
4. **Classification rule-based** basée sur le contenu (mots-clés, patterns)

---

## 📐 Deux cas de figure

> **Note** : Le type de projet (< ou ≥ 240m²) est déterminé automatiquement par l'analyse des documents (notamment le CERFA).

### Projet < 240 m²
- Formulaire : `Formulaire_petits-projets_juin_2024.pdf`
- Outil de calcul : `Outil-calcul-eaux-pluviales-240inf-septembre-2024.xlsx`
- Prescriptions : `Prescriptions-eaux-pluviales-Grand-Chalon-petit-projet-inf-240m²-mars-2024.pdf`

### Projet ≥ 240 m²
- Formulaire : `Formulaire_gros-projets_juin_2024.pdf`
- Outil de calcul : `Outil-calcul-eaux-pluviales-240sup-septembre-2024.xlsx`
- Prescriptions : `Prescriptions-eaux-pluviales-Grand-Chalon-gros-projet-sup-240m²-fevrier-2024.pdf`

---

## 👥 Utilisateurs

### Cible
- **Professionnels** (bureaux d'études, aménageurs, constructeurs)

### Gestion des utilisateurs
- ❌ Pas d'authentification
- ❌ Pas de persistance des données
- ❌ Pas de système de rôles
- Usage ponctuel : on dépose, on analyse, on obtient le résultat

---

## 🔧 Stack technique

### Frontend
- **Framework** : React avec TypeScript
- **UI** : Tailwind CSS
- **Upload** : react-dropzone

### Backend
- **Framework** : FastAPI (Python)
- **Extraction PDF** : PyMuPDF (fitz) - rapide et efficace pour les PDF texte
- **Extraction Word** : python-docx
- **IA** : Système rule-based custom (pas de LLM pré-entraîné)

### Hébergement
- **Local** (développement)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                    (React + TypeScript)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Upload    │  │   Rapport   │  │      Chatbot        │  │
│  │  Zone Drop  │  │  Conformité │  │   (FAQ dynamique)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                    (FastAPI - Python)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Extraction │  │  Analyse    │  │     Chatbot         │  │
│  │  PDF/Word   │  │  Rule-based │  │     Rule-based      │  │
│  │  (PyMuPDF)  │  │  (custom)   │  │     (FAQ)           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 Informations projet
- **Date de création** : Décembre 2024
- **Approche IA** : Rule-based (système fait maison, pas de LLM)

