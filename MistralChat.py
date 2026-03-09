import streamlit as st
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import logging
import datetime
from streamlit_feedback import streamlit_feedback

from utils.config import APP_TITLE, COMMUNE_NAME, MISTRAL_API_KEY
from utils.vector_store import VectorStoreManager
from utils.database import log_interaction, update_feedback
from utils.query_classifier import QueryClassifier
from utils.memory import save_message, get_recent_messages
from utils.sentiment import is_negative
from utils.tickets import create_ticket

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide"
)

@st.cache_resource
def get_vector_store():
    logging.info("Chargement du VectorStoreManager...")
    return VectorStoreManager()

@st.cache_resource
def get_mistral_client():
    if not MISTRAL_API_KEY:
        st.error("Erreur: La clé API Mistral (MISTRAL_API_KEY) n'est pas configurée.")
        st.stop()
    logging.info("Initialisation du client Mistral...")
    return MistralClient(api_key=MISTRAL_API_KEY)

@st.cache_resource
def get_query_classifier():
    logging.info("Initialisation du classificateur de requêtes...")
    return QueryClassifier()

vector_store = get_vector_store()
client = get_mistral_client()
query_classifier = get_query_classifier()

# État de session
if "messages" not in st.session_state:
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if "frustration_count" not in st.session_state:
        st.session_state.frustration_count = 0
    st.session_state.messages = []

if "last_interaction_id" not in st.session_state:
    st.session_state.last_interaction_id = None

