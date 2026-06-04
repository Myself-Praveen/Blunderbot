import torch
from torch.utils.data import IterableDataset, DataLoader
from tqdm import tqdm
import time
from encoder import fen_to_tensor
from pgn_parser import parse_games

class LichessPositionalDataset(IterableDataset):
    def __init__(self, pgn_path: str, min_elo: int = 2500, max_samples: int = 100000):
        super(LichessPositionalDataset).__init__()
        self.pgn_path = pgn_path
        self.min_elo = min_elo
        self.max_samples = max_samples

    def __iter__(self):
        count = 0
        board_generator = parse_games(self.pgn_path, self.min_elo)
        
        for board in board_generator:
            if count >= self.max_samples:
                break
                
            tensor = fen_to_tensor(board.fen())
            yield tensor
            count += 1

def profile_dataloader():
    """
    Performance profiling for the data ingestion pipeline using tqdm.
    """
    print("Initializing DataLoader Profiler...")
    
    # In production, pgn_path would point to the decompressed Lichess DB
    dataset = LichessPositionalDataset(pgn_path="data/lichess_db.pgn", max_samples=1000)
    dataloader = DataLoader(dataset, batch_size=32, num_workers=0)
    
    start_time = time.time()
    
    try:
        for batch_idx, batch in enumerate(tqdm(dataloader, desc="Ingesting Batches")):
            # Simulate sending batch to GPU
            pass
    except FileNotFoundError:
        print("PGN file not found. Run download_lichess.py first.")
        
    end_time = time.time()
    print(f"Data ingestion profiling completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    profile_dataloader()
