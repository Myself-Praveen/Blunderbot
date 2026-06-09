import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# We default to GPT-4o for complex chess reasoning, but can fallback to a cheaper model
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

def get_llm():
    """
    Initializes and returns the LangChain ChatOpenAI instance.
    Requires OPENAI_API_KEY to be set in the environment.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY not found in environment. LLM Agents will fail.")
        
    return ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        api_key=api_key,
        max_tokens=500
    )

if __name__ == "__main__":
    # Simple test
    try:
        llm = get_llm()
        print(f"LLM successfully configured using model: {DEFAULT_MODEL}")
    except Exception as e:
        print(f"Failed to configure LLM: {e}")
