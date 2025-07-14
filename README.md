#  Agentic ChatBot - AI-Powered Personal Assistant

An intelligent conversational agent built with LangChain and Google Gemini that manages conversations and to-do lists through natural language interactions.(Todo Bot)

##  Project Overview

TodoBot is an agentic AI system that demonstrates core AI agent capabilities:
- **Conversational Memory**: Remembers user names and conversation history
- **Tool Integration**: Seamlessly executes to-do list operations via LLM function calls
- **Persistent Storage**: Maintains state across sessions
- **Natural Language Interface**: Intuitive conversational interactions

##  Architecture

### System Architecture Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit UI   │───▶│   TodoAgent     │───▶│  LLM (Gemini)   │
│  (User Input)   │    │   (Orchestrator)│    │  (Reasoning)    │
│ - Chat Interface│    │ - Prompt Mgmt   │    │ - Tool Selection│
│ - Session State │    │ - Error Handler │    │ - Param Extract │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                        │
        ▼                       ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Real-time UI    │    │ Context Builder │    │ Tool Execution  │
│ Updates         │◀───│ (History +      │    │ (Todo Operations)│
│ - Todo Sidebar  │    │  User Context)  │    │ - CRUD Ops      │
│ - Chat History  │    │                 │    │ - Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                        │
        ▼                       ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ User Experience │    │ Memory System   │    │ File Storage    │
│ - Visual Feedback│    │ (Conversation   │    │ (JSON Files)    │
│ - Error Messages│    │  & User Data)   │    │ - todos.json    │
│ - Loading States│    │                 │    │ - conversation  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

```
TodoBot System
├──  Agent Core (agent.py)
│   ├── LLM Integration (Gemini 2.0 Flash)
│   ├── Prompt Engineering & Context Management
│   ├── Tool Orchestration (LangChain AgentExecutor)
│   └── Response Processing & Error Handling
│
├──  Tool System (tools.py)
│   ├── add_todo() - Add tasks with duplicate checking
│   ├── list_todos() - Display formatted task lists
│   ├── remove_todo() - Remove by name/index with fuzzy matching
│   └── clear_todos() - Bulk task removal
│
├──  Memory System (memory.py)
│   ├── ConversationBufferMemory (LangChain)
│   ├── Persistent JSON Storage
│   ├── User Context Management
│   └── Session State Handling
│
├──  Interface Layer (web_app.py)
│   ├── Streamlit Web Framework
│   ├── Real-time Chat Interface (st.chat_message, st.chat_input)
│   ├── Live Todo Display with Auto-refresh
│   ├── Session State Management (st.session_state)
│   ├── Interactive Controls & Quick Commands
│   └── Responsive Design with Custom CSS
│
└──  Configuration (config.py)
    ├── API Keys & Model Settings
    ├── File Paths & Storage Config
    └── Agent Parameters
```

##  Memory Management

### Storage Architecture

**Conversation Memory:**
- **Storage**: `data/conversation_history.json`
- **Structure**: 
  ```json
  {
    "user_name": "John",
    "conversations": [
      {"type": "human", "content": "Hello!"},
      {"type": "ai", "content": "Hi John! How can I help?"}
    ]
  }
  ```

**Todo Storage:**
- **Storage**: `data/todos.json`
- **Structure**: 
  ```json
  {
    "todos": [
      "Buy groceries",
      "Finish project",
      "Call dentist"
    ]
  }
  ```
- **Persistence**: Immediate save after each modification
- **Concurrency**: File-based locking prevents corruption

### Memory Retrieval Process

1. **Agent Initialization**: Loads existing conversation history and user data
2. **Context Building**: Combines user name + recent conversation history
3. **Dynamic Context**: Updates context window with each interaction
4. **Persistent Updates**: Saves state after every user interaction

##  Tool System

### Tool Registration Process

```python
# 1. Tool Definition with Pydantic Schemas
class TodoInput(BaseModel):
    task: str = Field(description="The task to add to the to-do list")

# 2. Function Implementation
def add_todo(task: str) -> str:
    # Business logic with error handling
    todos = load_todos()
    if task.lower() in [t.lower() for t in todos]:
        return f"Task '{task}' already exists"
    todos.append(task)
    save_todos(todos)
    return f" Added '{task}' to your to-do list"

# 3. Tool Registration with LangChain
Tool(
    name="add_todo",
    func=add_todo,
    description="Add a new task to the user's to-do list. Input should be the task description.",
    args_schema=TodoInput
)

# 4. LLM Binding
llm_with_tools = llm.bind_tools(tools)
```

### Available Tools

| Tool | Function | Input Schema | Error Handling |
|------|----------|--------------|----------------|
| `add_todo` | Add new tasks | `TodoInput(task: str)` | Duplicate detection, validation |
| `list_todos` | Display all tasks | No input required | Empty list handling |
| `remove_todo` | Remove by name/index | `TodoRemoveInput(task_or_index: str)` | Fuzzy matching, partial matches |
| `clear_todos` | Remove all tasks | No input required | Confirmation messaging |

