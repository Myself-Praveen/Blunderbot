import torch
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from network import ChessPositionalAutoencoder
from dataset import LichessPositionalDataset

# Connect to backend Qdrant
client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "chess_positions_128d"

def ingest_vectors(batch_size=64):
    """
    Passes extracted Lichess tensors through our pre-trained autoencoder,
    grabs the 128-d latent representation, and indexes it into Qdrant.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load model weights (ignoring decoder for inference)
    model = ChessPositionalAutoencoder(embedding_dim=128).to(device)
    try:
        model.load_state_dict(torch.load("checkpoints/autoencoder_v1.pt"))
    except FileNotFoundError:
        print("Warning: No checkpoint found, using random weights for testing pipeline.")
    model.eval()

    dataset = LichessPositionalDataset(pgn_path="data/lichess_db.pgn", max_samples=1000)
    
    # Simulated batch logic
    current_batch_points = []
    
    print("Ingesting vectors into Qdrant...")
    with torch.no_grad():
        for i, tensor in enumerate(dataset):
            tensor = tensor.unsqueeze(0).to(device) # Add batch dimension [1, 12, 8, 8]
            
            # Forward pass: We only care about the latent vector here
            _, latent = model(tensor)
            vector_128d = latent.cpu().numpy().flatten().tolist()
            
            # Create a vector point with metadata payload
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector_128d,
                payload={"fen": "simulated_fen_payload_string", "source": "lichess_2024"}
            )
            current_batch_points.append(point)
            
            if len(current_batch_points) >= batch_size:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=current_batch_points
                )
                current_batch_points = []
                
        # Insert remaining
        if current_batch_points:
            client.upsert(collection_name=COLLECTION_NAME, points=current_batch_points)
            
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_vectors()
