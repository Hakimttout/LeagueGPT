from app.__old__.prompts.llm_interface import build_prompt, ask_llm_local
import chromadb
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

from app.__old__.reranking.reranker import rerank

# Paramètres
CHROMA_DIR = "../../chroma/leaguegpt"
COLLECTION_NAME = "patch_chunks"

# Chargement du modèle e5-base (pour encoder la requête)
tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-base")
model = AutoModel.from_pretrained("intfloat/multilingual-e5-base")

def normalize(vec):
    return vec / np.linalg.norm(vec)

def embed_query(text: str):
    text = "query: " + text.strip()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        output = model(**inputs)
        embeddings = output.last_hidden_state[:, 0, :]
        return normalize(embeddings.squeeze().numpy())

# Question utilisateur
user_query = input("Pose ta question LoL : ")
query_embedding = embed_query(user_query)

# Connexion à Chroma
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(name=COLLECTION_NAME)

# Étape 1 – Récupération des top 10 candidats (dense retrieval)
raw_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=10,  # plus large pour que le reranker ait le choix
    include=["documents", "metadatas", "distances"]
)

# On extrait les documents pour le reranker
docs = raw_results["documents"][0]
metas = raw_results["metadatas"][0]

# Étape 2 – Reranking
reranked = rerank(user_query, docs, top_k=3)

top_chunks_texts = [doc for doc, _ in reranked]
prompt = build_prompt(top_chunks_texts, user_query)
response = ask_llm_local(prompt)

print("\n🤖 Réponse générée par LeagueGPT++ (local) :")
print(response)
