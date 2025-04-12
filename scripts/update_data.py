# scripts/update_data.py
import os
import sys

# Extend sys.path to access app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.generate_chunks import run_ingestion_pipeline
from app.embedding.build_chroma import build_chroma
from app.chunking.chunk_patch_notes import chunk_from_riot_json
from app.config import CHUNK_DIR, PATCH_DIR, get_chroma_host
import chromadb
import json

# Ensure chunk directory exists
os.makedirs(CHUNK_DIR, exist_ok=True)

# Initialize Chroma client
host, port = get_chroma_host()
client = chromadb.HttpClient(host=host, port=port)

print("Step 1: Downloading + parsing patches...")
run_ingestion_pipeline(limit=3)

# Iterate through all patch files in the patch directory
for filename in os.listdir(PATCH_DIR):
    if filename.endswith(".json"):
        patch_version = filename.split("_")[-1].replace(".json", "")
        collection_name = f"patch_{patch_version}"

        # Skip if collection already exists in Chroma
        existing_collections = client.list_collections()
        if collection_name in existing_collections:
            print(f" Patch {patch_version} already indexed in Chroma, skipping.")
            continue

        # Load patch file and chunk it
        with open(os.path.join(PATCH_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = chunk_from_riot_json(data)

        print(f"{len(chunks)} chunks for patch {patch_version}")

        # Save chunks to file
        with open(os.path.join(CHUNK_DIR, f"chunks_{patch_version}.json"), "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        # Index chunks into Chroma
        os.environ["ENV"] = "local"
        build_chroma(chunks, collection_name)
