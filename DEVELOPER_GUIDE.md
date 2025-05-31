# Developer Guide

This guide helps developers get started with the Personal Assistant Agent codebase and contribute to the project.

## 🏗️ Architecture Overview

The Personal Assistant Agent is built with a modular, extensible architecture:

```
personal-assistant-agent/
├── main.py                    # Core application and entry point
├── models/                    # Data models and schemas
├── processors/                # Transcript and task processors
├── integrations/              # External service integrations
├── api/                       # FastAPI endpoints (future)
├── tests/                     # Test suite
└── docs/                      # Documentation
```

## 🚀 Development Setup

### 1. Clone and Setup Environment

```zsh
git clone https://github.com/flemmerz/personal-assistant-agent.git
cd personal-assistant-agent

# Run automated setup
python setup.py

# Or manual setup:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```zsh
cp .env.example .env
# Edit .env with your configuration
code .env  # or vim .env, nano .env
```

**Required environment variables:**
```zsh
export DATABASE_URL="postgresql://user:password@localhost:5432/assistant_db"
export OPENAI_API_KEY="sk-your-key-here"  # OR ANTHROPIC_API_KEY
```

### 3. Setup Database

```zsh
python setup.py --database
```

### 4. Run Tests

```zsh
python test_setup.py
```

## 🧠 Core Components

### Configuration Management
```python
from main import Config

config = Config()
# Automatically loads from environment variables
```

### Database Manager
```python
from main import DatabaseManager

db = DatabaseManager(config)
await db.initialize()
await db.insert_transcript(transcript)
```

### AI Client Manager
```python
from main import AIClientManager

ai = AIClientManager(config)
await ai.initialize()
action_items = await ai.extract_action_items(transcript_text)
```

### Transcript Processor
```python
from main import TranscriptProcessor

processor = TranscriptProcessor(config, db, ai)
action_items = await processor.process_transcript(transcript)
```

## 📝 Adding New Features

### Adding a New Task Type

1. **Extend the TaskType enum:**
```python
# In main.py
class TaskType(Enum):
    EMAIL_FOLLOW_UP = "email_follow_up"
    DOCUMENT_CREATION = "document_creation"
    YOUR_NEW_TYPE = "your_new_type"  # Add here
```

2. **Update the AI prompt:**
```python
# In AIClientManager.extract_action_items()
# Add your new task type to the prompt instructions
```

3. **Add processing logic:**
```python
# Create a new processor class
class YourNewTypeProcessor:
    async def process(self, action_item: ActionItem):
        # Your processing logic here
        pass
```

### Adding a New Integration

1. **Create integration class:**
```python
# integrations/your_service.py
class YourServiceIntegration:
    def __init__(self, config):
        self.config = config
        self.client = None
    
    async def initialize(self):
        # Setup API client
        pass
    
    async def send_action_item(self, action_item: ActionItem):
        # Send to your service
        pass
```

2. **Register integration:**
```python
# In main.py PersonalAssistantAgent class
def __init__(self):
    # ... existing code ...
    self.your_service = YourServiceIntegration(self.config)
```

### Adding New AI Models

1. **Update AIClientManager:**
```python
async def initialize(self):
    if self.config.AI_MODEL.startswith("your_model"):
        import your_ai_library
        self.client = your_ai_library.Client(api_key=self.config.YOUR_API_KEY)
```

2. **Add model-specific logic:**
```python
async def extract_action_items(self, transcript_text: str):
    if self.config.AI_MODEL.startswith("your_model"):
        # Your model-specific API call
        response = await self.client.generate(prompt)
    # ... handle response
```

## 🗄️ Database Schema

### Tables

**meeting_transcripts**
- `id` (Primary Key)
- `title` (VARCHAR)
- `date` (TIMESTAMP)
- `participants` (JSONB)
- `content` (TEXT)
- `source` (VARCHAR)
- `metadata` (JSONB)
- `processed` (BOOLEAN)

**action_items**
- `id` (Primary Key)
- `transcript_id` (Foreign Key)
- `assignee` (VARCHAR)
- `description` (TEXT)
- `task_type` (VARCHAR)
- `urgency_level` (VARCHAR)
- `deadline` (DATE)
- `status` (VARCHAR)
- `entities` (JSONB)
- `confidence_score` (FLOAT)

### Adding New Tables

```python
# In DatabaseManager.create_tables()
await conn.execute('''
    CREATE TABLE IF NOT EXISTS your_new_table (
        id SERIAL PRIMARY KEY,
        -- your columns here
    );
''')
```

## 🔌 Integration Patterns

### Webhook Integration
```python
# For services that send webhooks
from fastapi import FastAPI

app = FastAPI()

@app.post("/webhook/transcription")
async def handle_transcription_webhook(data: dict):
    agent = PersonalAssistantAgent()
    await agent.initialize()
    
    # Process webhook data
    transcript = create_transcript_from_webhook(data)
    action_items = await agent.processor.process_transcript(transcript)
    
    return {"status": "processed", "action_items": len(action_items)}
