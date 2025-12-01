import chromadb
import chromadb.errors
from chromadb.utils import embedding_functions
from datasets import load_dataset
import os

# 1. Setup ChromaDB (Local Vector Store)
# This will create a folder 'roast_db' in your backend directory
client = chromadb.PersistentClient(path="./roast_db")

# Use a free, local embedding model (no OpenAI costs)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Delete collection if it exists (to start fresh) try/except block
try:
    client.delete_collection(name="reddit_roasts")
except (ValueError, chromadb.errors.NotFoundError):
    pass

collection = client.create_collection(
    name="reddit_roasts",
    embedding_function=sentence_transformer_ef
)

print("📥 Downloading Dataset (this might take a moment)...")
# Load the dataset
ds = load_dataset("gus-gustavo/reddit_roastme", split="train")

# 2. Filter & Process
# We don't want ALL of them (it's huge). Let's take 2000 random samples 
# or filter for high quality if the dataset has scores.
# For this dataset, we'll shuffle and take a subset to keep it fast.
shuffled_ds = ds.shuffle(seed=42).select(range(2000))

documents = []
ids = []
metadatas = []

print(f"🔥 Ingesting {len(shuffled_ds)} toxic comments into Vector DB...")

for i, item in enumerate(shuffled_ds):
    # Depending on dataset structure, 'text' is usually the roast 
    # and we might have 'title' as context.
    # Adjust keys below based on exact dataset columns if they differ.
    
    roast_text = item.get('body') or item.get('text')
    
    # Skip empty or deleted comments
    if not roast_text or "[deleted]" in roast_text or len(roast_text) < 20:
        continue

    documents.append(roast_text)
    ids.append(f"roast_{i}")
    # We can store extra info if needed
    metadatas.append({"source": "reddit"})

# 3. Add to Database
# Chroma handles the embedding (converting text to numbers) automatically
batch_size = 100
for i in range(0, len(documents), batch_size):
    print(f"Processing batch {i} to {i+batch_size}...")
    collection.add(
        documents=documents[i:i+batch_size],
        ids=ids[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size]
    )

print("✅ Knowledge Base Built! You can now run the backend.")