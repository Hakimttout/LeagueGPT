# app/reranking/reranker.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Paramètres du modèle léger
RERANKER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Chargement du modèle
tokenizer = AutoTokenizer.from_pretrained(RERANKER_NAME)
model = AutoModelForSequenceClassification.from_pretrained(RERANKER_NAME)

def rerank(query, documents, top_k=3):
    """
    Rerank une liste de documents par pertinence par rapport à une requête.
    :param query: str
    :param documents: liste de textes
    :param top_k: nombre de résultats à garder
    :return: liste triée de tuples (doc, score)
    """
    pairs = [(query, doc) for doc in documents]

    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        scores = model(**inputs).logits.squeeze()

    probs = F.softmax(scores, dim=-1)  # Pour les modèles avec plusieurs classes
    if probs.ndim == 0:
        probs = probs.unsqueeze(0)

    scored_docs = list(zip(documents, probs.tolist()))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return scored_docs[:top_k]