```

### Polling Integration
```python
# For services that require polling
import asyncio

async def poll_transcription_service():
    agent = PersonalAssistantAgent()
    await agent.initialize()
    
    while True:
        new_transcripts = await fetch_new_transcripts()
        for transcript in new_transcripts:
            await agent.processor.process_transcript(transcript)
        
        await asyncio.sleep(300)  # Poll every 5 minutes
```

## 🧪 Testing

### Unit Tests
```python
# tests/test_processors.py
import pytest
from main import TranscriptProcessor, Config

@pytest.mark.asyncio
async def test_action_item_extraction():
    config = Config()
    processor = TranscriptProcessor(config, mock_db, mock_ai)
    
    transcript = create_test_transcript()
    action_items = await processor.process_transcript(transcript)
    
    assert len(action_items) > 0
    assert action_items[0].assignee == "John"
```

### Integration Tests
```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_end_to_end_processing():
    agent = PersonalAssistantAgent()
    await agent.initialize()
    
    action_items = await agent.process_new_transcript(
        "tests/fixtures/sample_transcript.txt",
        "Test Meeting"
    )
    
    assert len(action_items) > 0
```

### Running Tests
```zsh
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_processors.py

# Run with coverage
python -m pytest --cov=main

# Run tests in verbose mode
python -m pytest -v

# Run tests and show local variables on failure
python -m pytest -l
```

## 📊 Performance Considerations

### Database Optimization
- Index frequently queried columns
- Use connection pooling
- Implement query pagination for large datasets

### AI Model Optimization
- Cache similar transcript patterns
- Batch process multiple transcripts
- Implement retry logic with exponential backoff

### Memory Management
- Stream large files instead of loading entirely
- Clean up temporary files
- Monitor memory usage in production

## 🚀 Deployment

### Local Development
```zsh
# Activate virtual environment
source venv/bin/activate

# Run the application
python main.py

# Run with environment variables
DATABASE_URL="postgresql://..." python main.py
```

### Docker Development
```zsh
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f assistant_api

# Run a one-off command
docker-compose run assistant_api python test_setup.py

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Production Deployment
```zsh
# Build and push Docker image
docker build -t personal-assistant-agent .
docker tag personal-assistant-agent your-registry/personal-assistant-agent
docker push your-registry/personal-assistant-agent

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Debugging
```zsh
# Connect to database
psql $DATABASE_URL

# View recent transcripts
psql $DATABASE_URL -c "SELECT id, title, processed FROM meeting_transcripts ORDER BY created_at DESC LIMIT 10;"

# View action items
psql $DATABASE_URL -c "SELECT assignee, description, status FROM action_items WHERE status = 'pending';"

# Check database connection
pg_isready -d $DATABASE_URL
```

### AI Response Debugging
```python
# Add detailed logging to AI client
print(f"AI Response: {response}")
print(f"Parsed Action Items: {action_items}")
```

### Environment Debugging
```zsh
# Check environment variables
echo $DATABASE_URL
echo $OPENAI_API_KEY

# Check virtual environment
echo $VIRTUAL_ENV
which python
which pip

# Check installed packages
pip list | grep -E "(openai|anthropic|asyncpg)"
```

## 📚 Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions under 50 lines

### Example Function
```python
async def process_transcript(
    self, 
    transcript: MeetingTranscript
) -> List[ActionItem]:
    """
    Process a meeting transcript and extract action items.
    
    Args:
        transcript: The meeting transcript to process
        
    Returns:
        List of extracted action items
        
    Raises:
        ProcessingError: If transcript processing fails
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logging.error(f"Failed to process transcript {transcript.id}: {e}")
        raise ProcessingError(f"Processing failed: {e}")
```

### Code Formatting
```zsh
# Format code with black
black .

# Sort imports with isort
isort .

# Check code style with flake8
flake8 .

# Type checking with mypy
mypy main.py
```

## 🤝 Contributing

### Pull Request Process
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python test_setup.py`
6. Submit a pull request

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive information in code
- [ ] Performance impact considered

## 📞 Getting Help

- **Issues**: Open a GitHub issue
- **Documentation**: Check the README and this guide
- **Testing**: Run `python test_setup.py` to diagnose problems
- **Community**: Join discussions in GitHub Issues

## 🔗 Useful Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Docker Documentation](https://docs.docker.com/)
- [zsh Documentation](https://zsh.sourceforge.io/Doc/)

## 🛠️ Development Tools

### Recommended zsh Configuration
```zsh
# Add to your ~/.zshrc for this project
alias pa-activate="source venv/bin/activate"
alias pa-test="python test_setup.py"
alias pa-run="python main.py"
alias pa-logs="tail -f logs/*.log"

# Function to quickly setup the project
pa-setup() {
    python setup.py
    python setup.py --database
    python test_setup.py
}
```

### VS Code Configuration
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.defaultProfile.osx": "zsh",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true
}
```