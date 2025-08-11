"""AI model service for handling different language models."""

import logging
from typing import Optional, Dict, Any, List
import streamlit as st
from abc import ABC, abstractmethod

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from ..models.chat_models import Message, MessageType
from config.settings import ModelConfig

logger = logging.getLogger(__name__)

class BaseModelService(ABC):
    """Abstract base class for model services."""
    
    @abstractmethod
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response from the model."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available."""
        pass

class HuggingFaceModelService(BaseModelService):
    """HuggingFace model service implementation."""
    
    def __init__(self, model_name: str = "google/flan-t5-base"):
        self.model_name = model_name
        self.pipeline = None
        self.tokenizer = None
        self._load_model()
    
    @st.cache_resource
    def _load_model(_self):
        """Load the HuggingFace model with caching."""
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers library not available")
            return None, None
            
        try:
            model_info = ModelConfig.AVAILABLE_MODELS.get(_self.model_name.split('/')[-1], {})
            model_type = model_info.get("type", "text2text-generation")
            
            pipeline_obj = pipeline(
                model_type,
                model=_self.model_name,
                device=-1,  # CPU
                torch_dtype="auto"
            )
            
            tokenizer = AutoTokenizer.from_pretrained(_self.model_name)
            
            logger.info(f"Successfully loaded model: {_self.model_name}")
            return pipeline_obj, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load model {_self.model_name}: {e}")
            return None, None
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response from the HuggingFace model."""
        if not self.is_available():
            return "Sorry, the AI model is not available right now."
        
        try:
            # Prepare the input
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}\nAnswer:"
            else:
                full_prompt = f"Question: {prompt}\nAnswer:"
            
            # Generate response
            result = self.pipeline(
                full_prompt,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            response = result[0]['generated_text']
            
            # Clean up the response
            if "Answer:" in response:
                response = response.split("Answer:")[-1].strip()
            
            return response if response else "I'm not sure how to respond to that."
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error while processing your request."
    
    def is_available(self) -> bool:
        """Check if the model is available."""
        return TRANSFORMERS_AVAILABLE and self.pipeline is not None

class FallbackModelService(BaseModelService):
    """Fallback service for when main models are unavailable."""
    
    def __init__(self):
        self.responses = {
            # Math
            r"(?i)what.*2\s*\+\s*2|2\s*\+\s*2": "4",
            r"(?i)what.*5\s*\*\s*5|5\s*\*\s*5": "25",
            r"(?i)what.*10\s*-\s*3|10\s*-\s*3": "7",
            
            # Geography
            r"(?i)capital.*india": "New Delhi is the capital of India.",
            r"(?i)capital.*france": "Paris is the capital of France.",
            r"(?i)capital.*japan": "Tokyo is the capital of Japan.",
            
            # General knowledge
            r"(?i)after.*a|letter.*after.*a": "B comes after A in the alphabet.",
            r"(?i)hello|hi|hey": "Hello! I'm running in basic mode. How can I help you?",
            r"(?i)how.*you": "I'm doing well, thank you for asking!",
            r"(?i)weather": "I don't have access to current weather data. Please check a weather service.",
            
            # Science
            r"(?i)photosynthesis": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create glucose and oxygen.",
            r"(?i)gravity": "Gravity is the force that attracts objects toward each other, keeping us on Earth's surface.",
        }
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using pattern matching."""
        import re
        
        prompt_lower = prompt.lower()
        
        # Check patterns
        for pattern, response in self.responses.items():
            if re.search(pattern, prompt):
                return response
        
        # Default responses based on keywords
        if any(word in prompt_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm currently in basic mode. How can I assist you today?"
        elif any(word in prompt_lower for word in ["help", "what", "how"]):
            return "I'm here to help! I can answer basic questions about math, geography, and general knowledge."
        elif "?" in prompt:
            return "That's an interesting question! Unfortunately, I'm running in basic mode and may not have the full answer."
        else:
            return "I understand you're trying to communicate with me. I'm currently in basic mode with limited capabilities."
    
    def is_available(self) -> bool:
        """Fallback is always available."""
        return True

class ModelManager:
    """Manages different AI models and provides unified interface."""
    
    def __init__(self):
        self.current_model: Optional[BaseModelService] = None
        self.fallback_model = FallbackModelService()
        self.available_models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available models."""
        if TRANSFORMERS_AVAILABLE:
            for model_key, model_info in ModelConfig.AVAILABLE_MODELS.items():
                try:
                    model_service = HuggingFaceModelService(model_info["model_id"])
                    if model_service.is_available():
                        self.available_models[model_key] = model_service
                        if self.current_model is None:
                            self.current_model = model_service
                except Exception as e:
                    logger.warning(f"Failed to initialize model {model_key}: {e}")
        
        # Set fallback if no models available
        if self.current_model is None:
            self.current_model = self.fallback_model
    
    def set_model(self, model_name: str) -> bool:
        """Set the current model."""
        if model_name in self.available_models:
            self.current_model = self.available_models[model_name]
            return True
        elif model_name == "fallback":
            self.current_model = self.fallback_model
            return True
        return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        models = list(self.available_models.keys())
        models.append("fallback")
        return models
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using current model."""
        if self.current_model:
            return self.current_model.generate_response(prompt, context)
        return self.fallback_model.generate_response(prompt, context)
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models."""
        status = {
            "current_model": type(self.current_model).__name__,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "available_models": self.get_available_models(),
            "model_count": len(self.available_models)
        }
        return status
