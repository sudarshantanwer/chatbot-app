"""Chat session management service."""

import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import streamlit as st

from ..models.chat_models import ChatSession, Message, MessageType, UserPreferences

class SessionManager:
    """Manages chat sessions and user preferences."""
    
    def __init__(self):
        self.current_session: Optional[ChatSession] = None
        self.user_preferences: UserPreferences = UserPreferences()
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session state."""
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = self.create_new_session()
        
        if "user_preferences" not in st.session_state:
            st.session_state.user_preferences = self.user_preferences.to_dict()
        
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
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        if not self.current_session:
            return {}
        
        messages = self.current_session.messages
        user_messages = [m for m in messages if m.message_type == MessageType.USER]
        bot_messages = [m for m in messages if m.message_type == MessageType.BOT]
        
        total_chars = sum(len(m.content) for m in messages)
        session_duration = (datetime.now() - self.current_session.created_at).total_seconds() / 60
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "bot_messages": len(bot_messages),
            "total_characters": total_chars,
            "session_duration_minutes": round(session_duration, 1),
            "created_at": self.current_session.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
