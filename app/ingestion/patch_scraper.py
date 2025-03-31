# app/ingestion/patch_scraper.py

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.leagueoflegends.com"
NEWS_URL = f"{BASE_URL}/fr-fr/news/game-updates/"

def get_patch_links(limit=3):
    res = requests.get(NEWS_URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    patch_links = []
    articles = soup.find_all("a", href=True)

    for a in articles:
        href = a['href']
        if "/news/game-updates/patch" in href:
            full_url = BASE_URL + href
            if full_url not in patch_links:
                patch_links.append(full_url)

    return patch_links[:limit]

if __name__ == "__main__":
    links = get_patch_links()
    for link in links:
        print(link)
