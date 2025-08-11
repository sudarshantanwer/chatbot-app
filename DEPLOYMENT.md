# 🚀 SmartBot Pro Deployment Guide

## Quick Start

### Option 1: Using the Setup Script (Recommended)
```bash
# Clone and navigate to the project
git clone <repository-url>
cd chatbot-app

# Run the setup script
./setup_and_run.sh

# For legacy version
./setup_and_run.sh --legacy
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run main.py --server.port 8502

# Or run the legacy version
streamlit run app.py --server.port 8502
```

### Option 3: Using Python Run Script
```bash
# Check dependencies
python run.py --check

# Run modular version
python run.py

# Run legacy version
python run.py --legacy
```

## Features Comparison

| Feature | Legacy App (app.py) | Modular App (main.py) |
|---------|--------------------|-----------------------|
| Basic Chat | ✅ | ✅ |
| AI Models | Single (FLAN-T5) | Multiple Models |
| UI Themes | ❌ | ✅ Multiple Themes |
| File Upload | ❌ | ✅ |
| Export Options | Basic TXT | TXT, JSON, MD |
| Session Stats | ❌ | ✅ |
| Code Highlighting | ❌ | ✅ |
| Modular Architecture | ❌ | ✅ |
| Error Handling | Basic | Advanced |
| Configuration | Hardcoded | Centralized |

## Environment Configuration

### Creating .env file
```bash
cp .env.template .env
# Edit .env with your settings
```

### Key Environment Variables
- `HUGGINGFACE_API_TOKEN`: Your HuggingFace API token
- `DEFAULT_MODEL`: Default AI model to use
- `DEBUG_MODE`: Enable debug logging
- `THEME`: Default UI theme

## Troubleshooting

### Port Already in Use
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or use a different port
streamlit run main.py --server.port 8503
```

### Model Loading Issues
1. Check internet connection
2. Verify HuggingFace access
3. Try smaller models first (flan-t5-small)
4. Clear model cache: `rm -rf model_cache/`

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Memory Issues
- Use smaller models (flan-t5-small instead of flan-t5-base)
- Reduce `MAX_CHAT_HISTORY` in settings
- Clear browser cache

## Performance Optimization

### For Development
- Use `flan-t5-small` for faster responses
- Enable debug mode for detailed logging
- Use local model cache

### For Production
- Use `flan-t5-base` or larger models
- Disable debug mode
- Configure proper caching
- Use GPU if available (set `USE_GPU=true`)

## Deployment Options

### Local Development
```bash
streamlit run main.py --server.port 8502
```

### Docker Deployment
```dockerfile
# Dockerfile (create this file)
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Cloud Deployment (Streamlit Cloud)
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy from GitHub repository
4. Set environment variables in Streamlit Cloud settings

## Security Considerations

1. **API Keys**: Store in environment variables, not code
2. **File Uploads**: Validate file types and sizes
3. **User Input**: Sanitize all user inputs
4. **HTTPS**: Use HTTPS in production
5. **Rate Limiting**: Implement rate limiting for API calls

## Monitoring and Logging

### Enable Logging
```python
# Add to .env
LOG_LEVEL=INFO
DEBUG_MODE=true
```

### Monitor Performance
- Check session statistics in the UI
- Monitor model response times
- Track memory usage

## Backup and Recovery

### Backup User Data
```bash
# Export chat sessions
cp -r user_data/ backup/user_data_$(date +%Y%m%d)/
```

### Model Cache Backup
```bash
# Backup model cache
tar -czf model_cache_backup.tar.gz model_cache/
```

## Support

### Getting Help
1. Check the troubleshooting section
2. Review application logs
3. Check GitHub issues
4. Contact support team

### Reporting Issues
Please include:
- Python version
- Operating system
- Error messages
- Steps to reproduce
- Screenshots (if UI related)

---

**Happy Chatting! 🤖**
