import redis
import json
import os
import asyncio

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Standard Redis client for Pub/Sub
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=2, decode_responses=True)

class PubSubManager:
    """
    Manages Redis Publish/Subscribe channels.
    Allows the Celery workers to broadcast Stockfish evaluation scores
    back to the FastAPI gateway, which then routes it to the correct 
    WebSocket client connection.
    """
    def __init__(self, channel="blunderbot_scores"):
        self.channel = channel

    def publish_score(self, session_id: str, fen: str, score: float):
        """Called by Celery worker when evaluation finishes."""
        message = {
            "session_id": session_id,
            "fen": fen,
            "score": score,
            "type": "stockfish_eval"
        }
        redis_client.publish(self.channel, json.dumps(message))

    async def subscribe_and_listen(self, websocket_manager):
        """
        Runs continuously in a FastAPI background task.
        Listens for published scores and dispatches them via WebSockets.
        """
        pubsub = redis_client.pubsub()
        pubsub.subscribe(self.channel)
        
        # Non-blocking listen loop
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = json.loads(message["data"])
                # Route to the appropriate WebSocket client via the manager
                await websocket_manager.broadcast_to_session(
                    data["session_id"], 
                    json.dumps(data)
                )
            await asyncio.sleep(0.01)

pubsub_manager = PubSubManager()
