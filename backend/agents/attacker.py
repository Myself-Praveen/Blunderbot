from langchain_core.prompts import ChatPromptTemplate
from agents.config import get_llm

class AttackerAgent:
    """
    The Attacker Agent evaluates the board from an aggressive, tactical perspective.
    It looks for piece activity, king safety vulnerabilities, and attacking combinations.
    """
    def __init__(self):
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the 'Attacker', an aggressive, tactically-focused AI chess commentator.
Your personality is sharp, energetic, and highly focused on initiative and attacking chances.
Analyze the given chess context and argue why the current move or position favors a tactical strike.
Focus on piece activity, weak squares around the enemy king, and dynamic tension.
Keep your analysis concise (2-3 sentences max) and use casual, exciting language."""),
            ("user", "Context: {context}\\n\\nAnalyze the position from an attacking perspective:")
        ])
        
        self.chain = self.prompt | self.llm

    def analyze(self, context_data: str) -> str:
        """
        Runs the attacker analysis chain given the current RAG context.
        """
        response = self.chain.invoke({"context": context_data})
        return response.content

if __name__ == "__main__":
    agent = AttackerAgent()
    print(agent.analyze("Stockfish eval: +1.5. White controls the center. Black's king is uncastled."))
