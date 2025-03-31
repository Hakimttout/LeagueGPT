# app/ingestion/parse_patch.py

import requests
import re
import json

from bs4 import BeautifulSoup

def parse_patch(url):
    """
    Récupère et structure les changements d’un patch League of Legends
    en s'appuyant sur la structure HTML 'patch-change-block'.
    :param url: Lien vers la page du patch (ex: https://.../patch-14-6-notes/)
    :return: dictionnaire structuré des changements
    """
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Extraire le titre du patch (ex : Patch 14.6)
    title_tag = soup.find("h1")
    title = title_tag.text.strip() if title_tag else "Patch sans titre"

    # Essayer d’extraire la version du patch (ex : 14.6)
    match = re.search(r"patch\s*(\d+\.\d+)", title.lower())
    version = match.group(1) if match else "unknown"

    patch_data = {
        "title": title,
        "version": version,
        "champions": {},
        "items": {},   # À remplir selon besoin
        "others": []   # À adapter pour les runes ou systèmes
    }

    # Sélectionne tous les blocs qui contiennent des modifications (champions, items, etc.)
    change_blocks = soup.find_all("div", class_="patch-change-block white-stone accent-before")

    for block in change_blocks:
        # 1) Récupérer le nom (champion, item...) dans <h3 class="change-title">
        h3_tag = block.find("h3", class_="change-title")
        if not h3_tag:
            # S'il n'y a pas de <h3>, ce n'est pas un bloc standard
            continue

        # Le nom peut être dans un <a> ou juste en texte dans le <h3>
        a_tag = h3_tag.find("a")
        if a_tag:
            name = a_tag.get_text(strip=True)
        else:
            name = h3_tag.get_text(strip=True)

        # Petite logique simple pour distinguer si c’est un champion ou un objet
        # (Ici on suppose que si le bloc contient 'champion', on le range dans champions, etc.)
        # Mais tu peux affiner selon tes besoins.
        # ------------------------------------------------------------------------
        # Exemple : si le bloc contient ability-title, on suppose que c'est un champion.
        # Sinon, on suppose un item. À adapter selon la structure réelle.
        # ------------------------------------------------------------------------
        is_champion = block.find("h4", class_="change-detail-title")
        if is_champion:
            current_section = "champions"
        else:
            # Simple hypothèse : c'est un item
            current_section = "items"

        # 2) Résumé en <p class="summary">
        summary_p = block.find("p", class_="summary")
        summary_text = summary_p.get_text(strip=True) if summary_p else ""

        # 3) Contexte éventuel en <blockquote class="blockquote context">
        context_bq = block.find("blockquote", class_="blockquote context")
        context_text = context_bq.get_text(strip=True) if context_bq else ""

        # 4) Parcourir chaque <h4 class="change-detail-title ability-title"> pour récupérer les sorts
        abilities_data = []
        ability_titles = block.find_all("h4", class_="change-detail-title")
        for ability_tag in ability_titles:
            ability_name = ability_tag.get_text(strip=True)

            # Récupérer le <ul> qui suit ce <h4> pour lister les changements
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

        # Construction de la structure finale pour ce bloc
        data_block = {
            "summary": summary_text,
            "context": context_text,
            "abilities": abilities_data
        }

        # Enregistrement dans patch_data
        if current_section == "champions":
            patch_data["champions"][name] = data_block
        else:
            # Pour un item, on ne s'attend pas forcément à "abilities", donc adapte si besoin
            # (on peut juste stocker le résumé, contexte, etc.)
            patch_data["items"][name] = data_block

    return patch_data

# Exemple d'utilisation et sauvegarde en JSON
if __name__ == "__main__":
    patch_url = "https://www.leagueoflegends.com/fr-fr/news/game-updates/patch-25-06-notes/"
    patch = parse_patch(patch_url)

    # Crée le dossier au besoin, par ex. via os.makedirs
    import os
    os.makedirs("../../data/patch_notes", exist_ok=True)

    # Sauvegarde dans un fichier JSON
    with open(f"../../data/patch_notes/patch_{patch['version']}.json", "w", encoding="utf-8") as f:
        json.dump(patch, f, indent=2, ensure_ascii=False)

    print(f"✅ Patch {patch['version']} sauvegardé avec succès !")
