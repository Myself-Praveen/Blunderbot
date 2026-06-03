import torch
import chess
import numpy as np

# Mapping piece types to layer indices
# 6 piece types * 2 colors = 12 channels
PIECE_TO_LAYER = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 2,
    chess.ROOK: 3,
    chess.QUEEN: 4,
    chess.KING: 5
}

def fen_to_tensor(fen: str) -> torch.Tensor:
    """
    Converts a FEN string into a 12x8x8 binary PyTorch tensor.
    Channels 0-5 are White pieces (P, N, B, R, Q, K).
    Channels 6-11 are Black pieces (p, n, b, r, q, k).
    """
    board = chess.Board(fen)
    tensor = np.zeros((12, 8, 8), dtype=np.float32)
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # 0 for white, 1 for black -> offset channels by 6 for black
            color_offset = 0 if piece.color == chess.WHITE else 6
            layer = PIECE_TO_LAYER[piece.piece_type] + color_offset
            
            # chess.SQUARES is 0-63 (0 is A1, 63 is H8)
            row = 7 - (square // 8) # Rank (0 is rank 8, 7 is rank 1)
            col = square % 8        # File (0 is a, 7 is h)
            
            tensor[layer, row, col] = 1.0
            
    return torch.from_numpy(tensor)

if __name__ == "__main__":
    # Test with starting position
    start_fen = chess.STARTING_FEN
    t = fen_to_tensor(start_fen)
    print(f"Tensor Shape: {t.shape}") # Should be [12, 8, 8]
    print(f"White Rooks Tensor at start:\\n{t[3]}")
