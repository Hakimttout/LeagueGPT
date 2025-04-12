import os
import json

def chunk_from_riot_json(json_data):
    """
    Extract and transform patch notes (champions, items, runes) into a list of usable text chunks.
    """
    version = json_data.get("version", "unknown")
    chunks = []

    # Process champion changes
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

                    # Create full text describing an ability change
                    full_text = (
                        f"In patch {version}, {champ} was modified. "
                        f"Context: {context} "
                        f"Change in {ability_name} ({label}): {change_text}"
                    )

                    # Append chunk to list
                    chunks.append({
                        "text": full_text.strip(),
                        "metadata": {
                            "champion": champ,
                            "patch_version": version,
                            "ability": ability_name,
                            "type": "patch_note",
                            "source": "riot",
                            "language": "en"
                        }
                    })

            # General summary for the champion
            if summary:
                chunks.append({
                    "text": f"Summary of patch {version} for {champ}: {summary}",
                    "metadata": {
                        "champion": champ,
                        "patch_version": version,
                        "type": "summary",
                        "source": "riot",
                        "language": "en"
                    }
                })

    # Process item changes
    if "items" in json_data:
        for item, changes in json_data["items"].items():
            for change in changes.get("changes", []):
                label = change.get("label", "")
                text = change.get("text", "")

                full_text = (
                    f"In patch {version}, item {item} was modified. "
                    f"{label}: {text}"
                )

                chunks.append({
                    "text": full_text.strip(),
                    "metadata": {
                        "item": item,
                        "patch_version": version,
                        "type": "patch_note",
                        "source": "riot",
                        "language": "en"
                    }
                })

    # Process rune changes
    if "runes" in json_data:
        for rune, changes in json_data["runes"].items():
            for change in changes.get("changes", []):
                label = change.get("label", "")
                text = change.get("text", "")

                full_text = (
                    f"In patch {version}, rune {rune} was modified. "
                    f"{label}: {text}"
                )

                chunks.append({
                    "text": full_text.strip(),
                    "metadata": {
                        "rune": rune,
                        "patch_version": version,
                        "type": "patch_note",
                        "source": "riot",
                        "language": "en"
                    }
                })

    return chunks

def chunk_all_patches(input_dir="../../data/patch_notes", output_path="../../data/patch_notes/chunks.json"):
    """
    Generate a JSON file containing all chunks extracted from patches located in a specified directory.
    """
    all_chunks = []

    # Iterate through JSON files
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            path = os.path.join(input_dir, filename)
            print(f"Processing file: {path}")

            with open(path, "r", encoding="utf-8") as f:
                patch_data = json.load(f)
                chunks = chunk_from_riot_json(patch_data)
                all_chunks.extend(chunks)

    # Save all chunks to a single file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"{len(all_chunks)} chunks saved in {output_path}")

if __name__ == "__main__":
    chunk_all_patches()
