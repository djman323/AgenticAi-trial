from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from .config import model, SYSTEM_PROMPT, selected_model
from .tools import read_file, write_file, list_files
from .schema import Context, ResponseFormat

# --- In-memory checkpoint for multi-step reasoning ---
checkpointer = InMemorySaver()

def build_agent(system_prompt: str = SYSTEM_PROMPT):
    """
    Dynamically build an Agentic AI Developer with a given system prompt.
    Enables full tool support for Gemini and similar models.
    """
    is_gemini = "gemini" in (selected_model or "").lower()

    if is_gemini:
        print("[AgenticAI] 🤖 Using Gemini with full tool support.")
        return create_agent(
            model=model,
            tools=[read_file, write_file, list_files],
            system_prompt=system_prompt,
            response_format=ResponseFormat,
            context_schema=Context,
            checkpointer=checkpointer,
        )

    # ❌ Fallback for unsupported models
    raise RuntimeError(f"Unsupported model type detected: {selected_model}. Please use Gemini or add a compatible handler.")
