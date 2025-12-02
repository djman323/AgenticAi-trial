import os
import time
import random
import pygame
import speech_recognition as sr
from gtts import gTTS
import inquirer
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.spinner import Spinner
from textual.events import Key
from agent.ai_agent import build_agent
from agent.schema import Context
from agent.config import SYSTEM_PROMPT

# Initialize Rich console
console = Console()

# Global state
class State:
    def __init__(self):
        self.current_tool = None
        self.tool_history = []
        self.messages = []
        self.thinking = False
        self.voice_mode = False
        self.thinking_lines = [
            "Okay, let me think.",
            "Hmm, interesting. Give me a second.",
            "Let's see what I can come up with.",
            "Alright, I'll think it through."
        ]
        
state = State()

# --- Initialize recognizer ---
recognizer = sr.Recognizer()

# --- TUI Layout ---
def make_layout() -> Layout:
    layout = Layout(name="root")
    
    # Create the split layout
    layout.split_row(
        Layout(name="main", ratio=2),
        Layout(name="sidebar", ratio=1)
    )
    
    # Split the main section into input and chat
    layout["main"].split_column(
        Layout(name="chat", ratio=7),
        Layout(name="input", ratio=2)
    )
    
    return layout

def generate_chat_panel():
    messages = state.messages[-10:]  # Show last 10 messages
    content_parts = []
    for i, msg in enumerate(messages):
        icon = "🤖" if i % 2 else "👤"
        formatted_msg = f"{icon} {msg}"
        # Add separator between messages
        if i > 0:
            content_parts.append("─" * 50)
        content_parts.append(formatted_msg)
    
    content = "\n".join(content_parts)
    return Panel(
        content,
        title="💬 Chat History",
        border_style="blue",
        padding=(1, 2),
        subtitle=f"Messages: {len(state.messages)}"
    )

def generate_tool_panel():
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Time", style="yellow")
    
    # Add current tool if any
    if state.current_tool:
        table.add_row(
            state.current_tool,
            "[yellow]Running[/yellow]" if state.thinking else "[green]Complete[/green]",
            time.strftime("%H:%M:%S")
        )
    
    # Add tool history (most recent first)
    for tool in reversed(state.tool_history[-5:]):
        table.add_row(
            tool,
            "[green]Complete[/green]",
            time.strftime("%H:%M:%S")
        )
        
    status = "🔴 Idle"
    if state.thinking:
        status = "🟢 Processing"
    elif state.voice_mode and not state.thinking:
        status = "🎤 Listening"
        
    return Panel(
        table,
        title=f"Tool Activity - {status}",
        border_style="green",
        padding=(1, 2)
    )

# --- Audio Playback ---
def speak(text):
    """Convert text to voice using Google TTS and play with pygame."""
    if not state.voice_mode:
        return
        
    with console.status("[yellow]Speaking...[/yellow]"):
        tts = gTTS(text=text, lang="en")
        tts.save("response.mp3")

        pygame.mixer.init()
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.quit()
        os.remove("response.mp3")

def update_layout(layout: Layout):
    """Update the TUI layout with current state"""
    layout["chat"].update(generate_chat_panel())
    layout["sidebar"].update(generate_tool_panel())
    if state.thinking:
        layout["input"].update(Panel(Spinner("dots"), title="Thinking...", border_style="yellow"))
    else:
        layout["input"].update(Panel("Type your message or 'exit' to quit", title="Input", border_style="blue"))

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

# --- Initialize Agent ---
def initialize_agent():
    # Ask for interaction mode
    questions = [
        inquirer.List('mode',
                     message="How would you like to interact with the AI?",
                     choices=['Text', 'Voice']),
    ]
    answers = inquirer.prompt(questions)
    state.voice_mode = answers['mode'] == 'Voice'
    
    # Get system prompt
    questions = [
        inquirer.Text('prompt',
                     message="Enter a custom system prompt (or press enter for default)",
                     default=SYSTEM_PROMPT)
    ]
    answers = inquirer.prompt(questions)
    system_prompt = answers['prompt']

    try:
        agent = build_agent(system_prompt)
        console.print("\n[green]🤖 AI Agent initialized successfully![/green]")
        welcome_msg = "Hello! I'm your AI assistant. How can I help you today?"
        state.messages.append(welcome_msg)
        speak(welcome_msg)
        return agent
    except Exception as e:
        console.print(f"\n[red]❌ Failed to initialize Agent: {e}[/red]")
        exit(1)

