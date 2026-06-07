from graph_db import driver

def traverse_opening(fen: str, depth: int = 3):
    """
    Given a board FEN, traverses the Neo4j opening tree to find:
    1. The most popular continuation moves (sorted by frequency).
    2. Win-rate statistics for each candidate move.
    
    This is the core of the GraphRAG system for openings (moves < 15).
    Instead of doing expensive vector similarity search, we do an O(1) 
    graph traversal to retrieve exact historical opening data.
    
    Returns a list of candidate moves with their stats.
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (current:Position {fen: $fen})-[m:MOVE]->(next:Position)
            WITH m, next,
                 next.white_wins AS ww,
                 next.black_wins AS bw,
                 next.draws AS d,
                 (next.white_wins + next.black_wins + next.draws) AS total_games
            RETURN m.san AS move,
                   m.frequency AS frequency,
                   next.fen AS resulting_fen,
                   next.move_number AS move_number,
                   ww, bw, d, total_games,
                   CASE WHEN total_games > 0 
                        THEN round(toFloat(ww) / total_games * 100, 1) 
                        ELSE 0.0 END AS white_win_pct,
                   CASE WHEN total_games > 0 
                        THEN round(toFloat(bw) / total_games * 100, 1) 
                        ELSE 0.0 END AS black_win_pct,
                   CASE WHEN total_games > 0 
                        THEN round(toFloat(d) / total_games * 100, 1) 
                        ELSE 0.0 END AS draw_pct
            ORDER BY m.frequency DESC
            LIMIT $depth
        """, fen=fen, depth=depth)
        
        candidates = []
        for record in result:
            candidates.append({
                "move": record["move"],
                "frequency": record["frequency"],
                "resulting_fen": record["resulting_fen"],
                "move_number": record["move_number"],
                "white_win_pct": record["white_win_pct"],
                "black_win_pct": record["black_win_pct"],
                "draw_pct": record["draw_pct"],
                "total_games": record["total_games"]
            })
        
        return candidates

def get_opening_name(fen: str):
    """
    Attempts to identify the opening name from a known position.
    Falls back to 'Unknown Opening' if the position is not catalogued.
    """
    # Common opening FENs (hardcoded subset for fast lookup)
    KNOWN_OPENINGS = {
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "King's Pawn Opening (1.e4)",
        "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": "Queen's Pawn Opening (1.d4)",
        "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1": "English Opening (1.c4)",
        "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1": "Réti Opening (1.Nf3)",
        "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": "French Defense (1.e4 e6)",
        "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": "Sicilian Defense (1.e4 c5)",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": "Open Game (1.e4 e5)",
    }
    
    # Strip move counters for comparison (just piece placement + active color)
    fen_key = fen
    return KNOWN_OPENINGS.get(fen_key, "Unknown Opening")

if __name__ == "__main__":
    import chess
    # Test: Traverse from starting position
    start_fen = chess.STARTING_FEN
    print(f"Traversing opening tree from starting position...")
    candidates = traverse_opening(start_fen)
    for c in candidates:
        print(f"  {c['move']}: played {c['frequency']}x | "
              f"W:{c['white_win_pct']}% B:{c['black_win_pct']}% D:{c['draw_pct']}%")
