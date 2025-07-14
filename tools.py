import json
from typing import List
from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
from config import TODOS_FILE

class TodoInput(BaseModel):
    task: str = Field(description="The task to add")

class TodoRemoveInput(BaseModel):
    task_or_index: str = Field(description="Task or index to remove")

def load_todos() -> List[str]:
    try:
        with open(TODOS_FILE, "r") as f:
            return json.load(f).get("todos", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_todos(todos: List[str]) -> None:
    with open(TODOS_FILE, "w") as f:
        json.dump({"todos": todos}, f, indent=2)

def add_todo(task: str) -> str:
    todos = load_todos()
    todos.append(task)
    save_todos(todos)
    return f"Added '{task}' to your to-do list."

def list_todos(_: str = "") -> str:
    todos = load_todos()
    if not todos:
        return "Your to-do list is empty."
    return "Here are your to-dos:\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(todos))

def remove_todo(task_or_index: str) -> str:
    todos = load_todos()
    if not todos:
        return "Your to-do list is empty."

    # Try by index
    try:
        index = int(task_or_index) - 1
        if 0 <= index < len(todos):
            removed = todos.pop(index)
            save_todos(todos)
            return f"Removed '{removed}' from your to-do list."
    except ValueError:
        pass

    # Try by name (partial match)
    for i, task in enumerate(todos):
        if task_or_index.lower() in task.lower():
            removed = todos.pop(i)
            save_todos(todos)
            return f"Removed '{removed}' from your to-do list."

    return f"Task '{task_or_index}' not found in your to-do list."

def clear_todos(_: str = "") -> str:
    save_todos([])
    return "Cleared all items from your to-do list."

def create_todo_tools() -> List[Tool]:
    return [
        Tool(
            name="add_todo",
            func=add_todo,
            description="Add a new item to the user's to-do list",
            args_schema=TodoInput
        ),
        Tool(
            name="list_todos",
            func=list_todos,
            description="List all items in the user's to-do list"
        ),
        Tool(
            name="remove_todo",
            func=remove_todo,
            description="Remove an item from the user's to-do list by task name or index number",
            args_schema=TodoRemoveInput
        ),
        Tool(
            name="clear_todos",
            func=clear_todos,
            description="Clear all items from the user's to-do list"
        )
    ]
