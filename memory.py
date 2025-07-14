import json
from typing import Optional, Dict, Any, List
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from config import CONVERSATION_FILE

class PersistentMemory:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.user_name: Optional[str] = None
        self.load_memory()

    def load_memory(self):
        try:
            with open(CONVERSATION_FILE, 'r') as f:
                data = json.load(f)
                self.user_name = data.get('user_name')
                for m in data.get("conversations", []):
                    if m["type"] == "human":
                        self.memory.chat_memory.add_user_message(m["content"])
                    elif m["type"] == "ai":
                        self.memory.chat_memory.add_ai_message(m["content"])
        except FileNotFoundError:
            pass

    def save_memory(self):
        conv = []
        for m in self.memory.chat_memory.messages:
            role = "human" if isinstance(m, HumanMessage) else "ai"
            conv.append({"type": role, "content": m.content})
        json.dump({"user_name": self.user_name, "conversations": conv}, open(CONVERSATION_FILE, "w"), indent=2)

    def add_message(self, message: str, is_human=True):
        if is_human:
            self.memory.chat_memory.add_user_message(message)
        else:
            self.memory.chat_memory.add_ai_message(message)
        self.save_memory()

    def get_context(self):
        context = f"The user's name is {self.user_name}. " if self.user_name else ""
        messages = self.memory.chat_memory.messages[-6:]
        for m in messages:
            prefix = "User" if isinstance(m, HumanMessage) else "Assistant"
            context += f"\n{prefix}: {m.content}"
        return context

    def set_user_name(self, name: str): self.user_name = name; self.save_memory()
    def get_user_name(self) -> Optional[str]: return self.user_name
    def clear_memory(self): self.memory.clear(); self.user_name = None; self.save_memory()
    def get_full_history(self) -> List[Dict[str, str]]:
        return [{"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
                for m in self.memory.chat_memory.messages]
