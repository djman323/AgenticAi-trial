import os
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