# Sidebar
with st.sidebar:
    st.title(f"📚 ODG GPT")
    st.caption("Mon Assistant virtuel")

    if st.button("🔄 Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_interaction_id = None
        st.rerun()

    st.divider()

    st.subheader("⚙️ Paramètres")

    model_options = {
        "mistral-small-latest": "Mistral Small (rapide)",
        "mistral-large-latest": "Mistral Large (précis)"
    }
    selected_model = st.selectbox(
        "Modèle LLM",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0
    )

    num_docs = st.slider(
        "Nombre de documents à récupérer",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )

    min_score_percent = st.slider(
        "Score minimum (filtrer les résultats faibles)",
        min_value=0,
        max_value=100,
        value=75,
        step=5,
        format="%d%%"
    )
    min_score = min_score_percent / 100.0

    st.divider()

    st.subheader("📝 Informations")
    st.markdown(f"**Modèle sélectionné**: {model_options[selected_model]}")
    st.markdown(f"**Documents indexés**: {vector_store.index.ntotal if vector_store.index else 0}")

    if st.session_state.messages:
        st.info(f"{len(st.session_state.messages) // 2} échanges dans cette conversation")

        conversation_text = "\n\n".join([
            f"{'Utilisateur' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in st.session_state.messages
        ])

        header = f"Conversation avec l'assistant virtuel de {COMMUNE_NAME}\n"
        header += f"Date: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        conversation_text = header + conversation_text

        st.download_button(
            label="💾 Télécharger la conversation",
            data=conversation_text,
            file_name=f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Corps principal
st.title(f"📚 {APP_TITLE}")
st.caption(f"Posez vos questions sur tous les documents que vous voulez !!!")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("Sources utilisées"):
                for i, source in enumerate(message["sources"]):
                    meta = source.get("metadata", {})
                    st.markdown(f"**Source {i+1}:** `{meta.get('source', 'N/A')}`")
                    st.markdown(f"*Score de similarité:* {source.get('score', 0.0):.2f}%")
                    if "raw_score" in source:
                        st.markdown(f"*Score brut:* {source.get('raw_score', 0.0):.4f}")
                    st.markdown(f"*Catégorie:* `{meta.get('category', 'N/A')}`")
                    st.text_area(
                        f"Extrait {i+1}",
                        value=source.get("text", "")[:500] + "...",
                        height=100,
                        disabled=True,
                        key=f"src_{message.get('timestamp', 'no_ts')}_{i}"
                    )

# Zone de saisie
if prompt := st.chat_input("Posez votre question ici..."):

    session_id = st.session_state.session_id

    # Sauvegarde du message utilisateur
    save_message(session_id, "user", prompt)

    # Détection d’insatisfaction
    if is_negative(prompt):
        st.session_state.frustration_count += 1
    else:
        st.session_state.frustration_count = 0

    # Escalade immédiate
    if any(x in prompt.lower() for x in ["humain", "conseiller", "agent", "support"]):
        ticket_id = create_ticket(session_id, prompt)
        response_text = f"Je comprends. J’ai créé un ticket pour un agent humain. Numéro : {ticket_id}."
        st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": [], "timestamp": datetime.datetime.now().isoformat(), "interaction_id": None})
        save_message(session_id, "assistant", response_text)
        st.chat_message("assistant").markdown(response_text)
        st.stop()

    # Escalade automatique après 3 frustrations
    if st.session_state.frustration_count >= 3:
        ticket_id = create_ticket(session_id, "Frustration détectée")
        response_text = f"Je vois que mes réponses ne suffisent pas. J’ai créé un ticket pour un agent humain. Numéro : {ticket_id}."
        st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": [], "timestamp": datetime.datetime.now().isoformat(), "interaction_id": None})
        save_message(session_id, "assistant", response_text)
        st.chat_message("assistant").markdown(response_text)
        st.stop()

    # Affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": datetime.datetime.now().isoformat()})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🧠 Recherche d'informations et génération de la réponse...")

            # Mémoire récente
            recent_messages = get_recent_messages(session_id, limit=5)

            # Classification RAG / Direct
            needs_rag, confidence, reason = query_classifier.needs_rag(prompt)
            logging.info(f"Classification: {'RAG' if needs_rag else 'DIRECT'} (confiance: {confidence:.2f}) - Raison: {reason}")

            if needs_rag:
                logging.info(f"Recherche de documents pour: '{prompt}' (max: {num_docs}, score min: {min_score})")
                retrieved_docs = vector_store.search(prompt, k=num_docs, min_score=min_score)
            else:
                retrieved_docs = []

            if needs_rag and retrieved_docs:
                logging.info(f"{len(retrieved_docs)} documents récupérés.")
                context_str = "\n\n---\n\n".join([
                    f"Source: {doc['metadata'].get('source', 'Inconnue')} (Score: {doc['score']:.4f})\nContenu: {doc['text']}"
                    for doc in retrieved_docs
                ])
                sources_for_log = [
                    {"text": doc["text"], "metadata": doc["metadata"], "score": doc["score"]}
                    for doc in retrieved_docs
                ]
                system_prompt = f"""Vous êtes un assistant virtuel pour {COMMUNE_NAME}.
Répondez à la question de l'utilisateur en vous basant UNIQUEMENT sur le contexte fourni ci-dessous.
Si l'information n'est pas dans le contexte, dites que vous ne savez pas.
Contexte:
---
{context_str}
---"""
            elif needs_rag and not retrieved_docs:
                logging.warning("Aucun document pertinent trouvé.")
                sources_for_log = []
                system_prompt = f"""Vous êtes un assistant virtuel pour {COMMUNE_NAME}.
Aucune information pertinente n'a été trouvée dans la base de connaissances.
Indiquez poliment que vous ne disposez pas de cette information spécifique."""
            else:
                sources_for_log = []
                system_prompt = f"""Vous êtes un assistant virtuel pour {COMMUNE_NAME}.
Répondez à la question de l'utilisateur en utilisant vos connaissances générales.
Si la question concerne des informations très spécifiques à {COMMUNE_NAME} que vous ne connaissez pas, dites-le clairement."""

            system_message = ChatMessage(role="system", content=system_prompt)
            user_message = ChatMessage(role="user", content=prompt)

            messages_for_api = [system_message]
            for role, content in recent_messages:
                messages_for_api.append(ChatMessage(role=role, content=content))
            messages_for_api.append(user_message)

            logging.info(f"Appel de l'API Mistral Chat avec le modèle {selected_model}...")
            chat_response = client.chat(
                model=selected_model,
                messages=messages_for_api
            )
            response_text = chat_response.choices[0].message.content
            logging.info("Réponse générée par Mistral.")

            message_placeholder.markdown(response_text)
            save_message(session_id, "assistant", response_text)

            if sources_for_log:
                with st.expander("Sources utilisées"):
                    for i, source in enumerate(sources_for_log):
                        meta = source.get("metadata", {})
                        st.markdown(f"**Source {i+1}:** `{meta.get('source', 'N/A')}`")
                        st.markdown(f"*Score de similarité:* {source.get('score', 0.0):.2f}%")
                        if "raw_score" in source:
                            st.markdown(f"*Score brut:* {source.get('raw_score', 0.0):.4f}")
                        st.markdown(f"*Catégorie:* `{meta.get('category', 'N/A')}`")
                        st.text_area(
                            f"Extrait {i+1}",
                            value=source.get("text", "")[:500] + "...",
                            height=100,
                            disabled=True,
                            key=f"src_new_{i}"
                        )
            elif needs_rag:
                st.info("Aucune source pertinente n'a été trouvée dans la base de connaissances pour cette question.")
            else:
                st.info("Réponse générée en mode direct, sans consultation de la base de connaissances.")

            metadata = {
                "mode": "RAG" if needs_rag else "DIRECT",
                "confidence": confidence,
                "reason": reason
            }

            interaction_id = log_interaction(
                query=prompt,
                response=response_text,
                sources=sources_for_log,
                metadata=metadata
            )
            st.session_state.last_interaction_id = interaction_id
            logging.info(f"Interaction enregistrée avec ID: {interaction_id}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "sources": sources_for_log,
                "timestamp": datetime.datetime.now().isoformat(),
                "interaction_id": interaction_id
            })

    except Exception as e:
        if hasattr(e, "status_code") and hasattr(e, "message"):
            logging.error(f"Erreur API Mistral: {e}")
            message_placeholder.error(f"Une erreur s'est produite lors de la communication avec l'API Mistral: {e}")
        else:
            logging.error(f"Erreur inattendue: {e}", exc_info=True)
            message_placeholder.error(f"Une erreur s'est produite: {e}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Erreur: {e}",
            "sources": [],
            "timestamp": datetime.datetime.now().isoformat(),
            "interaction_id": None
        })
        st.session_state.last_interaction_id = None

