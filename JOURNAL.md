# Journal de Développement — Assistant RAG pour Documents #

Un carnet de bord détaillé retraçant toutes les étapes, problèmes, prompts, incompréhensions et apprentissages.

### `📅 02/03/2026 — Démarrage du projet : poser les fondations`

Aujourd’hui, j’ai officiellement commencé le projet Assistant RAG pour Documents.
Je voulais une base propre, modulaire, et évolutive.

`✔️ Actions réalisées`
- Création du dossier chatbot-support-rag/.
- Mise en place de l’environnement virtuel Python.
- Installation des dépendances essentielles : streamlit, sqlalchemy, faiss-cpu, sentence-transformers, python-dotenv, mistralai.
- Création des dossiers : utils/, inputs/, vector_db/, database/.

`⚠️ Problème rencontré`
FAISS refusait de s’installer sur Windows.
💬 Prompt envoyé à l’IA
- “FAISS ne s’installe pas sur Windows, comment faire ?”

🤖 Réponse de l’IA (résumé)
- → Installer faiss-cpu au lieu de faiss.
  
`🛠️ Correction`

    Installation réussie avec :
    pip install faiss-cpu.

### `📅 03/03/2026 — Construction du pipeline RAG`

Aujourd’hui, j’ai attaqué le cœur du projet : l’indexation et la recherche vectorielle.

`✔️ Actions réalisées`
- Développement de utils/vector_store.py.
- Extraction et découpage des documents en chunks.
- Génération des embeddings avec Sentence Transformers.
- Création de l’index FAISS.
- Test sur un premier PDF.
  
  `⚠️ Problème rencontré`
- Chunking trop agressif → certains - documents donnaient 10 000+ chunks.
- Erreur FAISS : dimension mismatch → embeddings incohérents.

`💬 Prompt envoyé à l’IA`

    “FAISS me renvoie une erreur de dimension alors que j’utilise le même modèle. Pourquoi ?”

`🤖 Réponse de l’IA (résumé)`

→ Le modèle d’embeddings était instancié plusieurs fois avec des paramètres différents.

`🛠️ Correction`

    Centralisation du modèle dans config.py.

### `🗓️ 04/03/2026 — Classification des requêtes`

Objectif : distinguer les questions nécessitant le RAG des questions générales.

`✔️ Actions réalisées`

-    Création de utils/query_classifier.py.

-    Mise en place d’une logique hybride :

        règles heuristiques,

        mini‑prompt Mistral.

-    Tests sur plusieurs requêtes.

`⚠️ Problème rencontré`

Le classifieur envoyait trop de requêtes vers le RAG.
💬 Prompt envoyé à l’IA

    “Comment améliorer la classification RAG vs non-RAG sans entraîner un modèle ?”

`🤖 Réponse de l’IA (résumé)`

→ Combiner règles + prompt de classification.

`🛠️ Correction`

    Ajustement des mots-clés.

    Réécriture du prompt de classification.

### `05/03/2026 — Base de données— Base de données et ORM`
Aujourd’hui, j’ai mis en place la persistance des interactions.

`✔️ Actions réalisées`

-    Développement de utils/database.py.

    Création des tables :

        interactions

        feedbacks

        tickets

-    Ajout des fonctions CRUD.

-    Tests avec SQLite.

`⚠️ Problème rencontré`

Erreur SQLAlchemy : “no such table”
💬 Prompt envoyé à l’IA

    “SQLAlchemy ne crée pas mes tables, pourtant mes modèles sont définis. Pourquoi ?”

`🤖 Réponse de l’IA (résumé)`

→ create_all() n’était pas exécuté au bon endroit.

`🛠️ Correction`

    Ajout de l’initialisation dans database.py.

### `📅 09/03/2026 — Mémoire conversationnelle`

Objectif : permettre au chatbot de garder le contexte.

`✔️ Actions réalisées`

    Création de utils/memory.py.

    Mise en place d’une fenêtre de contexte (5 derniers messages).

    Intégration dans le pipeline.

