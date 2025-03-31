# app/config.py

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHROMA_DIR = os.path.join(ROOT_DIR, "data", "chroma", "leaguegpt")
CHUNKS_PATH = os.path.join(ROOT_DIR, "data", "patch_notes", "chunks.json")
PATCH_DIR = os.path.join(ROOT_DIR, "data", "patch_notes")

EMBED_MODEL = "intfloat/multilingual-e5-base"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-12-v2"
LLM_MODEL = "mistral"
