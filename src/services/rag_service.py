"""RAG (Retrieval-Augmented Generation) service for chat context enhancement."""

import os
from typing import List, Dict, Any, Optional
import sqlite3
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .database_service import ChatDatabase

class RAGService:
    """Service for retrieving relevant chat history as context."""
    
    def __init__(self, db_path: str = "data/chats.db", vector_db_path: str = "data/vector_db"):
        self.chat_db = ChatDatabase(db_path)
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        
        if CHROMADB_AVAILABLE:
            self._init_vector_db()
        else:
            print("ChromaDB not available. Using simple text search instead.")
    
    def _init_vector_db(self):
        """Initialize ChromaDB for vector similarity search."""
        try:
            # Initialize ChromaDB client with proper settings
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.vector_db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection("chat_messages")
                print("Using existing ChromaDB collection")
            except:
                self.collection = self.chroma_client.create_collection(
                    name="chat_messages",
                    metadata={"description": "Chat messages for RAG context"}
                )
                print("Created new ChromaDB collection")
            
            # Initialize embedding model with error handling
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Embedding model loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                # Try alternative model
                try:
                    self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
                    print("Loaded alternative embedding model")
                except:
                    print("Using ChromaDB default embeddings")
                    self.embedding_model = None
            
        except Exception as e:
            print(f"Error initializing vector database: {e}")
            print("Falling back to text search mode")
            self.chroma_client = None
            self.collection = None
    
    def index_chat_session(self, session_id: str) -> bool:
        """Index a chat session for vector search."""
        if not CHROMADB_AVAILABLE or not self.collection:
            return False
        
        try:
            # Load chat session
            session = self.chat_db.load_chat_session(session_id)
            if not session:
                return False
            
            # Prepare documents for indexing
            documents = []
            metadatas = []
            ids = []
            
            for i, message in enumerate(session.messages):
                # Only index substantial messages (skip very short ones)
                if len(message.content.strip()) > 10:
                    doc_id = f"{session_id}_{i}"
                    documents.append(message.content)
                    metadatas.append({
                        "session_id": session_id,
                        "message_type": message.message_type.value,
                        "timestamp": message.timestamp.isoformat(),
                        "message_index": i
                    })
                    ids.append(doc_id)
            
            if documents:
                # Add to collection (upsert to handle duplicates)
                self.collection.upsert(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                return True
            
        except Exception as e:
            print(f"Error indexing chat session: {e}")
        
        return False
    
    def index_all_sessions(self) -> int:
        """Index all saved chat sessions."""
        if not CHROMADB_AVAILABLE:
            return 0
        
        sessions = self.chat_db.get_all_chat_sessions()
        indexed_count = 0
        
        for session_info in sessions:
            if self.index_chat_session(session_info["id"]):
                indexed_count += 1
        
        return indexed_count
    
    def get_relevant_context(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Get relevant chat context for a query using vector similarity."""
        if CHROMADB_AVAILABLE and self.collection:
            return self._vector_search(query, max_results)
        else:
            return self._text_search(query, max_results)
    
    def _vector_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform vector similarity search."""
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )
            
            context_results = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )):
                    context_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "relevance_score": 1 - distance,  # Convert distance to similarity
                        "source": "vector_search"
                    })
            
            return context_results
            
        except Exception as e:
            print(f"Error in vector search: {e}")
            return self._text_search(query, max_results)
    
    def _text_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback text search when vector search is not available."""
        try:
            search_results = self.chat_db.search_messages(query, max_results)
            
            context_results = []
            for result in search_results:
                context_results.append({
                    "content": result["content"],
                    "metadata": {
                        "session_id": result["session_id"],
                        "session_name": result["session_name"],
                        "message_type": result["message_type"],
                        "timestamp": result["timestamp"]
                    },
                    "relevance_score": 0.5,  # Default score for text search
                    "source": "text_search"
                })
            
            return context_results
            
        except Exception as e:
            print(f"Error in text search: {e}")
            return []
    
    def build_context_prompt(self, query: str, max_context_length: int = 1000) -> str:
        """Build a context-enhanced prompt for the AI model."""
        relevant_context = self.get_relevant_context(query, max_results=3)
        
        if not relevant_context:
            return query
        
        # Build context section
        context_parts = []
        context_parts.append("Relevant information from previous conversations:")
        
        for i, ctx in enumerate(relevant_context, 1):
            content = ctx["content"]
            # Truncate if too long
            if len(content) > 200:
                content = content[:200] + "..."
            
            context_parts.append(f"{i}. {content}")
        
        context_text = "\n".join(context_parts)
        
        # Ensure total length doesn't exceed limit
        if len(context_text) > max_context_length:
            context_text = context_text[:max_context_length] + "..."
        
        # Combine context with query
        enhanced_prompt = f"""Context from previous conversations:
{context_text}

Current question: {query}

Please answer the current question, using the context above if relevant:"""
        
        return enhanced_prompt
    
    def get_session_summary(self, session_id: str) -> str:
        """Get a summary of a chat session for context."""
        session = self.chat_db.load_chat_session(session_id)
        if not session:
            return ""
        
        # Extract key messages (first few and last few)
        key_messages = []
        
        if len(session.messages) <= 6:
            key_messages = session.messages
        else:
            key_messages = session.messages[:3] + session.messages[-3:]
        
        summary_parts = []
        for msg in key_messages:
            if msg.message_type.value == "user":
                summary_parts.append(f"User: {msg.content[:100]}")
            else:
                summary_parts.append(f"Bot: {msg.content[:100]}")
        
        return " | ".join(summary_parts)
    
    def remove_session_from_index(self, session_id: str) -> bool:
        """Remove a session from the vector index."""
        if not CHROMADB_AVAILABLE or not self.collection:
            return True  # Nothing to remove if vector DB not available
        
        try:
            # Get all document IDs for this session
            results = self.collection.get(
                where={"session_id": session_id},
                include=["metadatas"]
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
            
            return True
            
        except Exception as e:
            print(f"Error removing session from index: {e}")
            return False
    
    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get RAG service statistics."""
        stats = {
            "vector_db_available": CHROMADB_AVAILABLE,
            "indexed_documents": 0,
            "total_sessions": 0
        }
        
        # Get database stats
        db_stats = self.chat_db.get_chat_statistics()
        stats.update(db_stats)
        
        # Get vector DB stats
        if CHROMADB_AVAILABLE and self.collection:
            try:
                collection_count = self.collection.count()
                stats["indexed_documents"] = collection_count
            except:
                pass
        
        return stats
