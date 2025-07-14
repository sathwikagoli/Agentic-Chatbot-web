import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from tools import create_todo_tools
from memory import PersistentMemory
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS

class TodoAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        self.memory = PersistentMemory()
        self.tools = create_todo_tools()
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.agent_executor = self._create_agent()

    def _create_agent(self):
        """Create agent with better prompt and tool handling"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are TodoBot, a helpful assistant that manages conversations and to-do lists.

PERSONALITY:
- Be friendly, conversational, and helpful
- Remember the user's name and context from previous messages
- Use tools when needed to manage the to-do list
- Always use tools to read or update the to-do list - never guess the contents

CONTEXT:
{context}

When the user asks about todos, ALWAYS use the list_todos tool first to get current state.
When adding/removing todos, use the appropriate tools and confirm the action.
Be conversational and natural in your responses."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = (
            {
                "input": lambda x: x["input"],
                "context": lambda x: x["context"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x.get("chat_history", []),
            }
            | prompt
            | self.llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate"
        )

    def _extract_name(self, message: str) -> str:
        """Extract name from user message"""
        patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"i'm (\w+)",
            r"call me (\w+)",
            r"this is (\w+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).capitalize()
        return None

    def chat(self, user_input: str) -> str:
        """Main chat method with improved error handling"""
        # Extract and store name if provided
        name = self._extract_name(user_input)
        if name and not self.memory.get_user_name():
            self.memory.set_user_name(name)

        # Add to memory
        self.memory.add_message(user_input, is_human=True)
        
        # Get context
        context = self.memory.get_context()
        
        # Prepare inputs
        inputs = {
            "input": user_input,
            "context": context,
            "chat_history": self.memory.memory.chat_memory.messages[-4:],  # Last 4 messages
        }

        try:
            # Get response from agent
            response = self.agent_executor.invoke(inputs)
            answer = response.get("output", "Sorry, I couldn't process that.")
            
            # Clean up response
            answer = self._clean_response(answer)
            
        except Exception as e:
            print(f"Agent error: {e}")
            answer = "I apologize, but I encountered an error. Please try again."

        # Add response to memory
        self.memory.add_message(answer, is_human=False)
        return answer

    def _clean_response(self, response: str) -> str:
        """Clean up agent response"""
        # Remove any remaining agent scratchpad artifacts
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that look like agent artifacts
            if any(marker in line.lower() for marker in ['thought:', 'action:', 'observation:', 'final answer:']):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def get_user_name(self) -> str:
        return self.memory.get_user_name() or "there"

    def clear_conversation(self) -> str:
        self.memory.clear_memory()
        return "Conversation cleared! How can I help you today?"