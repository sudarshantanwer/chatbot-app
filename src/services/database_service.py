"""Database service for storing and retrieving chat histories."""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..models.chat_models import ChatSession, Message, MessageType

class ChatDatabase:
    """SQLite database for storing chat sessions."""
    
    def __init__(self, db_path: str = "data/chats.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create chat_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    content TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    timestamp TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON messages (session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages (timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_updated ON chat_sessions (updated_at)")
            
            conn.commit()
    
    def save_chat_session(self, session: ChatSession, name: str, description: str = "") -> bool:
        """Save a chat session to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save session metadata
                cursor.execute("""
                    INSERT OR REPLACE INTO chat_sessions 
                    (id, name, description, created_at, updated_at, message_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    name,
                    description,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                    len(session.messages),
                    json.dumps({"theme": session.theme.value, "model_name": session.model_name})
                ))
                
                # Delete existing messages for this session
                cursor.execute("DELETE FROM messages WHERE session_id = ?", (session.session_id,))
                
                # Save all messages
                for message in session.messages:
                    message_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO messages 
                        (id, session_id, content, message_type, timestamp, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        message_id,
                        session.session_id,
                        message.content,
                        message.message_type.value,
                        message.timestamp.isoformat(),
                        json.dumps(message.metadata)
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving chat session: {e}")
            return False
    
    def load_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Load a chat session from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get session metadata
                cursor.execute("""
                    SELECT id, name, description, created_at, updated_at, metadata
                    FROM chat_sessions WHERE id = ?
                """, (session_id,))
                
                session_row = cursor.fetchone()
                if not session_row:
                    return None
                
                # Parse metadata
                metadata = json.loads(session_row[5]) if session_row[5] else {}
                
                # Create session object
                session = ChatSession(
                    session_id=session_row[0],
                    created_at=datetime.fromisoformat(session_row[3]),
                    updated_at=datetime.fromisoformat(session_row[4]),
                    model_name=metadata.get("model_name", "flan-t5-base")
                )
                
                # Load messages
                cursor.execute("""
                    SELECT content, message_type, timestamp, metadata
                    FROM messages WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,))
                
                for row in cursor.fetchall():
                    message_metadata = json.loads(row[3]) if row[3] else {}
                    message = Message(
                        content=row[0],
                        message_type=MessageType(row[1]),
                        timestamp=datetime.fromisoformat(row[2]),
                        metadata=message_metadata
                    )
                    session.messages.append(message)
                
                return session
                
        except Exception as e:
            print(f"Error loading chat session: {e}")
            return None
    
    def get_all_chat_sessions(self) -> List[Dict[str, Any]]:
        """Get all saved chat sessions with metadata."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, description, created_at, updated_at, message_count
                    FROM chat_sessions
                    ORDER BY updated_at DESC
                """)
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                        "message_count": row[5]
                    })
                
                return sessions
                
        except Exception as e:
            print(f"Error getting chat sessions: {e}")
            return []
    
    def delete_chat_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first (foreign key constraint)
                cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                
                # Delete session
                cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            return False
    
    def search_messages(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for messages containing the query text."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT m.content, m.message_type, m.timestamp, s.name, s.id
                    FROM messages m
                    JOIN chat_sessions s ON m.session_id = s.id
                    WHERE m.content LIKE ?
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "content": row[0],
                        "message_type": row[1],
                        "timestamp": row[2],
                        "session_name": row[3],
                        "session_id": row[4]
                    })
                
                return results
                
        except Exception as e:
            print(f"Error searching messages: {e}")
            return []
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count sessions
                cursor.execute("SELECT COUNT(*) FROM chat_sessions")
                session_count = cursor.fetchone()[0]
                
                # Count messages
                cursor.execute("SELECT COUNT(*) FROM messages")
                message_count = cursor.fetchone()[0]
                
                # Get latest session
                cursor.execute("""
                    SELECT updated_at FROM chat_sessions 
                    ORDER BY updated_at DESC LIMIT 1
                """)
                latest_row = cursor.fetchone()
                latest_activity = latest_row[0] if latest_row else None
                
                return {
                    "total_sessions": session_count,
                    "total_messages": message_count,
                    "latest_activity": latest_activity
                }
                
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
