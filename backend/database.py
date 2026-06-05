import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Initialize Qdrant Client (Using local memory/storage for dev, switch to URL for prod)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

COLLECTION_NAME = "chess_positions_128d"

def init_qdrant_schema():
    """
    Defines the Vector Database schema.
    We use 128-d vectors to match our PyTorch Autoencoder latent space.
    Cosine similarity is optimal for normalized embeddings.
    """
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=128, 
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{COLLECTION_NAME}' successfully created.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

if __name__ == "__main__":
    init_qdrant_schema()
