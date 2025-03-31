# app/embedding/build_chroma.py

import json
import os
import chromadb
from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm
import numpy as np
from app.config import CHROMA_DIR, CHUNKS_PATH, EMBED_MODEL

def normalize(vec):
    return vec / np.linalg.norm(vec)

# Paramètres
COLLECTION_NAME = "patch_chunks"

def build_chroma():
    # Load des chunks
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Setup Chroma
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Supprimer l’ancienne collection si elle existe
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(name=COLLECTION_NAME)

    collection = client.create_collection(name=COLLECTION_NAME)

    # Embedding model
    # Chargement du modèle e5-base
    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
    model = AutoModel.from_pretrained(EMBED_MODEL)

    def embed_text(text: str):
        # Préfixe obligatoire pour les documents
        text = "passage: " + text.strip()
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            output = model(**inputs)
            embeddings = output.last_hidden_state[:, 0, :]
            return normalize(embeddings.squeeze().numpy())

    print(f"🔢 {len(chunks)} chunks à embedder...")

    # Injection dans Chroma par batch
    for i, chunk in enumerate(tqdm(chunks)):
        doc_id = f"chunk-{i}"
        embedding = embed_text(chunk["text"])

        # On ajoute le chunk avec métadonnées
        collection.add(
            documents=[chunk["text"]],
            embeddings=[embedding],
            metadatas=[chunk["metadata"]],
            ids=[doc_id]
        )

    print(f"✅ {len(chunks)} chunks indexés dans Chroma ({COLLECTION_NAME})")

if __name__ == "__main__":
    build_chroma()