# Feedback
last_assistant_message = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None)
current_interaction_id = last_assistant_message.get("interaction_id") if last_assistant_message else None

if current_interaction_id:
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optionnel] Commentaires :",
        key=f"feedback_{current_interaction_id}",
        align="flex-start",
        on_submit=lambda x: logging.info(f"Feedback soumis: {x}")
    )

    if feedback:
        feedback_score = feedback.get("score")

        if feedback_score in ["👍", "thumbs_up"]:
            feedback_score = "positive"
        elif feedback_score in ["👎", "thumbs_down"]:
            feedback_score = "negative"
        else:
            logging.warning(f"Score de feedback invalide: {feedback_score}")
            feedback_score = None

        feedback_value = 1 if feedback_score == "positive" else 0 if feedback_score == "negative" else None
        feedback_text = "positif" if feedback_score == "positive" else "négatif" if feedback_score == "negative" else "N/A"
        feedback_emoji = "👍" if feedback_score == "positive" else "👎" if feedback_score == "negative" else "N/A"
        comment = feedback.get("text", None)

        success = update_feedback(current_interaction_id, feedback_text, comment, feedback_value)
        if success:
            st.toast(f"Merci pour votre retour ({feedback_emoji}) !", icon="✅")
        else:
            st.toast("Erreur lors de l'enregistrement de votre retour.", icon="❌")
else:
    st.write("Posez une question pour pouvoir donner votre avis sur la réponse.")
