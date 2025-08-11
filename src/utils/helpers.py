"""Utility functions for the chatbot application."""

import re
import json
import base64
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib

def sanitize_text(text: str) -> str:
    """Sanitize text input to prevent injection attacks."""
    if not isinstance(text, str):
        return ""
    
    # Remove potential HTML/script tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def format_timestamp(dt: datetime, include_date: bool = False) -> str:
    """Format datetime for display."""
    if include_date:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime("%H:%M:%S")

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from text."""
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for language, code in matches:
        code_blocks.append({
            "language": language or "text",
            "code": code.strip()
        })
    
    return code_blocks

def highlight_code(code: str, language: str = "python") -> str:
    """Add basic syntax highlighting for code."""
    # This is a simplified version - in production you might use pygments
    if language.lower() == "python":
        # Highlight Python keywords
        keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'return']
        for keyword in keywords:
            code = re.sub(f'\\b{keyword}\\b', f'**{keyword}**', code)
    
    return code

def generate_session_id() -> str:
    """Generate a unique session ID."""
    timestamp = str(datetime.now().timestamp())
    hash_object = hashlib.md5(timestamp.encode())
    return hash_object.hexdigest()[:8]

def validate_file_size(file_size: int, max_size: int = 10 * 1024 * 1024) -> bool:
    """Validate file size is within limits."""
    return file_size <= max_size

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    size = size_bytes
    unit_index = 0
    
    while size >= 1024 and unit_index < len(size_names) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.1f} {size_names[unit_index]}"

def create_download_link(content: str, filename: str, mime_type: str = "text/plain") -> str:
    """Create a download link for content."""
    b64_content = base64.b64encode(content.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64_content}" download="{filename}">Download {filename}</a>'

def parse_user_input(user_input: str) -> Dict[str, Any]:
    """Parse user input to extract intent and entities."""
    user_input = sanitize_text(user_input)
    
    # Simple intent detection
    intents = {
        "greeting": re.search(r'\b(hello|hi|hey|good morning|good afternoon)\b', user_input, re.IGNORECASE),
        "question": re.search(r'\b(what|who|when|where|why|how)\b', user_input, re.IGNORECASE),
        "math": re.search(r'\b(\d+\s*[+\-*/]\s*\d+)\b', user_input),
        "help": re.search(r'\b(help|assist|support)\b', user_input, re.IGNORECASE),
        "goodbye": re.search(r'\b(bye|goodbye|see you|farewell)\b', user_input, re.IGNORECASE)
    }
    
    detected_intent = None
    for intent, match in intents.items():
        if match:
            detected_intent = intent
            break
    
    # Extract entities (simplified)
    entities = {
        "numbers": re.findall(r'\b\d+\b', user_input),
        "math_operations": re.findall(r'[+\-*/]', user_input),
        "countries": re.findall(r'\b(india|france|japan|usa|china|germany)\b', user_input, re.IGNORECASE)
    }
    
    return {
        "original_text": user_input,
        "intent": detected_intent,
        "entities": entities,
        "length": len(user_input),
        "word_count": len(user_input.split())
    }

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two texts."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def get_response_suggestions(user_input: str) -> List[str]:
    """Get response suggestions based on user input."""
    suggestions = []
    parsed_input = parse_user_input(user_input)
    
    if parsed_input["intent"] == "greeting":
        suggestions.extend([
            "Hello! How can I help you today?",
            "Hi there! What would you like to know?",
            "Greetings! I'm here to assist you."
        ])
    elif parsed_input["intent"] == "question":
        suggestions.extend([
            "That's an interesting question. Let me think...",
            "I'll do my best to answer that for you.",
            "Here's what I know about that topic:"
        ])
    elif parsed_input["intent"] == "math":
        suggestions.extend([
            "Let me calculate that for you.",
            "Here's the mathematical result:",
            "The answer to your calculation is:"
        ])
    
    return suggestions[:3]  # Return top 3 suggestions

class TextProcessor:
    """Advanced text processing utilities."""
    
    @staticmethod
    def clean_response(response: str) -> str:
        """Clean AI model response."""
        # Remove common artifacts
        response = re.sub(r'\n+', '\n', response)  # Multiple newlines
        response = re.sub(r'\s+', ' ', response)   # Multiple spaces
        response = response.strip()
        
        # Remove repetitive patterns
        sentences = response.split('.')
        unique_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in unique_sentences:
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences) + ('.' if unique_sentences else '')
    
    @staticmethod
    def add_personality(response: str, personality: str = "friendly") -> str:
        """Add personality to bot responses."""
        if personality == "friendly":
            if not any(word in response.lower() for word in ["!", "😊", "great", "wonderful"]):
                response += " 😊"
        elif personality == "professional":
            if not response.endswith('.'):
                response += "."
        
        return response
