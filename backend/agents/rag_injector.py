import sys
import os

# Ensure backend imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from similarity import get_nearest_neighbors
try:
    from graph_traversal import traverse_opening, get_opening_name
except ImportError:
    # Handle environment where Neo4j isn't mocking properly
    def traverse_opening(fen, depth=3): return []
    def get_opening_name(fen): return "Unknown"

def build_rag_context(fen: str, move_number: int, latent_vector: list = None) -> str:
    """
    Constructs the hybrid RAG context string to be injected into the LLM prompts.
    
    If in the opening phase (move < 15), it relies on Neo4j GraphRAG for exact
    opening theory, win-rates, and nomenclature.
    
    If in the mid-game (move >= 15), it relies on Qdrant Vector DB for semantic
    similarity mapping to historical GM positions (Narrative RAG).
    """
    context_lines = []
    
    # 1. GraphRAG (Opening Phase)
    if move_number < 15:
        opening_name = get_opening_name(fen)
        context_lines.append(f"Opening Phase Detected: {opening_name}.")
        
        try:
            candidates = traverse_opening(fen, depth=2)
            if candidates:
                context_lines.append("Historical Continuations from Graph DB:")
                for c in candidates:
                    context_lines.append(f" - {c['move']} (Played {c['frequency']}x, White Win: {c['white_win_pct']}%, Black Win: {c['black_win_pct']}%)")
        except Exception as e:
            context_lines.append(f"Graph retrieval failed: {str(e)}")
            
    # 2. VectorRAG (Mid/End-game Phase)
    elif latent_vector is not None:
        context_lines.append("Mid-Game Phase Detected. Semantic Similarity Search:")
        try:
            neighbors = get_nearest_neighbors(latent_vector, limit=2)
            if neighbors:
                for idx, n in enumerate(neighbors):
                    context_lines.append(f" - Match {idx+1} Score: {n['score']:.2f}. Source DB: {n['source']}")
        except Exception as e:
            context_lines.append(f"Vector retrieval failed: {str(e)}")
            
    if not context_lines:
        return "No historical RAG context available for this position."
        
    return "\\n".join(context_lines)

if __name__ == "__main__":
    # Test RAG construction
    import chess
    print(build_rag_context(chess.STARTING_FEN, move_number=0))
