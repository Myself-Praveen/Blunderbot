import subprocess
import os

# Default path to the Stockfish binary
# In production (Docker), this should point to the compiled C++ binary
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")

class StockfishEngine:
    """
    A Python wrapper around the Stockfish C++ binary using subprocess.
    Communicates via the Universal Chess Interface (UCI) protocol.
    """
    def __init__(self, depth=15):
        self.depth = depth
        self.process = None

    def start(self):
        """Spawns the Stockfish subprocess."""
        try:
            self.process = subprocess.Popen(
                [STOCKFISH_PATH],
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Initialize UCI protocol
            self._send_command("uci")
            self._wait_for("uciok")
            self._send_command("isready")
            self._wait_for("readyok")
        except FileNotFoundError:
            raise RuntimeError(f"Stockfish binary not found at {STOCKFISH_PATH}")

    def _send_command(self, command: str):
        if not self.process or not self.process.stdin:
            raise RuntimeError("Engine process is not running.")
        self.process.stdin.write(command + "\\n")
        self.process.stdin.flush()

    def _wait_for(self, expected_token: str):
        if not self.process or not self.process.stdout:
            return
        while True:
            line = self.process.stdout.readline().strip()
            if not line:
                break
            if expected_token in line:
                break

    def evaluate_position(self, fen: str, timeout: int = 10, max_retries: int = 3) -> float:
        """
        Evaluates a FEN position and returns the score in centipawns.
        Includes timeout protection and exponential backoff for engine crashes.
        """
        import time
        import math
        
        retries = 0
        while retries < max_retries:
            try:
                self._send_command("ucinewgame")
                self._send_command(f"position fen {fen}")
                self._send_command(f"go depth {self.depth}")

                best_score = 0.0
                start_time = time.time()
                
                while True:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Stockfish engine timed out after {timeout}s")
                        
                    line = self.process.stdout.readline().strip()
                    if not line:
                        continue
                    
                    if "score cp" in line:
                        parts = line.split()
                        try:
                            cp_index = parts.index("cp")
                            best_score = int(parts[cp_index + 1]) / 100.0
                        except (ValueError, IndexError):
                            pass
                    elif "score mate" in line:
                        parts = line.split()
                        try:
                            mate_index = parts.index("mate")
                            moves_to_mate = int(parts[mate_index + 1])
                            best_score = 1000.0 if moves_to_mate > 0 else -1000.0
                        except (ValueError, IndexError):
                            pass
                            
                    if line.startswith("bestmove"):
                        return best_score
                        
            except (TimeoutError, BrokenPipeError) as e:
                retries += 1
                if retries >= max_retries:
                    print(f"Engine failed after {max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff: 1s, 2s, 4s...
                sleep_time = math.pow(2, retries - 1)
                print(f"Engine crashed or timed out. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                
                # Reboot engine for next attempt
                self.stop()
                self.start()
                
        return 0.0

    def stop(self):
        """Terminates the Stockfish process cleanly."""
        if self.process:
            self._send_command("quit")
            self.process.wait(timeout=2)
            self.process = None

if __name__ == "__main__":
    # Test execution
    import chess
    try:
        engine = StockfishEngine(depth=10)
        engine.start()
        score = engine.evaluate_position(chess.STARTING_FEN)
        print(f"Starting position eval: {score}")
        engine.stop()
    except RuntimeError as e:
        print(e)
