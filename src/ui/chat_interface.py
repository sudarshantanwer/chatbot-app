"""Main user interface components for the chatbot."""

import streamlit as st
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models.chat_models import Message, MessageType, ChatTheme
from ..services.session_service import SessionManager
from ..services.ai_service import ModelManager
from ..utils.helpers import format_timestamp, extract_code_blocks, TextProcessor
from config.settings import AppConfig, ThemeConfig

class ChatInterface:
    """Main chat interface component."""
    
    def __init__(self, session_manager: SessionManager, model_manager: ModelManager):
        self.session_manager = session_manager
        self.model_manager = model_manager
        self.text_processor = TextProcessor()
    
    def render(self):
        """Render the main chat interface."""
        self._render_header()
        self._render_sidebar()
        self._render_chat_area()
        self._render_input_area()
    
    def _render_header(self):
        """Render the header section."""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title(AppConfig.APP_TITLE)
            st.caption(AppConfig.APP_DESCRIPTION)
        
        # Status indicator
        model_status = self.model_manager.get_model_status()
        if model_status["transformers_available"]:
            st.success("🟢 AI Models Available")
        else:
            st.warning("🟡 Running in Basic Mode")
    
    def _render_sidebar(self):
        """Render the sidebar with controls and settings."""
        with st.sidebar:
            st.header("⚙️ Settings")
            
            # Model selection
            self._render_model_selector()
            
            st.divider()
            
            # Chat controls
            self._render_chat_controls()
            
            st.divider()
            
            # Session stats
            self._render_session_stats()
            
            st.divider()
            
            # Theme settings
            self._render_theme_settings()
    
    def _render_model_selector(self):
        """Render model selection interface."""
        st.subheader("🤖 AI Model")
        
        available_models = self.model_manager.get_available_models()
        
        if len(available_models) > 1:
            selected_model = st.selectbox(
                "Choose AI Model:",
                available_models,
                format_func=lambda x: self._format_model_name(x)
            )
            
            if st.button("Apply Model"):
                if self.model_manager.set_model(selected_model):
                    st.success(f"Switched to {selected_model}")
                    st.rerun()
                else:
                    st.error("Failed to switch model")
        else:
            st.info("Only basic model available")
    
    def _render_chat_controls(self):
        """Render chat control buttons."""
        st.subheader("💬 Chat Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                self.session_manager.clear_session()
                st.rerun()
        
        with col2:
            if st.button("📊 Stats", use_container_width=True):
                st.session_state.show_stats = not st.session_state.get("show_stats", False)
        
        # Export options
        export_format = st.selectbox(
            "Export Format:",
            ["txt", "json", "md"],
            format_func=lambda x: {"txt": "Text", "json": "JSON", "md": "Markdown"}[x]
        )
        
        if st.button("📥 Export Chat", use_container_width=True):
            chat_content = self.session_manager.export_chat(export_format)
            if chat_content:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_export_{timestamp}.{export_format}"
                st.download_button(
                    label=f"Download {export_format.upper()}",
                    data=chat_content,
                    file_name=filename,
                    mime=f"text/{export_format}"
                )
            else:
                st.warning("No chat history to export")
    
    def _render_session_stats(self):
        """Render session statistics."""
        if st.session_state.get("show_stats", False):
            st.subheader("📊 Session Stats")
            stats = self.session_manager.get_session_stats()
            
            if stats:
                st.metric("Messages", stats["total_messages"])
                st.metric("Duration (min)", stats["session_duration_minutes"])
                st.metric("Characters", stats["total_characters"])
                st.caption(f"Started: {stats['created_at']}")
    
    def _render_theme_settings(self):
        """Render theme selection."""
        st.subheader("🎨 Appearance")
        
        themes = list(ThemeConfig.THEMES.keys())
        current_theme = st.session_state.get("theme", "default")
        
        selected_theme = st.selectbox(
            "Theme:",
            themes,
            index=themes.index(current_theme) if current_theme in themes else 0,
            format_func=lambda x: x.title()
        )
        
        if selected_theme != current_theme:
            st.session_state.theme = selected_theme
            self._apply_theme(selected_theme)
    
    def _render_chat_area(self):
        """Render the main chat message area."""
        st.subheader("💬 Conversation")
        
        messages = self.session_manager.get_messages()
        
        if not messages:
            st.info("👋 Start a conversation by typing a message below!")
            self._render_example_prompts()
            return
        
        # Create chat container
        chat_container = st.container()
        
        with chat_container:
            for message in messages:
                self._render_message(message)
    
    def _render_message(self, message: Message):
        """Render a single chat message."""
        timestamp = format_timestamp(message.timestamp)
        
        if message.message_type == MessageType.USER:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(message.content)
                if st.session_state.get("show_timestamps", False):
                    st.caption(timestamp)
        
        elif message.message_type == MessageType.BOT:
            with st.chat_message("assistant", avatar="🤖"):
                # Check for code blocks
                code_blocks = extract_code_blocks(message.content)
                if code_blocks:
                    self._render_message_with_code(message.content, code_blocks)
                else:
                    st.write(message.content)
                
                if st.session_state.get("show_timestamps", False):
                    st.caption(timestamp)
    
    def _render_message_with_code(self, content: str, code_blocks: List[Dict[str, str]]):
        """Render message with syntax-highlighted code blocks."""
        # Split content by code blocks and render alternately
        parts = content.split("```")
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Regular text
                if part.strip():
                    st.write(part.strip())
            else:  # Code block
                lines = part.strip().split('\n')
                language = lines[0] if lines else "text"
                code = '\n'.join(lines[1:]) if len(lines) > 1 else part
                
                st.code(code, language=language)
    
    def _render_input_area(self):
        """Render the chat input area."""
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_area(
                    "Type your message:",
                    placeholder="Ask me anything...",
                    height=60,
                    key="user_input"
                )
            
            with col2:
                st.write("")  # Add some spacing
                st.write("")  # Add some spacing
                submit_button = st.form_submit_button("Send 📤", use_container_width=True)
            
            if submit_button and user_input.strip():
                self._process_user_input(user_input.strip())
                st.rerun()
    
    def _render_example_prompts(self):
        """Render example prompts for users."""
        with st.expander("💡 Try these example questions"):
            examples = [
                "What is 25 * 4?",
                "What is the capital of France?", 
                "Explain photosynthesis in simple terms",
                "Write a short poem about technology",
                "What comes after the letter 'Z'?",
                "How does gravity work?"
            ]
            
            cols = st.columns(2)
            for i, example in enumerate(examples):
                with cols[i % 2]:
                    if st.button(example, key=f"example_{i}", use_container_width=True):
                        self._process_user_input(example)
                        st.rerun()
    
    def _process_user_input(self, user_input: str):
        """Process user input and generate response."""
        # Add user message
        self.session_manager.add_message(user_input, MessageType.USER)
        
        # Get conversation context
        context = self.session_manager.get_conversation_context()
        
        # Generate AI response
        with st.spinner("🤔 Thinking..."):
            response = self.model_manager.generate_response(user_input, context)
            response = self.text_processor.clean_response(response)
            response = self.text_processor.add_personality(response, "friendly")
        
        # Add bot response
        self.session_manager.add_message(response, MessageType.BOT)
    
    def _format_model_name(self, model_key: str) -> str:
        """Format model name for display."""
        model_names = {
            "flan-t5-base": "FLAN-T5 Base (Recommended)",
            "flan-t5-small": "FLAN-T5 Small (Fast)",
            "dialogpt": "DialoGPT (Conversational)",
            "fallback": "Basic Mode"
        }
        return model_names.get(model_key, model_key.title())
    
    def _apply_theme(self, theme_name: str):
        """Apply selected theme."""
        if theme_name in ThemeConfig.THEMES:
            theme = ThemeConfig.THEMES[theme_name]
            
            # Apply theme using custom CSS
            st.markdown(f"""
            <style>
            .stApp {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
            }}
            .stSidebar {{
                background-color: {theme['secondary_background_color']};
            }}
            .stButton > button {{
                background-color: {theme['primary_color']};
                color: white;
                border: none;
            }}
            </style>
            """, unsafe_allow_html=True)

class FileUploadInterface:
    """File upload interface component."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def render(self):
        """Render file upload interface."""
        with st.expander("📁 File Upload"):
            uploaded_file = st.file_uploader(
                "Upload a text file to analyze:",
                type=['txt', 'md', 'py', 'js', 'json'],
                help="Upload text files for analysis or questions"
            )
            
            if uploaded_file is not None:
                self._process_uploaded_file(uploaded_file)
    
    def _process_uploaded_file(self, uploaded_file):
        """Process uploaded file."""
        try:
            content = str(uploaded_file.read(), "utf-8")
            
            st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
            
            # Show file preview
            if len(content) > 500:
                st.text_area("File Preview (first 500 chars):", content[:500] + "...", height=150)
            else:
                st.text_area("File Content:", content, height=150)
            
            # Add to chat context
            file_message = f"📁 File uploaded: {uploaded_file.name}\n\nContent preview:\n{content[:200]}..."
            self.session_manager.add_message(file_message, MessageType.SYSTEM)
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
