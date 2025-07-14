import streamlit as st
from agent import TodoAgent

# Page settings
st.set_page_config(page_title="TodoBot", page_icon="🤖", layout="centered")

# Debug: Confirm Streamlit is working
st.title("🤖 TodoBot - Your Personal Assistant")
st.markdown("Welcome to your AI-powered to-do manager and chatbot!")

# Initialize agent only once
if "agent" not in st.session_state:
    try:
        st.session_state.agent = TodoAgent()
        st.success("✅ Agent initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize agent: {e}")
        st.stop()

# Setup conversation state
if "messages" not in st.session_state:
    st.session_state.messages = []
    user_name = st.session_state.agent.get_user_name()
    greeting = f"👋 Welcome back, {user_name}!" if user_name else "👋 Hello! I'm TodoBot. What's your name?"
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Sidebar with clear/reset
with st.sidebar:
    st.header("🔧 Settings")
    if st.button("🧹 Clear Chat"):
        st.session_state.agent.clear_conversation()
        st.session_state.messages = []
        st.experimental_rerun()

    st.markdown("### 💡 Example Prompts")
    st.markdown("""
- Add 'Buy milk' to my to-do list  
- List my todos  
- Remove 'Buy milk'  
- Clear my todo list  
- My name is Alice  
""")

# Show conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input from user
user_input = st.chat_input("Type your message here...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = st.session_state.agent.chat(user_input)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"❌ Agent failed: {e}")
