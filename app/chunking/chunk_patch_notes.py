# app/chunking/chunk_patch_notes.py

import os
import json

def chunk_from_riot_json(json_data):
    """
    Transforme un fichier de patch complet en une liste de chunks exploitables.
    Gère les changements pour : champions, items, runes/systèmes.
    """
    version = json_data.get("version", "unknown")
    chunks = []

    # Parcours des champions
    if "champions" in json_data:
        for champ, data in json_data["champions"].items():

            summary = data.get("summary", "")
            context = data.get("context", "")
            abilities = data.get("abilities", [])

            for ability in abilities:
                ability_name = ability.get("ability_name", "")
                for change in ability.get("changes", []):
                    label = change.get("label", "")
                    change_text = change.get("text", "")

                    full_text = (
                        f"Dans le patch {version}, {champ} a été modifié(e). "
                        f"Contexte : {context} "
                        f"Changement sur {ability_name} ({label}) : {change_text}"
                    )

                    chunks.append({
                        "text": full_text.strip(),
                        "metadata": {
                            "champion": champ,
                            "patch_version": version,
                            "ability": ability_name,
                            "type": "patch_note",
                            "source": "riot",
                            "language": "fr"
                        }
                    })

            # Chunk supplémentaire uniquement avec le résumé général
            if summary:
                chunks.append({
                    "text": f"Résumé du patch {version} pour {champ} : {summary}",
                    "metadata": {
                        "champion": champ,
                        "patch_version": version,
                        "type": "summary",
                        "source": "riot",
                        "language": "fr"
                    }
                })

    # Support des objets, runes, etc. si présents
    if "items" in json_data:
        for item, changes in json_data["items"].items():
            for change in changes.get("changes", []):
                label = change.get("label", "")
                text = change.get("text", "")

                full_text = (
                    f"Dans le patch {version}, l’objet {item} a été modifié. "
                    f"{label} : {text}"
                )

                chunks.append({
                    "text": full_text.strip(),
                    "metadata": {
                        "item": item,
                        "patch_version": version,
                        "type": "patch_note",
                        "source": "riot",
                        "language": "fr"
                    }
                })

    if "runes" in json_data:
        for rune, changes in json_data["runes"].items():
            for change in changes.get("changes", []):
                label = change.get("label", "")
                text = change.get("text", "")

                full_text = (
                    f"Dans le patch {version}, la rune {rune} a été modifiée. "
                    f"{label} : {text}"
                )

                chunks.append({
                    "text": full_text.strip(),
                    "metadata": {
                        "rune": rune,
                        "patch_version": version,
                        "type": "patch_note",
                        "source": "riot",
                        "language": "fr"
                    }
                })

    return chunks

def chunk_all_patches(input_dir="../../data/patch_notes", output_path="../../data/patch_notes/chunks.json"):
    """
    Applique le chunking à tous les fichiers patchs JSON présents dans un dossier.
    """
    all_chunks = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            path = os.path.join(input_dir, filename)
            print(path)
            with open(path, "r", encoding="utf-8") as f:
                patch_data = json.load(f)
                chunks = chunk_from_riot_json(patch_data)
                all_chunks.extend(chunks)

    # Sauvegarde dans un fichier unique
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(all_chunks)} chunks sauvegardés dans {output_path}")

if __name__ == "__main__":
    chunk_all_patches()