def handle_terminal_command(command: str, layout: Layout):
    """Handle terminal command execution with user permission"""
    questions = [
        inquirer.Confirm('execute',
                        message=f"Do you want to execute this command: {command}?",
                        default=False)
    ]
    with Live(layout, refresh_per_second=4, screen=False):
        answers = inquirer.prompt(questions)
        if answers and answers['execute']:
            state.current_tool = "Terminal"
            os.system(command)
            state.tool_history.append("Terminal")
            update_layout(layout)

def main():
    # Initialize agent
    agent = initialize_agent()
    config = {"configurable": {"thread_id": "interactive-session"}}
    context = Context(user_id="1")
    
    # Create initial layout
    layout = make_layout()
    layout["chat"].update(Panel("Welcome! Starting chat...", title="💬 Chat History", border_style="blue"))
    layout["sidebar"].update(Panel("Initializing...", title="🔧 Tool Activity", border_style="green"))
    layout["input"].update(Panel("Type your message or 'exit' to quit", title="✍️ Input", border_style="blue"))
    
    # Create Live display context
    live = Live(
        layout,
        refresh_per_second=4,
        screen=True,  # Changed to True to take over the screen
        vertical_overflow="visible"
    )
    
    try:
        # Start the live display
        live.start()
        should_exit = False
        
        while not should_exit:
            try:
                # Get user input
                if state.voice_mode:
                    user_input = listen()
                    if not user_input:
                        continue
                else:
                    live.stop()  # Temporarily stop live display for input
                    questions = [
                        inquirer.Text('input',
                                    message="You",
                                    default="")
                    ]
                    answers = inquirer.prompt(questions)
                    live.start()  # Restart live display
                    if not answers:
                        continue
                    user_input = answers['input']
                
                if user_input.lower() in {"bye", "exit", "quit"}:
                    speak("Goodbye! Have a great day!")
                    should_exit = True
                    continue
                
                # Add user message to history
                state.messages.append(user_input)
                update_layout(layout)
                
                # Process response
                state.thinking = True
                state.current_tool = None
                update_layout(layout)
                
                try:
                    # Invoke agent
                    response = agent.invoke(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config=config,
                        context=context
                    )
                    
                    # Extract response and tool information
                    reply = response.get("structured_response", response)
                    clean_reply = str(reply).strip()
                    
                    # Track tool usage from response
                    if hasattr(response, 'get') and response.get('tool_calls'):
                        for tool_call in response['tool_calls']:
                            tool_name = tool_call.get('name', 'Unknown Tool')
                            state.current_tool = tool_name
                            state.tool_history.append(tool_name)
                            update_layout(layout)
                    
                    # Check for terminal commands
                    if "```bash" in clean_reply or "```sh" in clean_reply:
                        try:
                            command = clean_reply.split("```")[1].split("\n", 2)[1].strip()
                            handle_terminal_command(command, layout)
                        except IndexError:
                            console.print("[red]Error: Could not parse terminal command[/red]")
                    
                    # Update state and display
                    state.messages.append(clean_reply)
                    state.thinking = False
                    update_layout(layout)
                    
                    # Speak response if in voice mode
                    speak(clean_reply)
                    
                except Exception as e:
                    error_msg = "Sorry, something went wrong while processing your request."
                    state.messages.append(f"❌ {error_msg}")
                    state.thinking = False
                    update_layout(layout)
                    speak(error_msg)
                    console.print(f"\n[red]Error: {e}[/red]")
                    
            except KeyboardInterrupt:
                should_exit = True
                continue
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue
    except KeyboardInterrupt:
        should_exit = True
    finally:
        # Clean up
        live.stop()
        if state.voice_mode:
            pygame.mixer.quit()
        if should_exit:
            console.print("[blue]👋 Thank you for using AgenticAI![/blue]")

if __name__ == "__main__":
    main()


