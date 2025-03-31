# app/backend/retrieve.py

import chromadb
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
import torch
from collections import defaultdict
import torch.nn.functional as F
import requests
from app.config import CHROMA_DIR, EMBED_MODEL, RERANK_MODEL

# === CONFIGURATION ===
COLLECTION_NAME = "patch_chunks"

# === EMBEDDING MODEL (E5 base) ===
embed_tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
embed_model = AutoModel.from_pretrained(EMBED_MODEL)

# === RERANKER MODEL (MiniLM) ===
rerank_tokenizer = AutoTokenizer.from_pretrained(RERANK_MODEL)
rerank_model = AutoModelForSequenceClassification.from_pretrained(RERANK_MODEL)

# === CHROMA CLIENT ===
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(name=COLLECTION_NAME)

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
def search_chunks(user_query, k=10):
    query_embedding = embed_query(user_query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return list(zip(results["documents"][0], results["metadatas"][0], results["distances"][0]))

# === RERANKING ===
def rerank_chunks(query: str, documents: list[str], metadatas: list[dict], top_k=5, score_gap=0.05, debug=False):
    # Préparation des paires pour le reranker
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
        print("\n🎯 Reranker scores:")
        for doc, meta, score in scored:
            champ = meta.get("champion", "?")
            print(f"- {champ} | {score:.4f} | {doc[:90]}...")

    # Étape 1 : Regrouper par champion (intelligence métier)
    grouped = defaultdict(list)
    for doc, meta, score in scored:
        champ = meta.get("champion", "inconnu")
        grouped[champ].append((doc, score))

    dominant_champion, group_chunks = max(grouped.items(), key=lambda item: len(item[1]))

    if debug:
        print(f"\n👑 Champion dominant : {dominant_champion} ({len(group_chunks)} chunks)")

    # Si suffisamment de chunks du même champion (>=2), on les prend tous
    MAX_CHUNKS = 14  # au cas où

    if len(group_chunks) >= 2:
        selected_chunks = group_chunks[:MAX_CHUNKS]
        if debug:
            print(f"✅ Chunks retenus : {len(selected_chunks)} / {len(group_chunks)}")
        return [(doc, score) for doc, score in selected_chunks]

    # Sinon : fallback sur cut dynamique par score gap
    selected = [scored[0]]
    for prev, curr in zip(scored, scored[1:]):
        if abs(curr[2] - prev[2]) < score_gap:
            selected.append(curr)
        else:
            break

    return [(doc, score) for doc, _, score in selected[:top_k]]



# === PROMPTING + GENERATION (Ollama) ===
def build_prompt(chunks: list, question: str):
    context = "\n\n---\n\n".join(chunks)
    prompt = f"""
        Tu es un expert de League of Legends.
        
        Voici des extraits du patch note et des changements récents concernant des champions et objets :
        
        {context}
        
        En te basant uniquement sur ce contexte, réponds à la question suivante de manière claire, structurée, et concise :
        
        {question}
        
        Si tu n’as pas assez d’informations, indique-le clairement.
    """
    return prompt.strip()

def ask_ollama(prompt: str, model: str = "mistral"):
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"].strip()

# === PIPELINE COMPLET ===
def generate_answer(question: str, n_chunks=10, top_k=3):
    raw = search_chunks(question, k=n_chunks)
    docs = [doc for doc, _, _ in raw]
    metas = [meta for _, meta, _ in raw]
    for doc, meta, dist in raw:
        print(f"- {meta.get('champion')} | {dist:.4f} | {doc[:100]}...")
    top_docs = rerank_chunks(question, docs, metas, top_k=7, debug=True)
    top_texts = [doc for doc, _ in top_docs]
    prompt = build_prompt(top_texts, question)
    return ask_ollama(prompt)
