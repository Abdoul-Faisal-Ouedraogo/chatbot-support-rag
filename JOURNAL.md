### `📅 02/03/2026 — Initialisation du projet`
- Création de la structure du projet chatbot-support-rag.
- Mise en place de l’environnement virtuel Python.
- Installation des dépendances principales : Streamlit, SQLAlchemy, FAISS, Sentence Transformers, Mistral API.
- Définition de l’objectif : construire un assistant RAG basé sur des documents PDF/Word.
- Création des dossiers initiaux : utils/, inputs/, vector_db/, database/.

### `📅 03/03/2026 — Mise en place du pipeline RAG`
- Développement du module vector_store.py.
- Implémentation du découpage des documents en chunks.
- Génération des embeddings avec Sentence Transformers.
- Création de l’index FAISS et tests de recherche vectorielle.
- Vérification du fonctionnement sur un premier PDF.

### ` — Classification des requêtes`
- Création du module query_classifier.py.
- Mise en place d’une logique simple pour distinguer :
-   questions nécessitant le RAG,
-   questions générales traitées par Mistral.
- Tests sur plusieurs exemples pour valider la classification.

### `— Base de données et ORM`
- Développement du module database.py avec SQLAlchemy.
- Création des tables :
-  interactions,
-  feedbacks,
-  tickets.
- Ajout des fonctions CRUD : enregistrement, récupération, mise à jour.
-   Tests de persistance avec SQLite.

### `📅 09/03/2026 — Mémoire conversationnelle`
Création du module memory.py.
Mise en place d’une fenêtre de contexte (5 derniers messages).
Intégration avec le pipeline de génération.
Tests sur des conversations multi‑tours.

-  Détection d’insatisfaction
Développement du module sentiment.py.
Mise en place d’un score de frustration.
Déclenchement d’alertes en cas de messages négatifs répétés.
Tests sur différents scénarios d’utilisateur frustré.

- Gestion des tickets
Création du module tickets.py.
Intégration avec le sentiment :
escalade automatique si frustration élevée,
création manuelle si l’utilisateur demande un agent humain.
    Enregistrement des tickets en base.

### `📅 10/03/2026 — Interface Streamlit`

    Développement du fichier principal MistralChat.py.

    Intégration de tous les modules :

        RAG,

        mémoire,

        sentiment,

        tickets,

        base de données.

    Ajout de l’affichage des sources et du score de similarité.

    Ajout du feedback utilisateur (👍 / 👎 + commentaire).

    Correction d’un bug d’import : get_all_interactions.

- Page Feedback Viewer

    Création de pages/1_Feedback_Viewer.py.

    Affichage des interactions, feedbacks, sources et métadonnées.

    Correction d’un mauvais import (data_loader → database).

    Tests de visualisation sur plusieurs sessions.

- Documentation du projet

    Rédaction d’une description complète du projet dans le README.

    Ajout des descriptions détaillées des modules :

        vector_store,

        query_classifier,

        database,

        memory,

        sentiment,

        tickets,

        pages.

    Ajout de la section architecture + choix techniques.

    Création du fichier DEVLOG.md.

