from chromadb import HttpClient

# Initialize Chroma client pointing to local ChromaDB instance
chroma = HttpClient(host="localhost", port=8001)

# List all available collections
collections = chroma.list_collections()
print("Available collections:", [col.name for col in collections])

# Access a specific collection (adjust name based on the list above)
collection = chroma.get_collection(name="patch_25.07")  # Update name as needed

# Check how many documents are stored in the collection
count = collection.count()
print(f"Documents in collection 'patch_14.7': {count}")

# Optional: display a sample document
docs = collection.get(include=["documents"], limit=1)
print("Sample document:", docs["documents"][0] if docs["documents"] else "No document found")
