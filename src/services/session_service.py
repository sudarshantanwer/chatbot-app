"""Chat session management service."""

import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import streamlit as st

from ..models.chat_models import ChatSession, Message, MessageType, UserPreferences
from .database_service import ChatDatabase
from .rag_service import RAGService

class SessionManager:
    """Manages chat sessions and user preferences."""
    
    def __init__(self):
        self.current_session: Optional[ChatSession] = None
        self.user_preferences: UserPreferences = UserPreferences()
        self.chat_db = ChatDatabase()
        self.rag_service = RAGService()
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session state."""
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = self.create_new_session()
        
        if "user_preferences" not in st.session_state:
            st.session_state.user_preferences = self.user_preferences.to_dict()
        
        if "saved_chats" not in st.session_state:
            st.session_state.saved_chats = self.chat_db.get_all_chat_sessions()
        
        self.current_session = st.session_state.chat_session
        self.user_preferences = UserPreferences(**st.session_state.user_preferences)
    
    def create_new_session(self) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id=session_id)
        
        # Add welcome message
        welcome_msg = Message(
            content="Hello! I'm SmartBot Pro. How can I assist you today?",
            message_type=MessageType.BOT
        )
        session.add_message(welcome_msg)
        
        return session
    
    def add_message(self, content: str, message_type: MessageType, metadata: Dict[str, Any] = None) -> None:
        """Add a message to the current session."""
        if not self.current_session:
            self.current_session = self.create_new_session()
        
        message = Message(
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        self.current_session.add_message(message)
        st.session_state.chat_session = self.current_session
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Get messages from current session."""
        if not self.current_session:
            return []
        
        messages = self.current_session.messages
        return messages[-limit:] if limit else messages
    
    def clear_session(self) -> None:
        """Clear current chat session."""
        self.current_session = self.create_new_session()
        st.session_state.chat_session = self.current_session
    
    def export_chat(self, format_type: str = "txt") -> str:
        """Export chat history in specified format."""
        if not self.current_session or not self.current_session.messages:
            return ""
        
        if format_type.lower() == "json":
            return json.dumps(self.current_session.to_dict(), indent=2)
        
        elif format_type.lower() == "txt":
            lines = []
            lines.append(f"Chat Session Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("=" * 50)
            
            for message in self.current_session.messages:
                timestamp = message.timestamp.strftime("%H:%M:%S")
                prefix = "You" if message.message_type == MessageType.USER else "Bot"
                lines.append(f"[{timestamp}] {prefix}: {message.content}")
            
            return "\n".join(lines)
        
        elif format_type.lower() == "md":
            lines = []
            lines.append(f"# Chat Session Export")
            lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            
            for message in self.current_session.messages:
                timestamp = message.timestamp.strftime("%H:%M:%S")
                if message.message_type == MessageType.USER:
                    lines.append(f"**[{timestamp}] You:** {message.content}")
                else:
                    lines.append(f"**[{timestamp}] Bot:** {message.content}")
                lines.append("")
            
            return "\n".join(lines)
        
        return ""
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        for key, value in preferences.items():
            if hasattr(self.user_preferences, key):
                setattr(self.user_preferences, key, value)
        
        st.session_state.user_preferences = self.user_preferences.to_dict()
    
    def get_conversation_context(self, max_messages: int = 6) -> str:
        """Get conversation context for AI model."""
        if not self.current_session:
            return ""
        
        return self.current_session.get_context()
    
    def get_rag_enhanced_context(self, query: str) -> str:
        """Get RAG-enhanced context for better AI responses."""
        return self.rag_service.build_context_prompt(query)
    
    def save_current_session(self, name: str, description: str = "") -> bool:
        """Save the current chat session to database."""
        if not self.current_session or not self.current_session.messages:
            return False
        
        success = self.chat_db.save_chat_session(self.current_session, name, description)
        
        if success:
            # Index the session for RAG
            self.rag_service.index_chat_session(self.current_session.session_id)
            
            # Refresh saved chats list
            st.session_state.saved_chats = self.chat_db.get_all_chat_sessions()
        
        return success
    
    def load_saved_session(self, session_id: str) -> bool:
        """Load a saved chat session."""
        loaded_session = self.chat_db.load_chat_session(session_id)
        
        if loaded_session:
            self.current_session = loaded_session
            st.session_state.chat_session = loaded_session
            return True
        
        return False
    
    def get_saved_sessions(self) -> List[Dict[str, Any]]:
        """Get all saved chat sessions."""
        return st.session_state.get("saved_chats", [])
    
    def delete_saved_session(self, session_id: str) -> bool:
        """Delete a saved chat session."""
        success = self.chat_db.delete_chat_session(session_id)
        
        if success:
            # Remove from vector index
            self.rag_service.remove_session_from_index(session_id)
            
            # Refresh saved chats list
            st.session_state.saved_chats = self.chat_db.get_all_chat_sessions()
        
        return success
    
    def search_chat_history(self, query: str) -> List[Dict[str, Any]]:
        """Search through saved chat history."""
        return self.rag_service.get_relevant_context(query, max_results=10)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        if not self.current_session:
            return {}
        
        messages = self.current_session.messages
        user_messages = [m for m in messages if m.message_type == MessageType.USER]
        bot_messages = [m for m in messages if m.message_type == MessageType.BOT]
        
        total_chars = sum(len(m.content) for m in messages)
        session_duration = (datetime.now() - self.current_session.created_at).total_seconds() / 60
        
        # Get RAG statistics
        rag_stats = self.rag_service.get_rag_statistics()
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "bot_messages": len(bot_messages),
            "total_characters": total_chars,
            "session_duration_minutes": round(session_duration, 1),
            "created_at": self.current_session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "saved_sessions": rag_stats.get("total_sessions", 0),
            "indexed_documents": rag_stats.get("indexed_documents", 0),
            "rag_enabled": rag_stats.get("vector_db_available", False)
        }
