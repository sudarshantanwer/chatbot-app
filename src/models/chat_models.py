"""Data models for the chatbot application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class MessageType(Enum):
    """Message type enumeration."""
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"

class ChatTheme(Enum):
    """Chat theme enumeration."""
    DEFAULT = "default"
    DARK = "dark"
    BLUE = "blue"

@dataclass
class Message:
    """Chat message model."""
    content: str
    message_type: MessageType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "content": self.content,
            "type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            content=data["content"],
            message_type=MessageType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )

@dataclass
class ChatSession:
    """Chat session model."""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    theme: ChatTheme = ChatTheme.DEFAULT
    model_name: str = "flan-t5-base"
    
    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get recent messages."""
        return self.messages[-count:] if self.messages else []
    
    def get_context(self, max_tokens: int = 500) -> str:
        """Get conversation context for AI model."""
        recent_messages = self.get_recent_messages(6)
        context_parts = []
        
        for msg in recent_messages:
            prefix = "User: " if msg.message_type == MessageType.USER else "Assistant: "
            context_parts.append(f"{prefix}{msg.content}")
        
        context = "\n".join(context_parts)
        # Truncate if too long
        if len(context) > max_tokens:
            context = context[-max_tokens:]
        
        return context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "theme": self.theme.value,
            "model_name": self.model_name
        }

@dataclass 
class UserPreferences:
    """User preferences model."""
    theme: ChatTheme = ChatTheme.DEFAULT
    preferred_model: str = "flan-t5-base"
    auto_scroll: bool = True
    show_timestamps: bool = False
    enable_sound: bool = False
    export_format: str = "txt"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preferences to dictionary."""
        return {
            "theme": self.theme.value,
            "preferred_model": self.preferred_model,
            "auto_scroll": self.auto_scroll,
            "show_timestamps": self.show_timestamps,
            "enable_sound": self.enable_sound,
            "export_format": self.export_format
        }
