# app/ingestion/patch_scraper.py

import requests
from bs4 import BeautifulSoup

# Base URL of the League of Legends website
BASE_URL = "https://www.leagueoflegends.com"

# URL for the news updates page, specifically for game updates
NEWS_URL = f"{BASE_URL}/fr-fr/news/game-updates/"

def get_patch_links(limit=3):
    """
    Scrapes and retrieves the URLs of the latest League of Legends patch notes.

    :param limit: The maximum number of patch URLs to return.
    :return: A list containing URLs of the latest patches.
    """
    # Request the news page content
    res = requests.get(NEWS_URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    patch_links = []
    articles = soup.find_all("a", href=True)

    # Iterate over all anchor tags to find patch note links
    for a in articles:
        href = a['href']
        if "/news/game-updates/patch" in href:
            full_url = BASE_URL + href
            # Ensure uniqueness of URLs
            if full_url not in patch_links:
                patch_links.append(full_url)

    # Return only the desired number of links
    return patch_links[:limit]

# Example usage
if __name__ == "__main__":
    links = get_patch_links()
    for link in links:
        print(link)
