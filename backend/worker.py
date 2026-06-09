import os
from celery import Celery

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
BACKEND_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

# Initialize Celery app
celery_app = Celery(
    "blunderbot_worker",
    broker=BROKER_URL,
    backend=BACKEND_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30, # Strict 30 second limit for engine tasks
)

if __name__ == "__main__":
    celery_app.start()

@celery_app.task(name="evaluate_position_task")
def evaluate_position_task(fen: str, depth: int = 15):
    """
    Celery task that spawns an isolated Stockfish engine instance
    to evaluate a board state asynchronously, preventing the FastAPI 
    event loop from blocking on heavy C++ computation.
    """
    from stockfish_engine import StockfishEngine
    
    engine = StockfishEngine(depth=depth)
    try:
        engine.start()
        score = engine.evaluate_position(fen)
        engine.stop()
        return {"fen": fen, "score": score}
    except Exception as e:
        if engine.process:
            engine.stop()
        return {"fen": fen, "error": str(e)}
