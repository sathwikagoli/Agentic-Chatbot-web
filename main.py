import sys
import os
from agent import TodoAgent
from config import GOOGLE_API_KEY

def run_cli():
    """Run the CLI version of the chatbot."""
    print("🤖 TodoBot CLI")
    print("=" * 50)
    print("Welcome! I'm your personal todo assistant.")
    print("I can help you manage your to-do list and have conversations.")
    print("Type 'quit', 'exit', or 'bye' to stop.")
    print("Type 'clear' to clear conversation history.")
    print("Type 'help' for available commands.")
    print("=" * 50)
    
    # Initialize agent
    try:
        agent = TodoAgent()
        print(f"✅ Agent initialized successfully!")
        
        # Check if user has a name
        user_name = agent.get_user_name()
        if user_name:
            print(f"👋 Welcome back, {user_name}!")
        else:
            print("👋 Hello! What's your name?")
            
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("Please check your .env file and make sure GOOGLE_API_KEY is set.")
        return
    
    print("\n" + "=" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\n🧑 You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Have a great day!")
                break
            
            elif user_input.lower() == 'clear':
                response = agent.clear_conversation()
                print(f"🤖 TodoBot: {response}")
                continue
            
            elif user_input.lower() == 'help':
                print("\n📋 Available Commands:")
                print("• 'quit', 'exit', 'bye' - Exit the chat")
                print("• 'clear' - Clear conversation history")
                print("• 'help' - Show this help message")
                print("\n📝 Todo Commands (just type naturally):")
                print("• 'Add [task] to my todo list'")
                print("• 'Show my todos' or 'List my todos'")
                print("• 'Remove [task] from my list'")
                print("• 'Clear my todo list'")
                continue
            
            elif not user_input:
                print("🤖 TodoBot: Please say something!")
                continue
            
            # Get response from agent
            print("🤖 TodoBot: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

def run_streamlit():
    """Run the Streamlit web interface."""
    import streamlit as st
    
    st.set_page_config(
        page_title="TodoBot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 TodoBot - Your Personal Assistant")
    st.markdown("*Manage your todos and have conversations with AI*")
    
    # Initialize agent
    if 'agent' not in st.session_state:
        try:
            st.session_state.agent = TodoAgent()
            st.success("✅ Agent initialized successfully!")
        except Exception as e:
            st.error(f"❌ Error initializing agent: {e}")
            st.error("Please check your .env file and make sure GOOGLE_API_KEY is set.")
            st.stop()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        user_name = st.session_state.agent.get_user_name()
        if user_name:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"👋 Welcome back, {user_name}! How can I help you today?"
            })
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "👋 Hello! I'm TodoBot. What's your name?"
            })
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Controls")
        
        if st.button("🗑️ Clear Conversation"):
            st.session_state.agent.clear_conversation()
            st.session_state.messages = []
            st.success("Conversation cleared!")
            st.rerun()
        
        st.header("📋 Quick Commands")
        st.markdown("""
        **Todo Commands:**
        - Add [task] to my list
        - Show my todos
        - Remove [task] from my list
        - Clear my todo list
        
        **General:**
        - Just chat naturally!
        - I remember your name and past conversations
        """)
        
        # Show current user
        user_name = st.session_state.agent.get_user_name()
        if user_name:
            st.info(f"👤 Current user: {user_name}")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.agent.chat(prompt)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    """Main entry point."""
    # Check if API key is set
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in .env file")
        print("Please add your Google AI Studio API key to the .env file")
        return
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        print("🌐 Starting Streamlit web interface...")
        run_streamlit()
    else:
        print("🖥️  Starting CLI interface...")
        run_cli()


if __name__ == "__main__":
    main()