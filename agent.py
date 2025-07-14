import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
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
        self.agent_executor = self._create_agent()

    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "context", "input", "agent_scratchpad"],
            template="""
You are TodoBot, a helpful assistant that manages conversations and to-do lists.

### RULES ###
- ALWAYS use tools to read or update the to-do list.
- NEVER fabricate to-do list content without calling a tool.
- STRICTLY follow this format:

Thought: [your reasoning]
Action: [tool name]
Action Input: [tool input]
Observation: [result from tool]

You can repeat the above as needed, but when you're done:

Thought: I now know the final answer.
Final Answer: [reply to user]

TOOLS:
{tools}

TOOL NAMES:
{tool_names}

CONTEXT:
{context}

USER INPUT:
Human: {input}
{agent_scratchpad}
"""
        )
        agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

    def _extract_name(self, message: str) -> str:
        # More flexible name matching
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
        name = self._extract_name(user_input)
        if name and not self.memory.get_user_name():
            self.memory.set_user_name(name)

        self.memory.add_message(user_input, is_human=True)
        context = self.memory.get_context()
        inputs = {
            "input": user_input,
            "context": context,
            "tools": "\n".join(f"- {t.name}: {t.description}" for t in self.tools),
            "tool_names": ", ".join(t.name for t in self.tools)
        }

        try:
            response = self.agent_executor.invoke(inputs)
            answer = response.get("output", "Sorry, I couldn't process that.")
        except Exception as e:
            answer = f"⚠️ Agent error: {e}"

        self.memory.add_message(answer, is_human=False)
        return answer

    def get_user_name(self) -> str:
        return self.memory.get_user_name() or "there"

    def clear_conversation(self) -> str:
        self.memory.clear_memory()
        return "Conversation cleared."
