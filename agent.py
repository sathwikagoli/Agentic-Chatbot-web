import re
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from tools import create_todo_tools
from memory import PersistentMemory
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS


class TodoAgent:
    """Main agent class that orchestrates everything."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        self.memory = PersistentMemory()
        self.tools = create_todo_tools()
        self.agent_executor = self._create_agent()
    
    def _create_agent_prompt(self) -> PromptTemplate:
        """Create the agent prompt template."""
        template = """You are a helpful assistant that manages conversations and to-do lists.

IMPORTANT INSTRUCTIONS:
1. Always be friendly and conversational
2. Remember the user's name if they tell you
3. Use the provided tools to manage their to-do list
4. Keep track of conversation context
5. When someone introduces themselves, remember their name for future interactions

AVAILABLE TOOLS:
{tools}

Tool names: {tool_names}

CONVERSATION CONTEXT:
{context}

TOOL USAGE FORMAT:
To use a tool, use this exact format:
Thought: I need to [what you want to do]
Action: [tool_name]
Action Input: [input for the tool]
Observation: [result from tool]
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: [your response to the user]

If you don't need to use any tools, you can respond directly.

CURRENT CONVERSATION:
Human: {input}
{agent_scratchpad}

Remember: Always be helpful, friendly, and use the tools when needed to manage the to-do list!"""
        
        return PromptTemplate(
            input_variables=["tools", "tool_names", "context", "input", "agent_scratchpad"],
            template=template
        )
    
    def _create_agent(self) -> AgentExecutor:
        """Create the ReAct agent with tools."""
        prompt = self._create_agent_prompt()
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def _extract_name_from_message(self, message: str) -> str:
        """Extract name from user message."""
        # Simple name extraction patterns
        patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"this is (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).capitalize()
        return None
    
    def chat(self, user_input: str) -> str:
        """Main chat method."""
        try:
            # Check if user is introducing themselves
            extracted_name = self._extract_name_from_message(user_input)
            if extracted_name and not self.memory.get_user_name():
                self.memory.set_user_name(extracted_name)
            
            # Add user message to memory
            self.memory.add_message(user_input, is_human=True)
            
            # Get context for the agent
            context = self.memory.get_context()
            
            # Prepare input for agent
            agent_input = {
                "input": user_input,
                "context": context,
                "tools": "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
            
            # Get response from agent
            response = self.agent_executor.invoke(agent_input)
            agent_response = response.get("output", "I'm sorry, I couldn't process that request.")
            
            # Add agent response to memory
            self.memory.add_message(agent_response, is_human=False)
            
            return agent_response
            
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Please try again."
            self.memory.add_message(error_msg, is_human=False)
            return error_msg
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get full conversation history."""
        return self.memory.get_full_history()
    
    def clear_conversation(self) -> str:
        """Clear conversation history."""
        self.memory.clear_memory()
        return "Conversation history cleared!"
    
    def get_user_name(self) -> str:
        """Get the user's name."""
        name = self.memory.get_user_name()
        return name if name else "there"