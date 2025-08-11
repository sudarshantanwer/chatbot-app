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
        
        # Check if sidebar is accessible, if not provide toggle
        self._render_sidebar_toggle()
        
        self._render_sidebar()
        self._render_chat_area()
        self._render_input_area()
    
    def _render_sidebar_toggle(self):
        """Render sidebar toggle button if sidebar is not visible."""
        if 'show_sidebar_controls' not in st.session_state:
            st.session_state.show_sidebar_controls = False
        
        # Add a button to toggle sidebar controls in main area
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            if st.button("⚙️ Settings", help="Toggle settings panel"):
                st.session_state.show_sidebar_controls = not st.session_state.show_sidebar_controls
        
        # If sidebar controls are toggled on, show them in main area
        if st.session_state.show_sidebar_controls:
            self._render_inline_controls()
    
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
        try:
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
                
                # Add a note about inline controls
                st.markdown("---")
                st.caption("💡 If sidebar disappears, use the ⚙️ Settings button in the main area")
                
        except Exception as e:
            # If sidebar fails to render, ensure inline controls are available
            st.session_state.show_sidebar_controls = True
            st.error("Sidebar unavailable. Using inline controls.")
    
    def _render_inline_controls(self):
        """Render controls inline in main area when sidebar is not accessible."""
        with st.expander("🔧 Chat Controls", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🗑️ Clear Chat", key="inline_clear"):
                    self.session_manager.clear_session()
                    st.rerun()
            
            with col2:
                if st.button("💾 Save Chat", key="inline_save"):
                    st.session_state.show_save_dialog = True
            
            with col3:
                if st.button("📁 Load Chat", key="inline_load"):
                    st.session_state.show_load_dialog = True
            
            with col4:
                available_models = self.model_manager.get_available_models()
                if len(available_models) > 1:
                    selected_model = st.selectbox(
                        "Model:",
                        available_models,
                        key="inline_model",
                        format_func=lambda x: self._format_model_name(x)
                    )
                    if st.button("Apply", key="inline_apply"):
                        self.model_manager.set_model(selected_model)
                        st.rerun()
    
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
        
        # Save chat section
        st.divider()
        st.subheader("💾 Save Current Chat")
        
        with st.form("save_chat_form"):
            chat_name = st.text_input("Chat Name:", placeholder="e.g., Python Help Session")
            chat_description = st.text_area("Description (optional):", 
                                           placeholder="Brief description of this conversation",
                                           height=60)
            
            save_submitted = st.form_submit_button("Save Chat", use_container_width=True)
            
            if save_submitted and chat_name.strip():
                if self.session_manager.save_current_session(chat_name.strip(), chat_description.strip()):
                    st.success(f"✅ Chat saved as '{chat_name}'")
                    st.rerun()
                else:
                    st.error("❌ Failed to save chat. Please try again.")
            elif save_submitted:
                st.error("Please enter a chat name.")
        
        # Load saved chats section
        st.divider()
        st.subheader("📁 Saved Chats")
        
        saved_sessions = self.session_manager.get_saved_sessions()
        
        if saved_sessions:
            # Search saved chats
            search_query = st.text_input("🔍 Search saved chats:", placeholder="Search by name or content...")
            
            if search_query:
                # Filter sessions by search query
                filtered_sessions = [
                    session for session in saved_sessions
                    if search_query.lower() in session["name"].lower() or 
                       search_query.lower() in session.get("description", "").lower()
                ]
            else:
                filtered_sessions = saved_sessions
            
            # Display saved chats
            for session in filtered_sessions[:10]:  # Show max 10
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{session['name']}**")
                        st.caption(f"Messages: {session['message_count']} | Updated: {session['updated_at'][:10]}")
                        if session.get('description'):
                            st.caption(f"Description: {session['description'][:50]}...")
                    
                    with col2:
                        if st.button("Load", key=f"load_{session['id']}", use_container_width=True):
                            if self.session_manager.load_saved_session(session['id']):
                                st.success(f"Loaded '{session['name']}'")
                                st.rerun()
                            else:
                                st.error("Failed to load chat")
                    
                    with col3:
                        if st.button("Delete", key=f"delete_{session['id']}", use_container_width=True):
                            if self.session_manager.delete_saved_session(session['id']):
                                st.success("Chat deleted")
                                st.rerun()
                            else:
                                st.error("Failed to delete")
                    
                    st.divider()
            
            if len(saved_sessions) > 10:
                st.info(f"Showing 10 of {len(saved_sessions)} saved chats. Use search to find specific chats.")
        else:
            st.info("No saved chats yet. Save your current conversation to access it later!")
        
        # Export options
        st.divider()
        st.subheader("📥 Export Options")
        
        export_format = st.selectbox(
            "Export Format:",
            ["txt", "json", "md"],
            format_func=lambda x: {"txt": "Text", "json": "JSON", "md": "Markdown"}[x]
        )
        
        if st.button("📥 Export Current Chat", use_container_width=True):
            chat_content = self.session_manager.export_chat(export_format)
            if chat_content:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_export_{timestamp}.{export_format}"
                st.download_button(
                    label=f"Download {export_format.upper()}",
                    data=chat_content,
                    file_name=filename,
                    mime=f"text/{export_format}",
                    use_container_width=True
                )
            else:
                st.warning("No chat history to export")
    
    def _render_session_stats(self):
        """Render session statistics."""
        if st.session_state.get("show_stats", False):
            st.subheader("📊 Session Stats")
            stats = self.session_manager.get_session_stats()
            
            if stats:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Messages", stats["total_messages"])
                    st.metric("Duration (min)", stats["session_duration_minutes"])
                    st.metric("Characters", stats["total_characters"])
                
                with col2:
                    st.metric("Saved Chats", stats.get("saved_sessions", 0))
                    st.metric("Indexed Docs", stats.get("indexed_documents", 0))
                    rag_status = "✅ Enabled" if stats.get("rag_enabled", False) else "❌ Disabled"
                    st.metric("RAG Status", rag_status)
                
                st.caption(f"Started: {stats['created_at']}")
        
        # RAG Settings
        st.divider()
        st.subheader("🧠 RAG Settings")
        
        # Enable/disable RAG
        use_rag = st.checkbox("Use Knowledge Base for Responses", 
                             value=st.session_state.get("use_rag", True),
                             help="Use previous conversations to enhance responses")
        st.session_state.use_rag = use_rag
        
        # RAG actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Rebuild Index", use_container_width=True,
                        help="Rebuild the knowledge base index"):
                with st.spinner("Rebuilding index..."):
                    indexed_count = self.session_manager.rag_service.index_all_sessions()
                    st.success(f"Indexed {indexed_count} sessions")
        
        with col2:
            if st.button("🔍 Test RAG", use_container_width=True,
                        help="Test the knowledge base search"):
                st.session_state.show_rag_test = not st.session_state.get("show_rag_test", False)
        
        # RAG test interface
        if st.session_state.get("show_rag_test", False):
            st.subheader("🔍 Knowledge Base Search")
            test_query = st.text_input("Test search query:", placeholder="Enter a question to search your chat history")
            
            if test_query:
                results = self.session_manager.search_chat_history(test_query)
                if results:
                    st.write("**Found relevant content:**")
                    for i, result in enumerate(results[:3], 1):
                        with st.expander(f"Result {i} (Score: {result.get('relevance_score', 0):.2f})"):
                            st.write(result['content'])
                            if 'metadata' in result:
                                st.caption(f"From: {result['metadata'].get('session_name', 'Unknown session')}")
                else:
                    st.info("No relevant content found.")
    
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
        
        # Get RAG-enhanced context
        with st.spinner("🔍 Searching knowledge base..."):
            rag_context = self.session_manager.get_rag_enhanced_context(user_input)
        
        # Generate AI response with RAG context
        with st.spinner("🤔 Thinking..."):
            response = self.model_manager.generate_response(user_input, rag_context, use_rag=True)
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
