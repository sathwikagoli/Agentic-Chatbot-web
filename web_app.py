import streamlit as st
from agent import TodoAgent
from tools import load_todos

# Page settings
st.set_page_config(
    page_title="TodoBot", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .todo-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #4caf50;
        color: #333333 !important;
        font-weight: 500;
    }
    
    .todo-item:hover {
        background-color: #e9ecef;
        transform: translateX(2px);
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🤖 TodoBot</h1><p>Your AI-powered personal assistant</p></div>', 
            unsafe_allow_html=True)

# Initialize agent
if "agent" not in st.session_state:
    try:
        with st.spinner("Initializing TodoBot..."):
            st.session_state.agent = TodoAgent()
        st.success("✅ TodoBot is ready!")
    except Exception as e:
        st.error(f"❌ Failed to initialize TodoBot: {e}")
        st.error("Please check your .env file and ensure GOOGLE_API_KEY is set.")
        st.stop()

# Initialize messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    user_name = st.session_state.agent.get_user_name()
    if user_name and user_name != "there":
        greeting = f"👋 Welcome back, {user_name}! How can I help you today?"
    else:
        greeting = "👋 Hello! I'm TodoBot, your personal AI assistant. What's your name?"
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Sidebar
with st.sidebar:
    st.header("🛠️ Controls")
    
    # User info
    user_name = st.session_state.agent.get_user_name()
    if user_name and user_name != "there":
        st.info(f"👤 User: {user_name}")
    
    # Clear conversation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.agent.clear_conversation()
            st.session_state.messages = []
            st.success("Chat cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Current todos display with auto-refresh
    st.header("📋 Current To-Dos")
    
    # Force refresh todos on every interaction
    if 'todo_refresh' not in st.session_state:
        st.session_state.todo_refresh = 0
    
    try:
        todos = load_todos()
        if todos:
            st.write(f"**Total: {len(todos)} items**")
            for i, todo in enumerate(todos, 1):
                st.markdown(f'<div class="todo-item" style="color: #333333 !important;">{i}. {todo}</div>', 
                          unsafe_allow_html=True)
        else:
            st.info("📝 No todos yet!")
    except Exception as e:
        st.error(f"Error loading todos: {e}")
    
    # Auto-refresh button
    if st.button("🔄 Refresh Todos", use_container_width=True):
        st.session_state.todo_refresh += 1
        st.rerun()
    
    # Quick commands
    st.header("💡 Quick Commands")
    quick_commands = [
        "Add 'Buy groceries' to my list",
        "List my todos",
        "Remove 'Buy groceries'",
        "Clear my todo list"
    ]
    
    for cmd in quick_commands:
        if st.button(f"💬 {cmd}", use_container_width=True):
            st.session_state.quick_command = cmd
            st.rerun()

# Handle quick commands
if hasattr(st.session_state, 'quick_command'):
    user_input = st.session_state.quick_command
    delattr(st.session_state, 'quick_command')
    
    # Add to messages and process
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Processing..."):
        try:
            response = st.session_state.agent.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            # Force todo refresh after any interaction
            st.session_state.todo_refresh = st.session_state.get('todo_refresh', 0) + 1
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.rerun()

# Main chat area
st.header("💬 Chat")

# Display conversation
chat_container = st.container()
with chat_container:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here... (e.g., 'Add buy milk to my list')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.chat(prompt)
                st.markdown(response)
                
                # Add to message history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Force todo refresh after any interaction
                st.session_state.todo_refresh = st.session_state.get('todo_refresh', 0) + 1
                
            except Exception as e:
                error_msg = f"❌ I apologize, but I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8em;">'
    'TodoBot - Built with LangChain, Streamlit, and Google Gemini'
    '</div>', 
    unsafe_allow_html=True
)