### Tool Execution Flow

1. **User Input**: Natural language request
2. **LLM Analysis**: Gemini determines required tool(s)
3. **Parameter Extraction**: LLM extracts structured parameters
4. **Tool Invocation**: Agent executes function with parameters
5. **Result Processing**: Tool returns formatted response
6. **Response Generation**: LLM formulates natural language response

##  Setup Instructions

### Prerequisites

- Python 3.8+
- Google AI Studio API Key

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/sathwikagoli/Agentic-Chatbot-web
   cd to-project-directory
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

4. **Create Data Directory**
   ```bash
   mkdir data
   ```

### Running the Application

**Web Interface (Recommended):**
```bash
python web_app.py
```
*This launches the Streamlit web interface automatically*

**CLI Interface:**
```bash
python main.py
```
*This starts the command-line interface for terminal-based interaction*

**Alternative Web Interface Launch:**
```bash
streamlit run web_app.py
```

**Web Interface with Custom Port:**
```bash
streamlit run web_app.py --server.port 8501
```

## Usage Examples

### Basic Conversation
```
User: Hi, I'm Sarah
Bot: Hello Sarah! Nice to meet you. How can I help you today?

User: Add "Buy groceries" to my todo list
Bot:  Added 'Buy groceries' to your to-do list.

User: What's on my list?
Bot:  Here are your current to-dos:
     1. Buy groceries
```

### Advanced Todo Management
```
User: Add these tasks: finish project, call dentist, book flight
Bot: I'll add those tasks for you one by one:
      Added 'finish project' to your to-do list.
      Added 'call dentist' to your to-do list.
      Added 'book flight' to your to-do list.

User: Remove the first task
Bot:  Removed 'finish project' from your to-do list.

User: Show my updated list
Bot:  Here are your current to-dos:
     1. call dentist
     2. book flight
```

### Context-Aware Responses
```
User: I completed the dentist appointment
Bot: That's great, Sarah! I'm glad you got that taken care of. 
     Would you like me to remove "call dentist" from your to-do list?

User: Yes please
Bot:  Removed 'call dentist' from your to-do list.
```

##  Web Interface Features

### Core Features
- **Real-time Chat**: Instant messaging with typing indicators
- **Live Todo Display**: Sidebar shows current todos with auto-refresh
- **Quick Commands**: One-click common actions
- **Responsive Design**: Works on desktop and mobile
- **Persistent Sessions**: Maintains state across browser sessions

### Enhanced UX Elements
- **Visual Feedback**: Success/error messages with icons
- **Loading States**: Spinner animations during processing
- **Gradient Design**: Modern, professional appearance
- **Keyboard Shortcuts**: Enter to send, etc.

##  Performance Optimizations

### Memory Management
- **Context Window**: Limited to last 6 messages for efficient processing
- **Lazy Loading**: Todos loaded only when needed
- **Caching**: Streamlit session state for responsive UI

### Token Optimization
- **Efficient Prompts**: Concise system prompts with clear instructions
- **Smart Context**: Only relevant history included in LLM calls
- **Tool Descriptions**: Optimized for accurate function calling

##  Current Limitations

1. **Storage Scalability**: File-based storage; may need database for large datasets
2. **Concurrency**: Single-user design; needs multi-user session management
3. **Context Length**: Limited conversation history for cost optimization
4. **Tool Complexity**: Simple CRUD operations; could expand to complex workflows
5. **Error Recovery**: Basic error handling; needs more sophisticated retry logic

##  Future Improvements

### Short-term Enhancements
- **Database Integration**: PostgreSQL/SQLite for better scalability
- **User Authentication**: Multi-user support with secure login
- **Rich Media Support**: Image uploads, voice notes, file attachments
- **Export Features**: PDF/CSV export for todos and chat history

### Technical Improvements
- **Vector Storage**: Semantic search using embeddings (ChromaDB/Pinecone)
- **Async Processing**: Non-blocking operations for better performance
- **Monitoring**: Logging, metrics, and health checks

## 📋 Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | Google Gemini 2.0 Flash | Natural language processing |
| **Framework** | LangChain | Agent orchestration & tool management |
| **Backend** | Python 3.8+ | Core application logic |
| **Frontend** | Streamlit | Web interface |
| **Storage** | JSON Files | Persistent data storage |
| **Memory** | ConversationBufferMemory | Conversation state management |
| **Validation** | Pydantic | Data validation & schemas |

##  Code Quality

- **Type Hints**: Full type annotation for better maintainability
- **Error Handling**: Comprehensive exception management
- **Documentation**: Detailed docstrings and inline comments
- **Modular Design**: Separation of concerns across multiple files
- **Configuration Management**: Centralized settings in config.py

##  Support

For issues or questions:
1. Check the error messages in the console
2. Verify your `.env` file contains a valid `GOOGLE_API_KEY`
3. Ensure all dependencies are installed correctly
4. Review the logs for detailed error information

---
