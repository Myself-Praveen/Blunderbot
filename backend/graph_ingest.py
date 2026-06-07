import chess.pgn
from graph_db import driver

MAX_OPENING_DEPTH = 15  # Only the first 15 moves constitute "opening theory"

def ingest_game_to_graph(game: chess.pgn.Game):
    """
    Takes a single parsed PGN game and inserts its first 15 moves
    into the Neo4j graph as a chain of Position nodes connected by MOVE edges.
    
    Also tracks the game result to build win-rate statistics on each node.
    """
    result = game.headers.get("Result", "*")
    white_win = 1 if result == "1-0" else 0
    black_win = 1 if result == "0-1" else 0
    draw = 1 if result == "1/2-1/2" else 0
    
    board = game.board()
    prev_fen = board.fen()
    
    with driver.session() as session:
        # Ensure root position exists
        session.run("""
            MERGE (p:Position {fen: $fen})
            ON CREATE SET p.move_number = 0, p.white_wins = 0, p.black_wins = 0, p.draws = 0
            SET p.white_wins = p.white_wins + $ww,
                p.black_wins = p.black_wins + $bw,
                p.draws = p.draws + $d
        """, fen=prev_fen, ww=white_win, bw=black_win, d=draw)
        
        for move_num, move in enumerate(game.mainline_moves(), start=1):
            if move_num > MAX_OPENING_DEPTH:
                break
                
            san = board.san(move)
            uci = move.uci()
            board.push(move)
            current_fen = board.fen()
            
            # MERGE ensures no duplicate positions/edges
            session.run("""
                MERGE (prev:Position {fen: $prev_fen})
                MERGE (curr:Position {fen: $curr_fen})
                ON CREATE SET curr.move_number = $move_num,
                              curr.white_wins = 0, curr.black_wins = 0, curr.draws = 0
                SET curr.white_wins = curr.white_wins + $ww,
                    curr.black_wins = curr.black_wins + $bw,
                    curr.draws = curr.draws + $d
                MERGE (prev)-[m:MOVE {san: $san}]->(curr)
                ON CREATE SET m.uci = $uci, m.frequency = 1
                ON MATCH SET m.frequency = m.frequency + 1
            """, prev_fen=prev_fen, curr_fen=current_fen,
                 move_num=move_num, san=san, uci=uci,
                 ww=white_win, bw=black_win, d=draw)
            
            prev_fen = current_fen

def ingest_pgn_file(file_path: str, min_elo: int = 2500, max_games: int = 1000):
    """
    Reads a PGN file and ingests qualifying games into the Neo4j opening tree.
    """
    count = 0
    with open(file_path, 'r') as pgn:
        while count < max_games:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            
            try:
                white_elo = int(game.headers.get("WhiteElo", 0))
                black_elo = int(game.headers.get("BlackElo", 0))
            except ValueError:
                continue
            
            if white_elo < min_elo or black_elo < min_elo:
                continue
            
            ingest_game_to_graph(game)
            count += 1
            
            if count % 100 == 0:
                print(f"Ingested {count} games into the opening tree.")
    
    print(f"Opening tree ingestion complete. Total games: {count}")

if __name__ == "__main__":
    ingest_pgn_file("data/lichess_db.pgn", max_games=500)
