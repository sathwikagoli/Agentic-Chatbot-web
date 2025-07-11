import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# File paths
TODOS_FILE = "data/todos.json"
CONVERSATION_FILE = "data/conversation_history.json"

# Model settings
MODEL_NAME = "gemini-2.0-flash"  # Updated from "gemini-pro"
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Agent settings
AGENT_NAME = "TodoBot"
AGENT_DESCRIPTION = "A helpful assistant that manages conversations and to-do lists"