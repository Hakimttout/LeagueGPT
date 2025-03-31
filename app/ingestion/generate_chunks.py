# app/ingestion/generate_chunks.py

import os
import json

from app.ingestion.patch_scraper import get_patch_links
from app.ingestion.parse_patch import parse_patch
from app.chunking.chunk_patch_notes import chunk_from_riot_json
from app.config import CHUNKS_PATH, PATCH_DIR

def run_ingestion_pipeline(limit=3):
    os.makedirs(PATCH_DIR, exist_ok=True)
    all_chunks = []

    patch_links = get_patch_links(limit=limit)

    for url in patch_links:
        patch = parse_patch(url)
        version = patch.get("version", "unknown")
        patch_file = os.path.join(PATCH_DIR, f"patch_{version}.json")

        # Sauvegarde brute si pas déjà existant
        if not os.path.exists(patch_file):
            with open(patch_file, "w", encoding="utf-8") as f:
                json.dump(patch, f, indent=2, ensure_ascii=False)
            print(f"✅ Patch {version} sauvegardé")

        # Chunking à partir du JSON
        chunks = chunk_from_riot_json(patch)
        all_chunks.extend(chunks)

    # Sauvegarde finale de tous les chunks
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(all_chunks)} chunks enregistrés dans {CHUNKS_PATH}")

if __name__ == "__main__":
    run_ingestion_pipeline()
