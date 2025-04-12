# app/ingestion/generate_chunks.py

import os
import json

from app.ingestion.patch_scraper import get_patch_links
from app.ingestion.parse_patch import parse_patch
from app.chunking.chunk_patch_notes import chunk_from_riot_json
from app.config import PATCH_DIR, CHUNK_DIR

def run_ingestion_pipeline(limit=3):
    os.makedirs(PATCH_DIR, exist_ok=True)
    os.makedirs(CHUNK_DIR, exist_ok=True)

    patch_links = get_patch_links(limit=limit)

    for url in patch_links:
        patch = parse_patch(url)
        version = patch.get("version", "unknown")
        patch_file = os.path.join(PATCH_DIR, f"patch_{version}.json")

        # Save raw patch if it doesn't exist
        if not os.path.exists(patch_file):
            with open(patch_file, "w", encoding="utf-8") as f:
                json.dump(patch, f, indent=2, ensure_ascii=False)
            print(f"Patch {version} saved")

        # Chunking the patch
        chunks = chunk_from_riot_json(patch)

        # Save individual chunks
        chunk_file = os.path.join(CHUNK_DIR, f"chunks_{version}.json")
        with open(chunk_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        print(f"{len(chunks)} chunks created for patch {version}")

if __name__ == "__main__":
    run_ingestion_pipeline()
