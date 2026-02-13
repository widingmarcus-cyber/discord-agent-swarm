"""
Basic tools for agents.

Add your own tools by creating new functions with the @tool decorator.
Register them in your agent's YAML config under 'tools:'.
"""

import subprocess
import logging
from datetime import datetime
from typing import Callable

logger = logging.getLogger(__name__)

# Tool registry
_tools: dict[str, Callable] = {}


def tool(name: str = None, description: str = ""):
    """Decorator to register a function as an agent tool."""
    def decorator(func):
        tool_name = name or func.__name__
        func._tool_name = tool_name
        func._tool_description = description or func.__doc__ or ""
        _tools[tool_name] = func
        return func
    return decorator


def get_tool(name: str) -> Callable:
    """Get a registered tool by name."""
    if name not in _tools:
        raise ValueError(f"Unknown tool: {name}. Available: {list(_tools.keys())}")
    return _tools[name]


def list_tools() -> list[dict]:
    """List all registered tools."""
    return [
        {"name": name, "description": func._tool_description}
        for name, func in _tools.items()
    ]


# --- Built-in tools ---


@tool(description="Get the current date and time")
def current_time() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool(description="Read the contents of a file from the memory directory")
def read_file(path: str) -> str:
    """Read a file from the memory/ directory."""
    from core.memory import MemoryManager
    manager = MemoryManager()
    return manager.read_file(path)


@tool(description="Write content to a file in the memory directory")
def write_file(path: str, content: str) -> str:
    """Write content to a file in the memory/ directory."""
    from core.memory import MemoryManager
    manager = MemoryManager()
    manager.write_file(path, content)
    return f"Written to {path}"


@tool(description="Execute a shell command (use with caution)")
def shell(command: str) -> str:
    """Execute a shell command and return output. Timeout: 30s."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        return output[:2000]  # Limit output size
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except Exception as e:
        return f"Error: {e}"
