import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="BlunderBot AI Engine", description="Hybrid GraphRAG Chess Commentator")

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "BlunderBot Core Online", "version": "0.1.0"}

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/commentary")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive FEN and move history from the client
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # TODO: Route to Redis Queue for Stockfish Analysis
            # TODO: Route to Neo4j/Qdrant for RAG context
            # TODO: Route to LLM for multi-agent debate
            
            # Mock Response for now
            mock_response = {
                "eval": 0.5,
                "classification": "normal",
                "dialogue": [
                    {"agent": "Attacker", "text": "Solid move, fighting for the center."},
                    {"agent": "Positional", "text": "Agreed. It maintains tension without overcommitting."}
                ],
                "visuals": {
                    "highlights": [],
                    "arrows": []
                }
            }
            
            # Simulate processing delay
            await asyncio.sleep(1)
            
            await manager.send_personal_message(json.dumps(mock_response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