`⚠️ Problème rencontré`

Le contexte se mélangeait entre utilisateurs.

`💬 Prompt envoyé à l’IA`

    “Comment gérer une mémoire conversationnelle dans Streamlit sans mélange entre utilisateurs ?”

`🤖 Réponse de l’IA (résumé)`

→ Utiliser st.session_state.

`🛠️ Correction`

    Stockage du contexte par session.

### `📅 09/03/2026 — Détection d’insatisfaction`

Objectif : détecter les messages frustrés.

`✔️ Actions réalisées`

    Développement de utils/sentiment.py.

    Score de frustration.

    Déclenchement d’alertes.

`⚠️ Problème rencontré`

Beaucoup de faux positifs.

`💬 Prompt envoyé à l’IA`

    “Comment éviter les faux positifs dans un détecteur de frustration simple ?”

`🤖 Réponse de l’IA (résumé)`

→ Ajouter une liste pondérée de mots négatifs + seuil ajustable.

`🛠️ Correction`

    Ajustement du seuil.

    Nettoyage de la liste de mots.

### `🗓️ 09/03/2026 — Gestion des tickets`

Objectif : escalader vers un agent humain.

`✔️ Actions réalisées`

    Création de utils/tickets.py.

    Intégration avec le module sentiment.

    Enregistrement en base.

`⚠️ Problème rencontré`

Création multiple du même ticket.

💬 Prompt envoyé à l’IA

    “Comment éviter la création multiple d’un ticket pour un même message ?”

`🤖 Réponse de l’IA (résumé)`

→ Ajouter un verrou logique.

`🛠️ Correction`

    Vérification avant création.

### `🗓️ 10/03/2026 — Interface Streamlit`

Objectif : créer l’interface utilisateur.

`✔️ Actions réalisées`

-    Développement de MistralChat.py.

-    Intégration :

        RAG,

        mémoire,

        sentiment,

        tickets,

        base de données.

-    Affichage des sources.

-    Feedback utilisateur.

`⚠️ Problème rencontré`

Bug d’import : get_all_interactions

`💬 Prompt envoyé à l’IA`

    “Pourquoi Streamlit ne trouve pas ma fonction get_all_interactions ?”

`🤖 Réponse de l’IA (résumé)`

→ Mauvais chemin d’import.

`🛠️ Correction`

    Correction du chemin.

### `🗓️ 10/03/2026 — Page Feedback Viewer`

`✔️ Actions réalisées`

-    Création de pages/1_Feedback_Viewer.py.

-    Affichage des interactions, feedbacks, sources.

-    Correction d’un import incorrect.

### `🗓️ 16/03/2026 — Étude du MCP (Model Context Protocol)`

j’ai voulu comprendre comment les LLM modernes utilisent des outils externes.

`✔️ Actions réalisées`

    Visionnage de plusieurs vidéos YouTube sur le MCP.

    **Compréhension de son rôle :

        standardiser les appels d’outils,

        améliorer la fiabilité des agents,

        structurer les interactions.

    Tentative d’intégration d’un mini‑MCP maison.**


💬 Prompt envoyé à l’IA

    “Est-ce que je dois intégrer le MCP dans mon assistant RAG ?”

🤖 Réponse de l’IA (résumé)

→ Utile pour des agents avancés, mais pas nécessaire ici.

🛠️ Décision

    Documenter l’apprentissage mais ne pas intégrer le MCP.

### `🗓️ 17/03/2026 — Documentation finale`
✔️ Actions réalisées

    Rédaction du README complet.

    Description détaillée des modules.

    Ajout de la section architecture.

    Nettoyage du code.




Dans le journal il faut que j'explique tout les problèmes que j'ai rencontré, comment j'ai procéder pour ressoudre chaque partie, comment je me suis fait aider par l'ia, les problèmes d'incompréhensions, 
 Dire aussi que j'ai régarder des videos sur youtube sur la mise en place du MCP, j'ai apris son importance et une idée sur comment la mettre en place mème si j'ai pas la faire dans mon cas.