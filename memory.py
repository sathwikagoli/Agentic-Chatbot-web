import json
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from config import CONVERSATION_FILE


class PersistentMemory:
    """Memory management with persistence."""
    
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.user_name: Optional[str] = None
        self.load_memory()
    
    def load_memory(self) -> None:
        """Load conversation history from file."""
        try:
            with open(CONVERSATION_FILE, 'r') as f:
                data = json.load(f)
                self.user_name = data.get('user_name')
                conversations = data.get('conversations', [])
                
                # Restore messages to memory
                for conv in conversations:
                    if conv['type'] == 'human':
                        self.memory.chat_memory.add_user_message(conv['content'])
                    elif conv['type'] == 'ai':
                        self.memory.chat_memory.add_ai_message(conv['content'])
        except FileNotFoundError:
            # File doesn't exist yet, start with empty memory
            pass
    
    def save_memory(self) -> None:
        """Save conversation history to file."""
        conversations = []
        
        # Convert messages to serializable format
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                conversations.append({
                    'type': 'human',
                    'content': message.content
                })
            elif isinstance(message, AIMessage):
                conversations.append({
                    'type': 'ai',
                    'content': message.content
                })
        
        data = {
            'user_name': self.user_name,
            'conversations': conversations
        }
        
        with open(CONVERSATION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_message(self, message: str, is_human: bool = True) -> None:
        """Add a message to memory and save."""
        if is_human:
            self.memory.chat_memory.add_user_message(message)
        else:
            self.memory.chat_memory.add_ai_message(message)
        self.save_memory()
    
    def get_context(self) -> str:
        """Get conversation context for the agent."""
        context = ""
        if self.user_name:
            context += f"The user's name is {self.user_name}. "
        
        # Get recent conversation history
        messages = self.memory.chat_memory.messages[-6:]  # Last 6 messages
        if messages:
            context += "Recent conversation:\n"
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    context += f"User: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    context += f"Assistant: {msg.content}\n"
        
        return context
    
    def set_user_name(self, name: str) -> None:
        """Set and save the user's name."""
        self.user_name = name
        self.save_memory()
    
    def get_user_name(self) -> Optional[str]:
        """Get the user's name."""
        return self.user_name
    
    def clear_memory(self) -> None:
        """Clear all memory."""
        self.memory.clear()
        self.user_name = None
        self.save_memory()
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for the agent."""
        return self.memory.load_memory_variables({})
    
    def get_full_history(self) -> List[Dict[str, str]]:
        """Get full conversation history."""
        history = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                history.append({'role': 'user', 'content': message.content})
            elif isinstance(message, AIMessage):
                history.append({'role': 'assistant', 'content': message.content})
        return history