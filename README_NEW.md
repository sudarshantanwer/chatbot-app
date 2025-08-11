# 🤖 SmartBot Pro - Advanced AI Chatbot

A sophisticated, modular chatbot application built with Streamlit and multiple AI models, featuring an advanced architecture, beautiful UI, and extensive functionality.

## ✨ Features

### 🧠 AI Capabilities
- **Multiple AI Models**: Support for Google FLAN-T5, Microsoft DialoGPT, and more
- **Intelligent Context**: Maintains conversation context for better responses
- **Fallback System**: Graceful degradation when AI models are unavailable
- **Smart Response Processing**: Automatic text cleaning and personality injection

### 💬 Chat Experience
- **Modern UI**: Beautiful chat interface with custom styling
- **Real-time Responses**: Fast, responsive chat experience
- **Message History**: Persistent conversation history
- **Code Highlighting**: Automatic syntax highlighting for code blocks
- **File Upload**: Analyze and discuss uploaded text files

### 🎨 Customization
- **Multiple Themes**: Default, Dark, and Blue themes
- **Flexible Settings**: Customizable model parameters and preferences
- **Session Management**: Save, load, and manage chat sessions
- **Export Options**: Export chats in TXT, JSON, or Markdown formats

### 📊 Analytics
- **Session Statistics**: Track messages, duration, and usage
- **Model Status**: Real-time model availability and performance
- **Debug Information**: Detailed error reporting and diagnostics

## 🏗️ Architecture

The application follows a modular architecture with clear separation of concerns:

```
chatbot-app/
├── main.py                 # Application entry point
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat_models.py  # Data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py   # AI model management
│   │   └── session_service.py # Session management
│   ├── ui/
│   │   ├── __init__.py
│   │   └── chat_interface.py # UI components
│   └── utils/
│       ├── __init__.py
│       └── helpers.py      # Utility functions
├── assets/                 # Static assets
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

### Key Components

1. **AI Service** (`src/services/ai_service.py`)
   - Model loading and management
   - Response generation
   - Fallback handling

2. **Session Service** (`src/services/session_service.py`)
   - Chat session management
   - Message persistence
   - Export functionality

3. **Chat Interface** (`src/ui/chat_interface.py`)
   - Main UI components
   - Theme management
   - User interactions

4. **Configuration** (`config/settings.py`)
   - Centralized settings
   - Model configurations
   - Feature flags

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run main.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

### Alternative: Using the original app.py
If you prefer the simpler version:
```bash
streamlit run app.py
```

## 🔧 Configuration

### Model Configuration
Edit `config/settings.py` to customize:
- Available AI models
- Model parameters (temperature, max tokens)
- Feature flags

### Environment Variables
Create a `.env` file for sensitive configurations:
```env
HUGGINGFACE_API_TOKEN=your_token_here
MODEL_CACHE_DIR=./model_cache
DEBUG_MODE=false
```

## 🎯 Usage Examples

### Basic Chat
1. Type your message in the input area
2. Press "Send" or hit Enter
3. View the AI response in the chat area

### Advanced Features
1. **Change Models**: Use the sidebar to switch between AI models
2. **Upload Files**: Use the file upload feature to analyze documents
3. **Export Chats**: Download conversation history in multiple formats
4. **Customize Themes**: Switch between different UI themes

### Example Prompts
- "What is 25 * 4?"
- "Explain quantum computing in simple terms"
- "Write a Python function to sort a list"
- "What's the capital of France?"

## 🧪 Development

### Project Structure
The codebase is organized into logical modules:
- **Models**: Data structures and types
- **Services**: Business logic and external integrations
- **UI**: User interface components
- **Utils**: Helper functions and utilities
- **Config**: Configuration and settings

### Adding New Features
1. **New AI Model**: Extend `BaseModelService` in `ai_service.py`
2. **UI Components**: Add to `chat_interface.py`
3. **Configuration**: Update `settings.py`

### Testing
```bash
# Run tests (if implemented)
pytest

# Code formatting
black src/

# Linting
flake8 src/
```

## 🔍 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Check internet connection
   - Verify HuggingFace access
   - Try smaller models first

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility

3. **Performance Issues**
   - Use smaller models for faster responses
   - Limit conversation history length

### Debug Mode
Enable debug information in the UI to see detailed error messages and system status.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit** for the amazing framework
- **HuggingFace** for transformer models
- **Google** for FLAN-T5 models
- **Microsoft** for DialoGPT

## 🆕 What's New in v2.0

- ✅ Complete modular architecture
- ✅ Multiple AI model support
- ✅ Advanced UI with themes
- ✅ File upload functionality
- ✅ Enhanced session management
- ✅ Comprehensive export options
- ✅ Better error handling
- ✅ Code syntax highlighting
- ✅ Session statistics
- ✅ Improved documentation

---

**Happy Chatting! 🚀**
