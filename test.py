import chromadb
client = chromadb.HttpClient(host="chroma", port=8000)
print(client.list_collections())