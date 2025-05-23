# app/ingestion/parse_patch.py

import requests
import re
import json

from bs4 import BeautifulSoup

def parse_patch(url):
    """
    Fetches and structures changes from a League of Legends patch,
    using the HTML structure 'patch-change-block'.
    :param url: URL of the patch page (e.g., https://.../patch-14-6-notes/)
    :return: structured dictionary of changes
    """
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Extract patch title (e.g., Patch 14.6)
    title_tag = soup.find("h1")
    title = title_tag.text.strip() if title_tag else "Untitled Patch"

    # Extract patch version (e.g., 14.6)
    match = re.search(r"patch\s*(\d+\.\d+)", title.lower())
    version = match.group(1) if match else "unknown"

    patch_data = {
        "title": title,
        "version": version,
        "champions": {},
        "items": {},   # Adjust as needed
        "others": []   # Adapt for runes or systems
    }

    # Select all blocks containing changes (champions, items, etc.)
    change_blocks = soup.find_all("div", class_="patch-change-block white-stone accent-before")

    for block in change_blocks:
        # Get the name (champion, item, etc.) from <h3 class="change-title">
        h3_tag = block.find("h3", class_="change-title")
        if not h3_tag:
            continue

        # Name could be in <a> or just text inside <h3>
        a_tag = h3_tag.find("a")
        if a_tag:
            name = a_tag.get_text(strip=True)
        else:
            name = h3_tag.get_text(strip=True)

        # Simple logic to determine if it's a champion or an item
        is_champion = block.find("h4", class_="change-detail-title")
        current_section = "champions" if is_champion else "items"

        # Summary in <p class="summary">
        summary_p = block.find("p", class_="summary")
        summary_text = summary_p.get_text(strip=True) if summary_p else ""

        # Context in <blockquote class="blockquote context">
        context_bq = block.find("blockquote", class_="blockquote context")
        context_text = context_bq.get_text(strip=True) if context_bq else ""

        # Iterate through <h4 class="change-detail-title ability-title"> to get abilities
        abilities_data = []
        ability_titles = block.find_all("h4", class_="change-detail-title")
        for ability_tag in ability_titles:
            ability_name = ability_tag.get_text(strip=True)

            # Get the <ul> following this <h4> for changes
            ul_tag = ability_tag.find_next_sibling("ul")
            changes_list = []
            if ul_tag:
                li_tags = ul_tag.find_all("li", recursive=False)
                for li in li_tags:
                    strong = li.find("strong")
                    label = strong.get_text(strip=True) if strong else ""
                    text = li.get_text(strip=True)
                    changes_list.append({
                        "label": label,
                        "text": text
                    })

            abilities_data.append({
                "ability_name": ability_name,
                "changes": changes_list
            })

        # Structure final data for this block
        data_block = {
            "summary": summary_text,
            "context": context_text,
            "abilities": abilities_data
        }

        # Save in patch_data
        if current_section == "champions":
            patch_data["champions"][name] = data_block
        else:
            patch_data["items"][name] = data_block

    return patch_data

# Example usage and saving as JSON
if __name__ == "__main__":
    patch_url = "https://www.leagueoflegends.com/fr-fr/news/game-updates/patch-25-06-notes/"
    patch = parse_patch(patch_url)

    # Create directory if needed
    import os
    os.makedirs("../../data/patch_notes", exist_ok=True)

    # Save to JSON file
    with open(f"../../data/patch_notes/patch_{patch['version']}.json", "w", encoding="utf-8") as f:
        json.dump(patch, f, indent=2, ensure_ascii=False)

    print(f"Patch {patch['version']} successfully saved!")
