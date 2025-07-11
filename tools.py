import json
from typing import List, Dict, Any
from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
from config import TODOS_FILE


class TodoInput(BaseModel):
    """Input for todo operations."""
    task: str = Field(description="The todo task description")


class TodoRemoveInput(BaseModel):
    """Input for removing todos."""
    task_or_index: str = Field(description="The task description or index number to remove")


def load_todos() -> List[str]:
    """Load todos from JSON file."""
    try:
        with open(TODOS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('todos', [])
    except FileNotFoundError:
        return []


def save_todos(todos: List[str]) -> None:
    """Save todos to JSON file."""
    with open(TODOS_FILE, 'w') as f:
        json.dump({'todos': todos}, f, indent=2)


def add_todo(task: str) -> str:
    """Add a new todo item."""
    todos = load_todos()
    todos.append(task)
    save_todos(todos)
    return f"Added '{task}' to your to-do list!"


def list_todos() -> str:
    """List all todo items."""
    todos = load_todos()
    if not todos:
        return "Your to-do list is empty!"
    
    todo_list = "\n".join([f"{i+1}. {todo}" for i, todo in enumerate(todos)])
    return f"Here's your current to-do list:\n{todo_list}"


def remove_todo(task_or_index: str) -> str:
    """Remove a todo item by task name or index."""
    todos = load_todos()
    if not todos:
        return "Your to-do list is empty!"
    
    # Try to remove by index first
    try:
        index = int(task_or_index) - 1  # Convert to 0-based index
        if 0 <= index < len(todos):
            removed_task = todos.pop(index)
            save_todos(todos)
            return f"Removed '{removed_task}' from your to-do list!"
        else:
            return f"Invalid index. Please use a number between 1 and {len(todos)}."
    except ValueError:
        # If not a number, try to remove by task name
        task_lower = task_or_index.lower()
        for i, todo in enumerate(todos):
            if task_lower in todo.lower():
                removed_task = todos.pop(i)
                save_todos(todos)
                return f"Removed '{removed_task}' from your to-do list!"
        
        return f"Task '{task_or_index}' not found in your to-do list."


def clear_todos() -> str:
    """Clear all todo items."""
    save_todos([])
    return "Cleared all items from your to-do list!"


# Create LangChain tools
def create_todo_tools() -> List[Tool]:
    """Create and return all todo tools."""
    return [
        Tool(
            name="add_todo",
            description="Add a new item to the user's to-do list",
            func=add_todo,
            args_schema=TodoInput
        ),
        Tool(
            name="list_todos",
            description="Show all items in the user's to-do list",
            func=lambda x: list_todos()  # Wrapper since list_todos takes no args
        ),
        Tool(
            name="remove_todo", 
            description="Remove an item from the user's to-do list by task name or index number",
            func=remove_todo,
            args_schema=TodoRemoveInput
        ),
        Tool(
            name="clear_todos",
            description="Clear all items from the user's to-do list",
            func=lambda x: clear_todos()
        )
    ]