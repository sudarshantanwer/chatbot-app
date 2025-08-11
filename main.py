"""
SmartBot Pro - Advanced AI Chatbot Application

A modular, feature-rich chatbot with multiple AI models,
improved UI, and extensive functionality.
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from datetime import datetime

# Import our modular components
from src.services.session_service import SessionManager
from src.services.ai_service import ModelManager
from src.ui.chat_interface import ChatInterface, FileUploadInterface
from config.settings import AppConfig

def initialize_app():
    """Initialize the Streamlit application."""
    st.set_page_config(
        page_title=AppConfig.APP_TITLE,
        page_icon=AppConfig.PAGE_ICON,
        layout=AppConfig.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 20%;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point."""
    initialize_app()
    
    # Initialize services
    session_manager = SessionManager()
    model_manager = ModelManager()
    
    # Initialize UI components
    chat_interface = ChatInterface(session_manager, model_manager)
    file_interface = FileUploadInterface(session_manager)
    
    # Render main interface
    chat_interface.render()
    
    # Render additional features in sidebar
    with st.sidebar:
        st.divider()
        
        # File upload
        if AppConfig.ENABLE_FILE_UPLOAD:
            file_interface.render()
        
        st.divider()
        
        # Advanced features
        with st.expander("🚀 Advanced Features"):
            
            # Voice input placeholder
            if AppConfig.ENABLE_VOICE_INPUT:
                st.info("🎤 Voice input feature coming soon!")
            
            # Export options
            if st.button("📋 Quick Export"):
                chat_content = session_manager.export_chat("txt")
                if chat_content:
                    st.download_button(
                        "Download Chat",
                        chat_content,
                        f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    )
            
            # Session management
            st.subheader("Session Options")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", use_container_width=True):
                    st.info("Save feature coming soon!")
            
            with col2:
                if st.button("📂 Load", use_container_width=True):
                    st.info("Load feature coming soon!")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown(f"""
            **{AppConfig.APP_TITLE}**
            
            Version: 2.0.0
            
            Features:
            - 🤖 Multiple AI Models
            - 💬 Advanced Chat Interface  
            - 📁 File Upload Support
            - 🎨 Multiple Themes
            - 📊 Session Statistics
            - 📥 Export Functionality
            
            Built with:
            - Streamlit
            - Transformers
            - Python 3.8+
            """)
            
            st.markdown("---")
            st.markdown("Made with ❤️ for better conversations")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please check your configuration and try again.")
        
        # Debug information for developers
        if st.checkbox("Show Debug Info"):
            st.exception(e)
