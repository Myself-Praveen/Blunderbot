import chess.pgn
from typing import Iterator, Tuple

def parse_games(file_path: str, min_elo: int = 2500) -> Iterator[chess.Board]:
    """
    Parses a PGN file and yields board states from games where both players
    have an ELO >= min_elo (e.g. Grandmaster level).
    """
    with open(file_path, 'r') as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            
            try:
                white_elo = int(game.headers.get("WhiteElo", 0))
                black_elo = int(game.headers.get("BlackElo", 0))
            except ValueError:
                continue
                
            # Pre-processor: Filter out low-quality games
            if white_elo < min_elo or black_elo < min_elo:
                continue
                
            # Iterate through the board states of the game
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                yield board.copy()

if __name__ == "__main__":
    # Example usage:
    # for board in parse_games("data/lichess_db.pgn"):
    #     print(board.fen())
    pass
