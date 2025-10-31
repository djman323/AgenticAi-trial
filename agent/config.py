import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Step 1: Load Gemini API Key from .env ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "❌ GEMINI_API_KEY not found.\n"
        "Please either set it using:\n"
        "   export GEMINI_API_KEY='your_key_here'\n"
        "or create a .env file in your project root with:\n"
        "   GEMINI_API_KEY=your_key_here"
    )

# --- Step 2: Initialize Gemini Model ---
try:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.4,
        max_output_tokens=1024,
        google_api_key=api_key,  # ✅ explicitly use the loaded key
    )
    selected_model = "gemini-2.0-flash-exp"
    print(f"[AgenticAI] ✅ Using Gemini model: {selected_model}")
except Exception as e:
    raise RuntimeError(f"❌ Could not initialize Gemini model.\n{e}")

# --- Step 3: System Prompt ---
SYSTEM_PROMPT = """You are an intelligent real-time voice assistant (Agentic AI Developer).

Your job is to:
1. Understand spoken instructions and respond naturally.
2. When coding-related, generate clean, correct code.
3. For general questions, provide concise and accurate answers.
4. Maintain a conversational, human-like tone.
5. Keep responses short and natural for speech output.
6. Never output metadata, symbols, or code formatting unless explicitly asked.

Your goal is to sound natural, helpful, and clear in every interaction.
"""
