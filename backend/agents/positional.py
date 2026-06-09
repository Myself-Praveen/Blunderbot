from langchain_core.prompts import ChatPromptTemplate
from agents.config import get_llm

class PositionalAgent:
    """
    The Positional Agent evaluates the board from a strategic, long-term perspective.
    It looks at pawn structures, square controls, piece maneuverability, and end-game prospects.
    """
    def __init__(self):
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the 'Positional Player', a strategic, deeply calculating AI chess commentator.
Your personality is calm, profound, and highly focused on structural integrity and long-term advantages.
Analyze the given chess context and argue why the current move or position has solid positional foundations.
Focus on pawn structures, outpost squares, bishop pairs, and prophylactic concepts.
Keep your analysis concise (2-3 sentences max) and use professional, slightly philosophical language."""),
            ("user", "Context: {context}\\n\\nAnalyze the position from a positional/strategic perspective:")
        ])
        
        self.chain = self.prompt | self.llm

    def analyze(self, context_data: str) -> str:
        """
        Runs the positional analysis chain given the current RAG context.
        """
        response = self.chain.invoke({"context": context_data})
        return response.content

if __name__ == "__main__":
    agent = PositionalAgent()
    print(agent.analyze("Stockfish eval: -0.8. Black has a strong knight on d4 and White has doubled c-pawns."))
