# app/backend/retrieve.py
import chromadb
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import torch
from collections import defaultdict
import torch.nn.functional as F
import requests
from app.config import CHROMA_DIR, EMBED_MODEL, RERANK_MODEL, get_chroma_host
from typing import List, Tuple

# === CONFIGURATION ===
COLLECTION_NAME = "patch_chunks"

# === EMBEDDING MODEL (E5 base) ===
embed_tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
embed_model = AutoModel.from_pretrained(EMBED_MODEL)

# === RERANKER MODEL (MiniLM) ===
rerank_tokenizer = AutoTokenizer.from_pretrained(RERANK_MODEL)
rerank_model = AutoModelForSequenceClassification.from_pretrained(RERANK_MODEL)

# === CONVERSATION MEMORY (éphémère) ===
conversation_history: List[Tuple[str, str]] = []  # (user_message, bot_response)

# === CHROMA CLIENT ===
def get_collection_safe(name):
    host, port = get_chroma_host()
    client = chromadb.HttpClient(host=host, port=port)
    try:
        return client.get_collection(name=name)
    except Exception as e:
        print(f"Erreur lors de la récupération de la collection {name} : {e}")
        return None

def get_latest_patch_collection():
    import os
    from app.config import CHUNK_DIR

    files = [f for f in os.listdir(CHUNK_DIR) if f.startswith("chunks_") and f.endswith(".json")]
    if not files:
        raise ValueError("Aucune collection de patch trouvée.")

    versions = [f.replace("chunks_", "").replace(".json", "") for f in files]
    latest_version = sorted(versions, reverse=True)[0]

    print(f"Utilisation du patch le plus récent : {latest_version}")
    return get_collection_safe(f"patch_{latest_version}")

# === EMBEDDING ===
def normalize(vec):
    return vec / np.linalg.norm(vec)

def embed_query(text: str):
    text = "query: " + text.strip()
    inputs = embed_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        output = embed_model(**inputs)
        embeddings = output.last_hidden_state[:, 0, :]
        return normalize(embeddings.squeeze().numpy())

# === SEARCH ===
def search_chunks(user_query, collection, k=10):
    query_embedding = embed_query(user_query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return list(zip(results["documents"][0], results["metadatas"][0], results["distances"][0]))

# === RERANKING ===
def rerank_chunks(query: str, documents: list[str], metadatas: list[dict], top_k=5, score_gap=0.05, debug=False):
    documents = [doc for doc in documents if isinstance(doc, str) and doc.strip()]
    if not documents:
        return []

    pairs = [(query, doc) for doc in documents]
    inputs = rerank_tokenizer(pairs, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        scores = rerank_model(**inputs).logits.squeeze()

    probs = F.softmax(scores, dim=-1)
    if probs.ndim == 0:
        probs = probs.unsqueeze(0)

    scored = list(zip(documents, metadatas, probs.tolist()))
    scored.sort(key=lambda x: x[2], reverse=True)

    if debug:
        print("\nReranker scores:")
        for doc, meta, score in scored:
            champ = meta.get("champion", "?")
            print(f"- {champ} | {score:.4f} | {doc[:90]}...")

    grouped = defaultdict(list)
    for doc, meta, score in scored:
        champ = meta.get("champion", "inconnu")
        grouped[champ].append((doc, score))

    dominant_champion, group_chunks = max(grouped.items(), key=lambda item: len(item[1]))

    if debug:
        print(f"\nChampion dominant : {dominant_champion} ({len(group_chunks)} chunks)")

    MAX_CHUNKS = 14
    if len(group_chunks) >= 2:
        selected_chunks = group_chunks[:MAX_CHUNKS]
        if debug:
            print(f"Chunks retenus : {len(selected_chunks)} / {len(group_chunks)}")
        return [(doc, score) for doc, score in selected_chunks]

    selected = [scored[0]]
    for prev, curr in zip(scored, scored[1:]):
        if abs(curr[2] - prev[2]) < score_gap:
            selected.append(curr)
        else:
            break

    return [(doc, score) for doc, _, score in selected[:top_k]]

# === PROMPTING + GENERATION (Ollama) ===
def build_prompt(chunks: list, question: str, history: List[dict] = None):
    context = "\n\n---\n\n".join(chunks)

    # Formatage de l'historique
    history_text = ""
    if history:
        turns = []
        for msg in history:
            role = msg["role"]
            if role == "user":
                turns.append(f"Utilisateur : {msg['content']}")
            else:
                turns.append(f"Assistant : {msg['content']}")
        history_text = "\n\n".join(turns)

    prompt = f"""
        Tu es un expert de League of Legends.

        Voici des extraits du patch note et des changements récents concernant des champions et objets :

        {context}

        {history_text}

        En te basant uniquement sur ce contexte et la conversation précédente, réponds à la question suivante de manière claire, structurée, et concise :

        {question}

        Si tu n’as pas assez d’informations, indique-le clairement.
    """
    return prompt.strip()


def ask_ollama(prompt: str, model: str = "mistral"):
    response = requests.post("http://ollama:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    print(response.text)
    try:
        data = response.json()
    except Exception:
        return "Erreur : Réponse non JSON d’Ollama"

    if "response" in data:
        return data["response"].strip()
    else:
        return f"Erreur : champ 'response' absent dans la réponse Ollama - status {response.status_code}, body: {data}"

# === PIPELINE COMPLET ===
def generate_answer(question: str, n_chunks=10, top_k=3, history: List[dict] = None):
    collection = get_latest_patch_collection()
    if not collection:
        return "Aucune donnée disponible pour répondre à cette question."

    raw = search_chunks(question, collection=collection, k=n_chunks)
    docs = [doc for doc, _, _ in raw]
    metas = [meta for _, meta, _ in raw]
    for doc, meta, dist in raw:
        print(f"- {meta.get('champion')} | {dist:.4f} | {doc[:100]}...")

    top_docs = rerank_chunks(question, docs, metas, top_k=7, debug=True)
    top_texts = [doc for doc, _ in top_docs]

    prompt = build_prompt(top_texts, question, history=history)
    response = ask_ollama(prompt)

    conversation_history.append((question, response))
    return response
