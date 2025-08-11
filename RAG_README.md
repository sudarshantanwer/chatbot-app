# 🤖 SmartBot Pro with RAG - Advanced AI Chatbot

A sophisticated AI chatbot with **RAG (Retrieval-Augmented Generation)** capabilities, persistent chat storage, and intelligent context enhancement. Built with Streamlit, HuggingFace Transformers, and ChromaDB.

## ✨ New RAG Features

### 🧠 **Intelligent Knowledge Base**
- **Save Conversations**: Save important chats with custom names and descriptions
- **Smart Retrieval**: Automatically finds relevant past conversations to enhance responses
- **Vector Search**: Uses semantic similarity to find the most relevant context
- **Chat Library**: Browse and reload previous conversations

### 💾 **Persistent Storage**
- **SQLite Database**: Stores all chat sessions and messages
- **Vector Database**: ChromaDB for semantic search and retrieval
- **Metadata**: Tracks conversation topics, timestamps, and context

### 🔍 **RAG Enhancement**
- **Context-Aware Responses**: Uses relevant past conversations to provide better answers
- **Knowledge Retrieval**: Searches through your entire chat history
- **Smart Prompting**: Automatically enhances queries with relevant context

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd chatbot-app

# Install dependencies (includes RAG packages)
pip install -r requirements.txt

# Run the application
streamlit run main.py --server.port 8502
```

### Or use the setup script:
```bash
./setup_and_run.sh
```

## 📖 How to Use RAG Features

### 1. **Save a Chat Session**
1. Have a conversation with the bot
2. Go to sidebar → "💾 Save Current Chat"
3. Enter a descriptive name (e.g., "Python Tutorial", "Math Problems")
4. Add an optional description
5. Click "Save Chat"

### 2. **Load Previous Conversations**
1. Go to sidebar → "📁 Saved Chats"
2. Browse your saved conversations
3. Click "Load" to continue an old conversation
4. Use the search box to find specific chats

### 3. **RAG in Action**
- When you ask a question, the system automatically:
  1. Searches your saved conversations for relevant context
  2. Includes that context in the AI prompt
  3. Provides more informed and consistent responses

### 4. **Manage Knowledge Base**
- **Rebuild Index**: Refresh the vector database
- **Test RAG**: Search your chat history manually
- **View Stats**: See how many chats are indexed

## 🎯 RAG Use Cases

### **Learning Assistant**
```
Save conversations about different topics:
- "Python Basics" 
- "Machine Learning Concepts"
- "Web Development Tips"

Later questions will reference your previous learning!
```

### **Project Support**
```
Save project-specific chats:
- "Database Design Discussion"
- "API Integration Help"
- "Bug Troubleshooting Session"

Get consistent project-aware assistance!
```

### **Personal Knowledge Base**
```
Build your own AI knowledge base:
- Save interesting conversations
- Ask follow-up questions later
- Get personalized responses based on your history
```

## 🔧 RAG Configuration

### Environment Variables
```env
# RAG Settings
ENABLE_RAG=true
RAG_MAX_RESULTS=5
RAG_CONTEXT_LENGTH=1000
VECTOR_DB_PATH=data/vector_db
CHAT_DB_PATH=data/chats.db
```

### Features Control
- **Enable/Disable RAG**: Toggle in sidebar
- **Search Quality**: Adjust max results and context length
- **Index Management**: Rebuild when needed

## 🏗️ Technical Architecture

### Database Layer
```
SQLite Database (chats.db)
├── chat_sessions (metadata)
└── messages (content)

ChromaDB (vector_db/)
├── Embeddings of all messages
└── Semantic search indices
```

### RAG Pipeline
```
User Query → Vector Search → Context Retrieval → Enhanced Prompt → AI Response
```

### Components
- **DatabaseService**: SQLite operations
- **RAGService**: Vector search and context building
- **SessionManager**: Chat management with RAG integration
- **AIService**: Enhanced prompt generation

## 📊 RAG Performance

### Metrics Available
- **Total Saved Chats**: Number of conversations stored
- **Indexed Documents**: Messages available for search
- **RAG Status**: Vector database availability
- **Search Relevance**: Similarity scores for retrieved context

### Optimization Tips
1. **Save Meaningful Chats**: Focus on substantial conversations
2. **Use Descriptive Names**: Helps with organization and search
3. **Regular Index Rebuilds**: Keep the vector database fresh
4. **Test Search**: Verify your knowledge base works

## 🔍 Troubleshooting

### RAG Not Working?
1. **Check Dependencies**: Ensure ChromaDB and sentence-transformers are installed
2. **Database Issues**: Check if `data/` directory exists and is writable
3. **Vector DB**: Try rebuilding the index
4. **Fallback Mode**: System uses text search if vector DB unavailable

### Performance Issues?
1. **Limit Chat History**: Don't save extremely long conversations
2. **Clean Old Chats**: Delete irrelevant saved conversations
3. **Reduce Context**: Lower `RAG_MAX_RESULTS` in settings

### Search Quality?
1. **Use Specific Names**: Save chats with descriptive titles
2. **Add Descriptions**: Help categorize conversations
3. **Test Queries**: Use the RAG test feature to verify search

## 🆚 Comparison: Before vs After RAG

| Feature | Basic Chatbot | RAG-Enhanced SmartBot Pro |
|---------|---------------|---------------------------|
| Memory | Session only | Persistent across sessions |
| Context | Current conversation | All saved conversations |
| Consistency | Limited | High (based on history) |
| Learning | None | Builds knowledge over time |
| Personalization | Basic | Deep (your conversation style) |
| Knowledge Retention | Lost on restart | Permanent storage |

## 🎯 Example RAG Workflow

```
Day 1: Ask about Python loops
→ Save as "Python Basics"

Day 5: Ask about list comprehensions  
→ RAG finds "Python Basics" conversation
→ AI knows you're learning Python
→ Gives more appropriate response level

Day 10: Ask about advanced Python patterns
→ RAG retrieves both previous Python conversations
→ AI provides advanced answer building on your history
```

## 🛠️ Advanced Features

### Batch Operations
- Import/export chat databases
- Bulk indexing of conversations
- Database backup and restore

### Search Enhancement
- Semantic similarity search
- Keyword-based filtering
- Time-range filtering
- Topic clustering

### Integration Ready
- API endpoints for external access
- Webhook support for automation
- Plugin architecture for extensions

## 📈 Roadmap

- [ ] **Multi-modal RAG**: Support for images and files
- [ ] **Smart Summarization**: Auto-generate chat summaries
- [ ] **Topic Detection**: Automatic conversation categorization
- [ ] **Export Knowledge Base**: Share your AI knowledge
- [ ] **Collaborative RAG**: Shared knowledge bases
- [ ] **Real-time Sync**: Cloud storage integration

---

**Transform your chatbot from a simple Q&A tool into a personalized AI assistant that learns and grows with you! 🚀**

## 🏃‍♂️ Getting Started Now

1. **Start a conversation** on any topic
2. **Save the chat** with a descriptive name
3. **Ask follow-up questions** later
4. **Watch as RAG enhances your experience!**

Your AI assistant will become smarter with every conversation you save. Building your personal knowledge base starts with your first saved chat! 💡
