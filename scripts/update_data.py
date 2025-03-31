# scripts/update_data.py

import os
import sys

# Ajoute le chemin de base du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.generate_chunks import run_ingestion_pipeline
from app.embedding.build_chroma import build_chroma

if __name__ == "__main__":
    print(" Étape 1 : Ingestion des patchs + génération des chunks...")
    run_ingestion_pipeline(limit=3)

    print("\n Étape 2 : Indexation des chunks dans Chroma...")
    build_chroma()

    print("\n Mise à jour terminée ! Ton système RAG est prêt 💪")
