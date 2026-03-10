# Assistant RAG pour Documents – Système Intelligent d’Analyse et de Recherche Contextuelle

Ce projet met en place un assistant intelligent spécialisé dans l’analyse et l’exploitation de documents, capable de répondre à des questions en s’appuyant sur des fichiers fournis par l’utilisateur (Word, PDF, textes réglementaires, rapports, procédures, etc.).
Il combine un modèle de langage Mistral avec une architecture Retrieval-Augmented Generation (RAG), une mémoire conversationnelle, un système de détection d’insatisfaction, et un module d’escalade vers un agent humain.
L’objectif est de transformer n’importe quel ensemble de documents en une base de connaissances consultable, accessible via une interface conversationnelle moderne.

## Fonctionnalités principales


- 🔍 **Recherche sémantique** avec FAISS pour trouver les documents pertinents
- 🧠 **Classification des requêtes** pour déterminer si une recherche RAG est nécessaire
- 🤖 **Génération de réponses** avec les modèles Mistral (Small ou Large)
- 📊 **Visualisation des feedbacks** avec graphiques et statistiques
- ⚙️ **Paramètres personnalisables** (modèle, nombre de documents, score minimum)
- 🧠 **Mémoire conversationnelle** conserve les derniers échanges pour comprendre les questions implicites 
- ⚠️ **Détection d’insatisfaction et gestion des escalades** Le système détecte automatiquement les messages négatifs ou frustrés.
- 🖥️ **Interface Streamlit moderne**


## Prérequis

- Python 3.10+ 
- Clé API Mistral (obtenue sur [console.mistral.ai](https://console.mistral.ai/))

## Installation

1. **Cloner le dépôt**

```bash
git clone <url-du-repo>
cd <nom-du-repo>
```

2. **Créer un environnement virtuel**

```bash
# Création de l'environnement virtuel
python -m venv venv

# Activation de l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configurer la clé API**

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```
MISTRAL_API_KEY=votre_clé_api_mistral
```

## Structure du projet

```
.
chatbot-support-rag/
│
├── MistralChat.py              # Interface principale Streamlit
├── pages/
│   └── 1_Feedback_Viewer.py    # Visualisation des interactions et feedbacks
│
├── utils/
│   ├── config.py               # Configuration générale
│   ├── vector_store.py         # Indexation FAISS et embeddings
│   ├── database.py             # ORM SQLAlchemy (interactions, feedback, tickets)
│   ├── memory.py               # Mémoire conversationnelle
│   ├── sentiment.py            # Détection d’insatisfaction
│   ├── tickets.py              # Gestion des tickets
│   └── query_classifier.py     # Détection RAG vs réponse directe
│
├── inputs/                     # Documents à indexer
├── vector_db/                  # Index FAISS + chunks
└── database/                   # Bases SQLite

```

## Utilisation

### 1. Ajouter des documents

Placez vos documents dans le dossier `inputs/`. Les formats supportés sont :
- PDF
- TXT
- DOCX
- CSV
- JSON

Vous pouvez organiser vos documents dans des sous-dossiers pour une meilleure organisation.

### 2. Indexer les documents

Exécutez le script d'indexation pour traiter les documents et créer l'index FAISS :

```bash
python indexer.py
```

Ce script va :
1. Charger les documents depuis le dossier `inputs/`
2. Découper les documents en chunks
3. Générer des embeddings avec Mistral
4. Créer un index FAISS pour la recherche sémantique
5. Sauvegarder l'index et les chunks dans le dossier `vector_db/`

### 3. Lancer l'application

```bash
streamlit run MistralChat.py
```

L'application sera accessible à l'adresse http://localhost:8501 dans votre navigateur.

## Fonctionnalités principales

### Classification des requêtes

L'application détermine automatiquement si une question nécessite une recherche RAG ou si une réponse directe du modèle Mistral est suffisante. Cela permet d'optimiser les performances et la pertinence des réponses. 
Elle Permet aussi une supervision humaine via un système de tickets et un tableau de feedback.

### Paramètres personnalisables

Dans la barre latérale, vous pouvez ajuster :
- Le modèle Mistral (Small ou Large)
- Le nombre de documents à récupérer (1-20)
- Le score minimum de similarité (0-100%)

### Feedback et analyse

L'application enregistre les interactions et les feedbacks des utilisateurs. Vous pouvez visualiser les statistiques dans la page "Feedback Viewer".

## Modules principaux

### `utils/vector_store.py`

Gère l'index vectoriel FAISS et la recherche sémantique :
- Chargement, nettoyage et découpage des documents en chunks exploitables
- Génération des embeddings à l’aide d’un modèle de type Sentence Transformers
- Construction et mise à jour de l’index FAISS pour la recherche vectorielle
- Recherche des passages les plus pertinents en fonction de la requête utilisateur
- Gestion du score de similarité et filtrage des résultats

### `utils/query_classifier.py`

Détermine si une requête nécessite une recherche RAG oun une réponse direct:
- Analyse linguistique et détection de mots-clés
- Classification légère basée sur le modèle Mistral
- Distinction entre questions générales (réponse directe) et questions documentaires (RAG)
- Amélioration de la précision et réduction des appels inutiles au RAG

### `utils/database.py`

Gère la base de données SQLite pour les interactions, feedbacks et tickets:
- Enregistrement des questions, réponses, sources et métadonnées
- Stockage des feedbacks utilisateurs (👍 / 👎 + commentaire)
- Suivi des interactions pour analyse et supervision
- Création et gestion des tickets d’escalade en cas d’insatisfaction
- Récupération des statistiques et historique des conversations

### `utils/memory.py`

Gère la mémoire conversationnelle de l’assistant:
- Stockage des derniers échanges pour maintenir le contexte
- Reconstruction du fil de conversation pour les questions implicites
- Gestion d’une fenêtre de contexte configurable
- Amélioration de la cohérence des réponses sur plusieurs tours

### `utils/tickets.py`

Gère la création et le suivi des tickets d’escalade :
- Génération d’un ticket lorsqu’un utilisateur demande de l’aide humaine
- Enregistrement en base de données (motif, message, timestamp)
- Intégration avec le système de frustration pour escalade automatique
- Suivi des demandes non résolues

### `MistralChat.py`

Fichier principal de l’application Streamlit :
- Interface de chat interactive avec l’utilisateur
- Gestion des paramètres (mode RAG, seuils, nombre de documents)
- Appels au modèle Mistral pour la génération de réponses
- Affichage des sources, du score de similarité et du contexte
- Intégration du feedback utilisateur (👍 / 👎)
- Connexion avec tous les modules internes (RAG, mémoire, sentiment, tickets)

### `pages/1_Feedback_Viewer.py`

Page Streamlit dédiée à l’analyse des interactions :
- Visualisation des questions, réponses et sources utilisées
- Affichage des feedbacks et commentaires utilisateurs
- Consultation des métadonnées (mode, score, temps)
- Outil de supervision pour améliorer la qualité du système RAG

## Personnalisation

Vous pouvez personnaliser l'application en modifiant les paramètres dans `utils/config.py` :
- Modèles Mistral utilisés
- Taille des chunks et chevauchement
- Nombre de documents par défaut
- Score de similatité


