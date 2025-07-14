import json
import os
from typing import List
from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
from config import TODOS_FILE

# Ensure data directory exists
os.makedirs(os.path.dirname(TODOS_FILE), exist_ok=True)

class TodoInput(BaseModel):
    task: str = Field(description="The task to add to the to-do list")

class TodoRemoveInput(BaseModel):
    task_or_index: str = Field(description="Task name or index number to remove")

def load_todos() -> List[str]:
    """Load todos from file"""
    try:
        with open(TODOS_FILE, "r") as f:
            return json.load(f).get("todos", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_todos(todos: List[str]) -> None:
    """Save todos to file"""
    os.makedirs(os.path.dirname(TODOS_FILE), exist_ok=True)
    with open(TODOS_FILE, "w") as f:
        json.dump({"todos": todos}, f, indent=2)

def add_todo(task: str) -> str:
    """Add a new task to the to-do list"""
    task = task.strip()
    if not task:
        return "Please provide a task to add."
    
    todos = load_todos()
    
    # Check for duplicates (case-insensitive)
    for existing_task in todos:
        if existing_task.lower() == task.lower():
            return f"Task '{task}' already exists in your to-do list."
    
    todos.append(task)
    save_todos(todos)
    return f"✅ Added '{task}' to your to-do list."

def list_todos(_: str = "") -> str:
    """List all tasks in the to-do list"""
    todos = load_todos()
    if not todos:
        return "📝 Your to-do list is empty."
    
    todo_list = "\n".join(f"{i+1}. {task}" for i, task in enumerate(todos))
    return f"📋 Here are your current to-dos:\n{todo_list}"

def remove_todo(task_or_index: str) -> str:
    """Remove a task from the to-do list by name or index"""
    todos = load_todos()
    if not todos:
        return "📝 Your to-do list is empty."

    task_or_index = task_or_index.strip()
    
    # Try by index first
    try:
        index = int(task_or_index) - 1
        if 0 <= index < len(todos):
            removed_task = todos.pop(index)
            save_todos(todos)
            return f"✅ Removed '{removed_task}' from your to-do list."
        else:
            return f"❌ Index {task_or_index} is out of range. You have {len(todos)} tasks."
    except ValueError:
        pass

    # Try by exact name match first
    for i, task in enumerate(todos):
        if task.lower() == task_or_index.lower():
            removed_task = todos.pop(i)
            save_todos(todos)
            return f"✅ Removed '{removed_task}' from your to-do list."
    
    # Try by partial name match
    matches = []
    for i, task in enumerate(todos):
        if task_or_index.lower() in task.lower():
            matches.append((i, task))
    
    if len(matches) == 1:
        i, task = matches[0]
        removed_task = todos.pop(i)
        save_todos(todos)
        return f"✅ Removed '{removed_task}' from your to-do list."
    elif len(matches) > 1:
        match_list = "\n".join(f"{i+1}. {task}" for i, task in matches)
        return f"❌ Multiple tasks match '{task_or_index}':\n{match_list}\nPlease be more specific."
    
    return f"❌ Task '{task_or_index}' not found in your to-do list."

def clear_todos(_: str = "") -> str:
    """Clear all tasks from the to-do list"""
    todos = load_todos()
    if not todos:
        return "📝 Your to-do list is already empty."
    
    save_todos([])
    return "🗑️ Cleared all tasks from your to-do list."

def create_todo_tools() -> List[Tool]:
    """Create and return all todo management tools"""
    return [
        Tool(
            name="add_todo",
            func=add_todo,
            description="Add a new task to the user's to-do list. Input should be the task description.",
            args_schema=TodoInput
        ),
        Tool(
            name="list_todos",
            func=list_todos,
            description="Display all tasks in the user's to-do list. No input required."
        ),
        Tool(
            name="remove_todo",
            func=remove_todo,
            description="Remove a task from the user's to-do list. Input can be the task name or index number.",
            args_schema=TodoRemoveInput
        ),
        Tool(
            name="clear_todos",
            func=clear_todos,
            description="Remove all tasks from the user's to-do list. No input required."
        )
    ]
