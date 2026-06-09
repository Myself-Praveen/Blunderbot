import asyncio
from langchain_core.prompts import ChatPromptTemplate
from agents.config import get_llm
from agents.attacker import AttackerAgent
from agents.positional import PositionalAgent

class ModeratorAgent:
    """
    The Moderator Agent controls the multi-agent debate workflow.
    It takes the raw outputs from the Attacker and Positional agents,
    evaluates them against the hard Stockfish math and RAG context,
    and synthesizes a final, human-readable commentary stream.
    """
    def __init__(self):
        self.llm = get_llm()
        self.attacker = AttackerAgent()
        self.positional = PositionalAgent()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the 'Moderator' of a live chess broadcast.
Your job is to take the conflicting arguments from your two co-commentators (Attacker and Positional)
and synthesize them into a final, engaging verdict for the viewer.
You also have access to hard Engine math (Stockfish evaluation) and Historical DB Context.
Resolve their debate, highlight who is currently 'more correct' based on the engine eval, and summarize.
Keep your summary under 3 sentences. Be punchy, broadcast-style."""),
            ("user", "Engine Eval: {engine_eval}\\nHistorical DB Context: {rag_context}\\n\\nAttacker's Take: {attack_text}\\nPositional's Take: {position_text}\\n\\nModerator Verdict:")
        ])
        
        self.chain = self.prompt | self.llm

    async def generate_debate(self, engine_eval: float, rag_context: str):
        """
        Orchestrates the asynchronous debate workflow.
        Runs both agents concurrently, then synthesizes their output.
        """
        context_data = f"Stockfish: {engine_eval}. RAG Notes: {rag_context}"
        
        # Run sub-agents concurrently using asyncio (Langchain sync wraps via to_thread here in prod, 
        # but for simplicity we run sequentially or use ThreadPoolExecutor)
        # Note: True async requires ainvoke(), mapping here for standard execution
        attack_text = self.attacker.analyze(context_data)
        position_text = self.positional.analyze(context_data)
        
        # Moderator synthesis
        final_verdict = self.chain.invoke({
            "engine_eval": engine_eval,
            "rag_context": rag_context,
            "attack_text": attack_text,
            "position_text": position_text
        })
        
        return {
            "dialogue": [
                {"agent": "Attacker", "text": attack_text},
                {"agent": "Positional", "text": position_text},
                {"agent": "Moderator", "text": final_verdict.content}
            ]
        }

if __name__ == "__main__":
    # Test execution
    moderator = ModeratorAgent()
    result = asyncio.run(moderator.generate_debate(
        engine_eval=2.5,
        rag_context="This resembles the Sicilian Najdorf. Historical win rate for white is 55%."
    ))
    for d in result["dialogue"]:
        print(f"[{d['agent']}]: {d['text']}\\n")
