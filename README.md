# BlunderBot ♟️🤖

> **A real-time, multi-agent chess commentary platform. Leverages hybrid GraphRAG, custom PyTorch positional embeddings, and asynchronous Redis queues to analyze your blunders with historical context via WebSockets.**

## 🌟 The "Wolf in Sheep's Clothing" Architecture

Don't let the playful name fool you. **BlunderBot** is engineered as a highly scalable, distributed system demonstrating elite-tier backend and ML engineering principles. It solves the core problem of generic LLM chess commentators by using actual mathematical board similarity and multi-agent debates.

### 🧠 Core Engineering Features
- **Positional Vector Embeddings:** Uses a custom Convolutional Autoencoder to compress 2D spatial board configurations into dense 128-d vectors.
- **Hybrid GraphRAG:** Utilizes Neo4j for $O(1)$ traversal of chess opening trees, switching to Qdrant/Pinecone Vector Search for mid-game positional similarity.
- **Asynchronous Telemetry:** Decouples heavy C++ Stockfish evaluation from the PyTorch inference pipeline using Redis Message Queues to manage backpressure.
- **Multi-Agent RAG Debate:** Spawns concurrent LLM personas (e.g., The Aggressor vs. The Positional Master) to debate the move in a real-time WebSocket stream.
- **Premium Real-Time UX:** Chess.com-grade UI featuring smooth-transition evaluation bars, CSS micro-animations for brilliant moves (`!!`) and blunders (`??`), and native Web Audio integration.

---

## 🛠️ Tech Stack
- **Frontend:** React, TailwindCSS, Framer Motion, React-Chessboard.
- **Backend Gateway:** Python (FastAPI), WebSockets, Pydantic.
- **Worker Nodes:** Redis, Celery, C++ Stockfish 16.
- **Machine Learning:** PyTorch (CNN Autoencoder), Llama-3/Claude.
- **Databases:** PostgreSQL (User Auth/State), Neo4j (Graph Openings), Qdrant (Vector Similarity).

---

## 📁 Repository Structure
* `backend/` - The FastAPI gateway, Redis queue workers, and Stockfish orchestration.
* `frontend/` - The React application and WebSocket client.
* `model/` - PyTorch training scripts for the chess positional autoencoder and data extraction from Lichess open databases.

*(Work in progress...)*
