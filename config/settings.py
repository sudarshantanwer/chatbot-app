"""Configuration settings for the chatbot application."""

import os
from typing import Dict, Any

class AppConfig:
    """Application configuration class."""
    
    # App settings
    APP_TITLE = "🤖 SmartBot Pro"
    APP_DESCRIPTION = "Advanced AI Chatbot with Multiple Features"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    
    # Model settings
    DEFAULT_MODEL = "google/flan-t5-base"
    FALLBACK_MODEL = "microsoft/DialoGPT-medium"
    MAX_NEW_TOKENS = 150
    TEMPERATURE = 0.7
    
    # Chat settings
    MAX_HISTORY_LENGTH = 20
    CONTEXT_WINDOW = 4
    
    # File settings
    CHAT_EXPORT_FORMAT = "txt"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # UI settings
    SIDEBAR_WIDTH = 300
    CHAT_INPUT_HEIGHT = 100
    
    # Feature flags
    ENABLE_FILE_UPLOAD = True
    ENABLE_CHAT_EXPORT = True
    ENABLE_CHAT_THEMES = True
    ENABLE_VOICE_INPUT = True
    ENABLE_CODE_HIGHLIGHTING = True

class ModelConfig:
    """Model-specific configuration."""
    
    AVAILABLE_MODELS = {
        "flan-t5-base": {
            "name": "Google FLAN-T5 Base",
            "description": "Versatile instruction-following model",
            "type": "text2text-generation",
            "model_id": "google/flan-t5-base"
        },
        "flan-t5-small": {
            "name": "Google FLAN-T5 Small",
            "description": "Faster, smaller version",
            "type": "text2text-generation", 
            "model_id": "google/flan-t5-small"
        },
        "dialogpt": {
            "name": "Microsoft DialoGPT",
            "description": "Conversational AI model",
            "type": "text-generation",
            "model_id": "microsoft/DialoGPT-medium"
        }
    }

class ThemeConfig:
    """UI Theme configuration."""
    
    THEMES = {
        "default": {
            "primary_color": "#FF6B6B",
            "background_color": "#FFFFFF",
            "secondary_background_color": "#F0F2F6",
            "text_color": "#262730"
        },
        "dark": {
            "primary_color": "#00D4AA", 
            "background_color": "#0E1117",
            "secondary_background_color": "#262730",
            "text_color": "#FAFAFA"
        },
        "blue": {
            "primary_color": "#1E88E5",
            "background_color": "#FFFFFF", 
            "secondary_background_color": "#E3F2FD",
            "text_color": "#1A1A1A"
        }
    }

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary."""
    return {
        "app": AppConfig,
        "model": ModelConfig,
        "theme": ThemeConfig
    }
