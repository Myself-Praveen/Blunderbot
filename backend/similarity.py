from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "chess_positions_128d"

def get_nearest_neighbors(query_vector: list, limit: int = 5):
    """
    Performs an exact or HNSW approximate nearest neighbor (ANN) search
    against the Qdrant vector database using Cosine Similarity.
    
    Returns the top-K similar historical chess positions, unlocking
    Narrative RAG without needing Stockfish centipawn exact matches.
    """
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    results = []
    for hit in search_result:
        results.append({
            "score": hit.score,
            "fen": hit.payload.get("fen", ""),
            "source": hit.payload.get("source", "unknown")
        })
        
    return results

if __name__ == "__main__":
    # Test with a dummy 128-d vector
    dummy_query = [0.1] * 128
    try:
        res = get_nearest_neighbors(dummy_query, limit=3)
        print("Nearest Neighbors Found:")
        print(res)
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
