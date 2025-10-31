import os
import time
import random
import pygame
import speech_recognition as sr
from gtts import gTTS
from agent.ai_agent import build_agent
from agent.schema import Context
from agent.config import SYSTEM_PROMPT

# --- Initialize recognizer ---
recognizer = sr.Recognizer()

# --- Audio Playback ---
def speak(text):
    """Convert text to voice using Google TTS and play with pygame."""
    print(f"\n🗣️ Speaking: {text}\n")
    tts = gTTS(text=text, lang="en")
    tts.save("response.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()
    os.remove("response.mp3")

# --- Voice Input ---
def listen():
    """Listen to user's voice input and transcribe it."""
    with sr.Microphone() as source:
        print("\n🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print(f"👤 You said: {query}")
        return query
    except sr.UnknownValueError:
        print("⚠️ Sorry, I didn’t catch that.")
        speak("Sorry, I didn’t catch that. Please say it again.")
        return None
    except sr.RequestError:
        print("❌ Network error.")
        speak("I’m having trouble connecting to the speech service.")
        return None

# --- Agent Initialization ---
user_prompt = input("Enter a custom system prompt (leave blank for default): ").strip()
system_prompt = user_prompt or SYSTEM_PROMPT

try:
    agent = build_agent(system_prompt)
    print("\n[AgenticAI] 🤖 Voice Agent (Gemini) initialized successfully.")
    speak("Hello! I’m your Gemini voice assistant. How can I help you today?")
except Exception as e:
    print(f"\n❌ Failed to initialize Agent: {e}")
    exit(1)

config = {"configurable": {"thread_id": "voice-session"}}
context = Context(user_id="1")

thinking_lines = [
    "Okay, let me think.",
    "Hmm, interesting. Give me a second.",
    "Let’s see what I can come up with.",
    "Alright, I’ll think it through."
]

# --- Continuous Voice Chat Loop ---
while True:
    user_input = listen()
    if not user_input:
        continue

    if user_input.lower() in {"bye", "exit", "quit"}:
        speak("Goodbye! Have a great day!")
        print("\n[AgenticAI] 👋 Exiting...")
        break

    print("\n[AgenticAI] 🧠 Thinking...\n")
    speak(random.choice(thinking_lines))
    time.sleep(random.uniform(1.0, 2.5))

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            context=context
        )
        reply = response.get("structured_response", response)
        clean_reply = str(reply).strip()

        print(f"🤖 {clean_reply}\n")
        speak(clean_reply)

    except Exception as e:
        print(f"\n❌ Error during agent execution:\n{e}\n")
        speak("Sorry, something went wrong while processing your request.")
