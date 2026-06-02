import React, { useState, useEffect, useCallback } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { motion } from 'framer-motion';

function App() {
  const [game, setGame] = useState(new Chess());
  const [evalScore, setEvalScore] = useState(50); // 0 to 100 representing white's advantage
  const [chatLog, setChatLog] = useState([
    { agent: "System", text: "Welcome to BlunderBot. Waiting for your first move..." }
  ]);
  const [arrows, setArrows] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Connect to WebSocket backend
    const ws = new WebSocket("ws://localhost:8000/ws/commentary");
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Update eval bar (mapping -10 to +10 centipawns to a 0-100 percentage height)
      const newScore = Math.min(Math.max((data.eval + 10) * 5, 0), 100);
      setEvalScore(newScore);
      
      // Add dialogue to chat
      if (data.dialogue) {
        setChatLog(prev => [...prev, ...data.dialogue]);
      }
      
      // Set arrows
      if (data.visuals && data.visuals.arrows) {
        setArrows(data.visuals.arrows);
      }
    };
    
    setSocket(ws);
    return () => ws.close();
  }, []);

  const makeAMove = useCallback(
    (move) => {
      const gameCopy = new Chess(game.fen());
      try {
        const result = gameCopy.move(move);
        setGame(gameCopy);
        
        // Send move to backend
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({
            event: "move",
            fen: gameCopy.fen(),
            san: result.san
          }));
        }
        return true;
      } catch (e) {
        return false;
      }
    },
    [game, socket]
  );

  function onDrop(sourceSquare, targetSquare) {
    const move = makeAMove({
      from: sourceSquare,
      to: targetSquare,
      promotion: 'q'
    });
    return move;
  }

  return (
    <div className="flex h-screen w-full bg-chess-dark text-white p-8">
      {/* Evaluation Bar */}
      <div className="w-8 h-[600px] bg-black rounded overflow-hidden mr-4 relative flex flex-col justify-end">
        <div 
          className="w-full bg-white eval-bar-fill"
          style={{ height: `${evalScore}%` }}
        />
      </div>

      {/* Chessboard Container */}
      <div className="w-[600px] h-[600px] rounded shadow-2xl">
        <Chessboard 
          position={game.fen()} 
          onPieceDrop={onDrop}
          customDarkSquareStyle={{ backgroundColor: '#739552' }}
          customLightSquareStyle={{ backgroundColor: '#ebecd0' }}
          customArrows={arrows}
          animationDuration={300}
        />
      </div>

      {/* Multi-Agent Chat Panel */}
      <div className="ml-8 flex-1 bg-[#262421] rounded-lg p-6 flex flex-col shadow-2xl backdrop-blur-md">
        <h2 className="text-2xl font-bold mb-4 text-gray-200">GM Commentary</h2>
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {chatLog.map((msg, idx) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={idx} 
              className={`p-3 rounded-md ${msg.agent === 'Attacker' ? 'bg-red-900/30 border-l-4 border-red-500' : 
                                         msg.agent === 'Positional' ? 'bg-blue-900/30 border-l-4 border-blue-500' : 
                                         'bg-gray-800'}`}
            >
              <strong className="text-sm text-gray-400 block mb-1">{msg.agent}</strong>
              <span className="text-gray-100">{msg.text}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
