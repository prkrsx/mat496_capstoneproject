#!/usr/bin/env python3
"""
React Learning Coach - Streamlit UI
Interactive web interface for the learning coach agent.
"""

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from graph import build_graph
import re

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="React Learning Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode monotone CSS
st.markdown("""
<style>
    /* Dark mode base */
    .main {
        background-color: #0d1117;
        color: #c9d1d9;
        padding: 0 2rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Stage badge styling */
    .stage-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #21262d;
        border: 1px solid #30363d;
        color: #c9d1d9;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Primary button styling */
    .stButton>button[kind="primary"] {
        background-color: #238636;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stButton>button[kind="primary"]:hover {
        background-color: #2ea043;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.3);
    }
    
    /* Regular button styling */
    .stButton>button {
        border-radius: 6px;
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #c9d1d9;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #30363d;
        border-color: #8b949e;
        transform: translateY(-1px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #21262d;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #c9d1d9;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: #238636;
    }
    
    .stProgress > div > div {
        background-color: #21262d;
    }
    
    /* Chat input styling */
    .stChatInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #30363d;
        background-color: #0d1117;
        color: #c9d1d9;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    .stChatInput>div>div>input:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
    }
    
    /* Chat message improvements */
    [data-testid="stChatMessage"] {
        border-radius: 6px;
        margin-bottom: 1rem;
        padding: 1rem;
        background-color: #161b22;
        border: 1px solid #21262d;
    }
    
    [data-testid="stChatMessageContent"] {
        padding: 0;
        color: #c9d1d9;
    }
    
    /* User message */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background-color: #0d1117;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 6px;
        font-weight: 600;
        background-color: #21262d;
        border: 1px solid #30363d;
        color: #c9d1d9;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #30363d;
    }
    
    /* Divider styling */
    hr {
        margin: 1.5rem 0;
        border-color: #21262d;
    }
    
    /* Caption text */
    .stCaption {
        color: #8b949e;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #c9d1d9;
    }
    
    /* Info, success boxes */
    .stAlert {
        background-color: #161b22;
        border: 1px solid #30363d;
        color: #c9d1d9;
        border-radius: 6px;
    }
    
    /* Title */
    h1 {
        color: #c9d1d9;
    }
    
    /* Links */
    a {
        color: #58a6ff;
    }
    
    a:hover {
        color: #79c0ff;
    }
    
    /* Code blocks */
    code {
        background-color: #161b22;
        color: #79c0ff;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'state' not in st.session_state:
        st.session_state.state = {
            "messages": [],
            "learner_profile": {},
            "project_spec": {"features": []},
            "stages": [],
            "current_stage_index": 0,
            "status": "onboarding",
        }
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'graph' not in st.session_state:
        st.session_state.graph = build_graph()
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def process_user_input(user_input):
    """Process user input through the graph."""
    if not user_input.strip():
        return
    
    # Add user message to state
    st.session_state.state["messages"].append(HumanMessage(content=user_input))
    
    # Add to chat history for display
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Process through graph
    with st.spinner("🤔 Coach is thinking..."):
        try:
            st.session_state.state = st.session_state.graph.invoke(st.session_state.state)
            
            # Extract new AI messages
            for msg in reversed(st.session_state.state["messages"]):
                if msg.type == "ai":
                    # Check if this message is already in chat history
                    if not st.session_state.chat_history or st.session_state.chat_history[-1]["content"] != msg.content:
                        st.session_state.chat_history.append({"role": "ai", "content": msg.content})
                    break
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.chat_history.append({
                "role": "ai", 
                "content": f"❌ Sorry, I encountered an error: {str(e)}"
            })

def display_sidebar():
    """Display sidebar with project info and controls."""
    with st.sidebar:
        # Header with gradient
        st.markdown("# 🎓 Learning Coach")
        
        state = st.session_state.state
        
        # Project info in expandable section
        if state.get("project_spec", {}).get("summary"):
            with st.expander("📋 Current Project", expanded=True):
                st.write(state["project_spec"]["summary"])
        
        # Level badge
        level = state.get("learner_profile", {}).get("assumed_level", "Not set")
        if level != "Not set":
            st.markdown(f"""
            <div style="text-align: center; margin: 1rem 0;">
                <span style="background-color: #21262d; border: 1px solid #30363d;
                             color: #c9d1d9; padding: 0.5rem 1.5rem; border-radius: 6px; 
                             font-weight: 600; font-size: 0.9rem;">
                    🎯 {level.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress with better visualization
        if state.get("stages"):
            current_stage = state.get("current_stage_index", 0)
            total_stages = len(state["stages"])
            progress = (current_stage / total_stages) if total_stages > 0 else 0
            
            st.markdown("### 📊 Your Progress")
            st.progress(progress)
            st.caption(f"**Stage {current_stage + 1}** of **{total_stages}**")
            st.divider()
            
            # Stages in collapsible section
            with st.expander("📚 All Stages", expanded=False):
                for i, stage in enumerate(state["stages"]):
                    if i == current_stage:
                        st.markdown(f"**▶ {i+1}. {stage['name']}**")
                    elif i < current_stage:
                        st.markdown(f"✅ ~~{i+1}. {stage['name']}~~")
                    else:
                        st.markdown(f"⭕ {i+1}. {stage['name']}")
        
        # Features in collapsible section
        if state.get("project_spec", {}).get("features"):
            with st.expander("✨ Features", expanded=False):
                for feature in state["project_spec"]["features"]:
                    st.markdown(f"• {feature}")
        
        st.divider()
        
        # Quick action buttons with icons
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("➡️ Continue", use_container_width=True, type="primary"):
            process_user_input("continue")
            st.rerun()
        
        if st.button("✅ Mark Complete", use_container_width=True):
            process_user_input("done")
            st.rerun()
        
        if st.button("🏋️ Practice", use_container_width=True):
            process_user_input("give me exercises")
            st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❓ Help", use_container_width=True):
                show_help()
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                if st.session_state.get('confirm_reset'):
                    reset_session()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("Tap again")

def show_help():
    """Display help information."""
    help_msg = """
### 🆘 Available Commands

**Navigation:**
- `continue` / `start` - Begin or show current stage
- `done` / `next stage` - Complete stage and move forward
- `go to stage X` - Jump to specific stage

**Learning:**
- `give me exercises` - Get 3 practice problems
- `give me exercises for X` - Practice specific topic
- Ask any question - Get explanations

**Planning:**
- `add feature: [description]` - Add new feature
- `I'm actually [level]` - Change difficulty level
  - Levels: beginner, intermediate, advanced

**Other:**
- `help` - Show this menu
"""
    st.session_state.chat_history.append({"role": "ai", "content": help_msg})
    st.rerun()

def reset_session():
    """Reset the session state."""
    st.session_state.clear()
    init_session_state()
    st.rerun()

def display_chat():
    """Display chat messages."""
    # Welcome message if no history
    if not st.session_state.chat_history:
        st.markdown("""
        ### 👋 Welcome to React Learning Coach!
        
        I'm your personal guide for mastering React and TypeScript through hands-on projects.
        
        **🎯 What I'll help you with:**
        - 📚 Structured learning path tailored to your level
        - 💡 Step-by-step guidance through real projects  
        - 🏋️ Practice exercises to reinforce concepts
        - ❓ Answers to your questions along the way
        
        ---
        
        **Let's get started!** Tell me what you'd like to build:
        
        💭 _Example: "I want to build a todo app with TypeScript and user authentication"_
        """)
        return
    
    # Display chat history using Streamlit's native chat messages
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(msg["content"])

def main():
    """Main application."""
    init_session_state()
    
    # Minimal header
    st.title("🎓 React Learning Coach")
    
    # Sidebar
    display_sidebar()
    
    # Show stage badge if available
    state = st.session_state.state
    if state.get("stages") and state.get("status") not in ["onboarding", ""]:
        current = state.get("current_stage_index", 0)
        total = len(state["stages"])
        stage_name = state["stages"][current]["name"] if current < total else "Complete"
        st.markdown(f"""
        <div class="stage-badge">
            📍 Stage {current + 1}/{total}: {stage_name}
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat area
    chat_container = st.container()
    with chat_container:
        display_chat()
    
    # Spacer
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Input area - clean and prominent
    user_input = st.chat_input(
        "💬 Type your message or command here...",
        key="chat_input"
    )
    
    if user_input:
        process_user_input(user_input)
        st.rerun()
    
    # Contextual quick suggestions based on state
    if state.get("stages"):
        current_idx = state.get("current_stage_index", 0)
        if current_idx < len(state.get("stages", [])):
            st.markdown("---")
            st.caption("💡 **Suggested actions:**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📖 Show instructions", key="btn_continue", use_container_width=True):
                    process_user_input("continue")
                    st.rerun()
            
            with col2:
                if st.button("🏋️ Get exercises", key="btn_exercises", use_container_width=True):
                    process_user_input("give me exercises")
                    st.rerun()
            
            with col3:
                if st.button("❓ Ask question", key="btn_question", use_container_width=True):
                    st.toast("💡 Type your question in the chat input above!")
            
            with col4:
                if st.button("✅ Mark done", key="btn_done", use_container_width=True):
                    process_user_input("done")
                    st.rerun()
    else:
        # Onboarding suggestions
        st.markdown("---")
        st.caption("💡 **Quick start examples:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Todo App", use_container_width=True):
                process_user_input("I want to build a todo app with TypeScript")
                st.rerun()
        
        with col2:
            if st.button("🛒 E-commerce", use_container_width=True):
                process_user_input("I want to build an e-commerce product catalog")
                st.rerun()
        
        with col3:
            if st.button("💬 Chat App", use_container_width=True):
                process_user_input("I want to build a real-time chat application")
                st.rerun()

if __name__ == "__main__":
    main()
