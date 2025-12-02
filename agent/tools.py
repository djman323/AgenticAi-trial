import os
import subprocess
from pathlib import Path
from langchain.tools import tool
from .schema import Context

BASE_DIR = Path(__file__).resolve().parent.parent

@tool
def read_file(file_name: str, context: Context) -> str:
    """Read the contents of a file."""
    file_path = BASE_DIR / file_name
    if not file_path.exists():
        return f"Error: The file {file_path} does not exist."
    with open(file_path, 'r') as f:
        return f.read()

@tool
def write_file(file_name: str, content: str) -> str:
    """Write content to a file."""
    file_path = BASE_DIR / file_name
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Successfully wrote to {file_path}"

@tool
def list_files(context: Context) -> str:
    """List all files in the project directory."""
    files = [f.name for f in BASE_DIR.iterdir() if f.is_file()]
    return "\n".join(files)

@tool
def delete_file(file_name: str) -> str:
    """Delete a file."""
    file_path = BASE_DIR / file_name
    if not file_path.exists():
        return f"Error: The file {file_path} does not exist."
    file_path.unlink()
    return f"Successfully deleted {file_path}"

@tool
def append_to_file(file_name: str, content: str) -> str:
    """Append content to a file."""
    file_path = BASE_DIR / file_name
    with open(file_path, 'a') as f:
        f.write(content)
    return f"Successfully appended to {file_path}"

@tool
def make_dir(dir_name: str) -> str:
    """Make a directory."""
    dir_path = BASE_DIR / dir_name
    if dir_path.exists():
        return f"Error: The directory {dir_path} already exists."
    dir_path.mkdir(parents=True, exist_ok=True)
    return f"Successfully made directory {dir_path}"

@tool
def delete_dir(dir_name: str) -> str:
    """Delete a directory."""
    dir_path = BASE_DIR / dir_name
    if not dir_path.exists():
        return f"Error: The directory {dir_path} does not exist."
    try:
        dir_path.rmdir()
        return f"Successfully deleted {dir_path}"
    except OSError:
        return f"Error: Directory {dir_path} is not empty."

@tool
def list_dir(dir_name: str) -> str:
    """List all files in a directory."""
    dir_path = BASE_DIR / dir_name
    if not dir_path.exists():
        return f"Error: The directory {dir_path} does not exist."
    files = [f.name for f in dir_path.iterdir()]
    return "\n".join(files)

@tool
def run_terminal_command(command: str) -> str:
    """
    Run a terminal command.
    Use this to create directories, install dependencies, run tests, etc.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout
        if result.stderr:
            output += f"\nError Output:\n{result.stderr}"
        return output if output.strip() else "Command executed successfully (no output)."
    except Exception as e:
        return f"Error executing command: {e}"

@tool
def web_search(query: str) -> str:
    """
    Search the web for documentation, solutions, or information.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        return "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    except Exception as e:
        return f"Error searching web: {e}"

@tool
def create_plan(plan_name: str, steps: str) -> str:
    """
    Create a structured plan file (e.g., plan.md).
    steps: A newline-separated list of steps.
    """
    file_path = BASE_DIR / plan_name
    content = f"# Plan: {plan_name}\n\n"
    for step in steps.split("\n"):
        if step.strip():
            content += f"- [ ] {step.strip()}\n"
    
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Successfully created plan at {file_path}"

@tool
def update_plan(plan_name: str, step_index: int, status: str) -> str:
    """
    Update a step in the plan.
    step_index: 0-based index of the step to update.
    status: 'done' (turns [ ] into [x]) or 'pending' (turns [x] into [ ]).
    """
    file_path = BASE_DIR / plan_name
    if not file_path.exists():
        return f"Error: Plan {file_path} does not exist."
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    step_count = 0
    new_lines = []
    updated = False
    
    for line in lines:
        if line.strip().startswith("- ["):
            if step_count == step_index:
                if status == 'done':
                    line = line.replace("- [ ]", "- [x]")
                elif status == 'pending':
                    line = line.replace("- [x]", "- [ ]")
                updated = True
            step_count += 1
        new_lines.append(line)
        
    if not updated:
        return f"Error: Step index {step_index} not found or invalid."
        
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    return f"Successfully updated step {step_index} to {status}"


