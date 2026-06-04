import requests
import zstandard as zstd
import os
import shutil

LICHESS_DB_URL = "https://database.lichess.org/standard/lichess_db_standard_rated_2024-01.pgn.zst"
DOWNLOAD_PATH = "data/lichess_db.pgn.zst"
OUTPUT_PATH = "data/lichess_db.pgn"

def download_and_extract():
    os.makedirs("data", exist_ok=True)
    
    print(f"Downloading {LICHESS_DB_URL}...")
    # Note: For production, we'd stream this. Using a placeholder download logic for scaffolding.
    with requests.get(LICHESS_DB_URL, stream=True) as r:
        r.raise_for_status()
        with open(DOWNLOAD_PATH, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
                
    print("Extracting ZStandard file...")
    dctx = zstd.ZstdDecompressor()
    with open(DOWNLOAD_PATH, 'rb') as ifh, open(OUTPUT_PATH, 'wb') as ofh:
        dctx.copy_stream(ifh, ofh)
        
    print("Done extracting!")

if __name__ == "__main__":
    download_and_extract()
