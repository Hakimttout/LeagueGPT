# app/config.py

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHROMA_DIR = os.path.join(ROOT_DIR, "data", "chroma", "leaguegpt")
CHUNK_DIR = os.path.join(ROOT_DIR, "data", "patch_notes", "chunks")
PATCH_DIR = os.path.join(ROOT_DIR, "data", "patch_notes")

EMBED_MODEL = "intfloat/multilingual-e5-base"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-12-v2"
LLM_MODEL = "mistral"

def get_chroma_host():
    env = os.getenv("ENV", "local")
    if env == "local":
        return "localhost", 8001
    else:
        return "chroma", 8000