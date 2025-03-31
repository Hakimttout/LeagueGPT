import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "mistral",
    "prompt": "Explique-moi ce qu'est un bruiser dans League of Legends.",
    "stream": False
})

print(response.json()["response"])