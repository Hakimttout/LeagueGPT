# app/frontend/streamlit_app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import streamlit as st
from app.backend.retrieve import generate_answer


# Mise en page de l'IHM
st.set_page_config(page_title="LeagueGPT++", page_icon="🧠", layout="centered")
st.title("💬 LeagueGPT++ — Chat éphémère autour de LoL")
st.markdown("Pose ta question sur un patch, un champion, un changement...")

# Initialiser l'historique du chat (temporaire)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage du chat existant
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input utilisateur
user_input = st.chat_input("Pose ta question ici...")

if user_input:
    # ➕ Ajouter la question au chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 🤖 Génération de la réponse via pipeline complet
    response = generate_answer(user_input)

    # ➕ Ajouter la réponse au chat
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
