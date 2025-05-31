# Personal Assistant Agent - Quick Start Guide

A smart personal assistant that processes meeting transcripts and automatically extracts action items, suggests deadlines, and helps automate follow-up tasks.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (optional, for background tasks)
- OpenAI or Anthropic API key
- zsh (recommended shell)

### 1. Clone and Setup

```zsh
# Clone the repository
git clone https://github.com/flemmerz/personal-assistant-agent.git
cd personal-assistant-agent

# Run the setup script
python setup.py

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```zsh
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
# or use your preferred editor: code .env, vim .env
```

**Required settings in `.env`:**
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/assistant_db
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 3. Setup Database

```zsh
# Automatic setup
python setup.py --database

# Or manually create database and run:
python -c "import asyncio; from main import PersonalAssistantAgent; asyncio.run(PersonalAssistantAgent().initialize())"
```

### 4. Test Your Setup

```zsh
python test_setup.py
```

### 5. Process Your First Transcript

```python
import asyncio
from main import PersonalAssistantAgent

async def test_transcript():
    agent = PersonalAssistantAgent()
    await agent.initialize()
    
    # Process a transcript file
    action_items = await agent.process_new_transcript(
        "path/to/your/transcript.txt", 
        "Meeting Title"
    )
    
    print(f"Extracted {len(action_items)} action items:")
    for item in action_items:
        print(f"- {item.assignee}: {item.description}")

asyncio.run(test_transcript())
```

## 📋 Features Implemented

### ✅ Core Infrastructure (Phase 1)
- **Database Setup**: PostgreSQL with proper schema for transcripts and action items
- **AI Integration**: OpenAI GPT-4 or Anthropic Claude for intelligent extraction
- **Transcript Processing**: Automated pipeline from text to structured action items
- **Task Management**: Store, retrieve, and update action items

### 🔧 What You Get
- **Smart Action Item Extraction**: AI analyzes meeting transcripts and identifies:
  - Who is responsible for each task
  - Task descriptions and context
  - Urgency levels and estimated deadlines
  - Task types (email, document creation, meetings, etc.)
  - Mentioned entities (people, companies, documents)

- **Confidence Scoring**: Each extracted action item includes a confidence score
- **Flexible Input**: Process files or direct text input
- **Database Storage**: All transcripts and action items stored with full search capability
- **Extensible Architecture**: Ready for automation plugins and integrations

## 📊 Using the System

### Process a Meeting Transcript

```python
from main import PersonalAssistantAgent

agent = PersonalAssistantAgent()
await agent.initialize()

# From file
action_items = await agent.process_new_transcript(
    "meeting_transcript.txt",
    "Weekly Team Meeting",
    {"meeting_type": "internal", "department": "engineering"}
)

# View extracted action items
for item in action_items:
    print(f"{item.assignee}: {item.description}")
    print(f"  Type: {item.task_type.value}")
    print(f"  Urgency: {item.urgency_level.value}")
    print(f"  Deadline: {item.estimated_deadline}")
    print(f"  Confidence: {item.confidence_score}")
```

### Get Your Pending Tasks

```python
# Get all pending tasks
pending = await agent.get_pending_tasks()

# Get tasks for specific person
my_tasks = await agent.get_pending_tasks("John Smith")

# Complete a task
await agent.complete_task(task_id)
```

## 🔗 Integration with Meeting Tools

### Google Meet + Google Drive
```zsh
# The system can automatically pull transcripts from Google Drive
# Set GOOGLE_DRIVE_FOLDER_ID in .env to your transcript folder
```

### Fellow.app Integration
```zsh
# Add Fellow API credentials to .env
echo "FELLOW_API_KEY=your-api-key" >> .env
echo "FELLOW_WORKSPACE_ID=your-workspace-id" >> .env

# Fellow transcripts will be automatically processed
```

### Tactiq Integration
```zsh
# Add Tactiq webhook endpoint or API integration
# Transcripts are processed as they're created
```

## 🐳 Docker Deployment

```zsh
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f assistant_api

# Access the API at http://localhost:8000

# Stop services
docker-compose down
```

## 📁 Project Structure

```
personal-assistant-agent/
├── main.py                 # Core application code
├── setup.py               # Setup and installation script
├── test_setup.py          # Test and verification script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── docker-compose.yml    # Docker deployment
├── data/                 # Sample files and data
│   ├── sample_transcript.txt
│   └── config_sample.json
├── uploads/              # Uploaded transcript files
├── templates/            # Document templates
├── logs/                 # Application logs
└── backups/             # Database backups
```

## 🔧 Development and Customization

### Adding New Task Types

```python
# Extend the TaskType enum in main.py
class TaskType(Enum):
    EMAIL_FOLLOW_UP = "email_follow_up"
    DOCUMENT_CREATION = "document_creation"
    YOUR_CUSTOM_TYPE = "your_custom_type"  # Add here
```

### Customizing AI Prompts

```python
# Modify the system_prompt in AIClientManager.extract_action_items()
system_prompt = """
Your custom instructions for the AI...
Focus on extracting specific types of tasks relevant to your workflow.
"""
```

### Adding Integrations

```python
# Create new integration classes
class SlackIntegration:
    async def send_reminder(self, task):
        # Send task reminder to Slack
        pass

class CalendarIntegration:
    async def create_reminder(self, task):
        # Create calendar reminder
        pass
```

## 🚧 Next Steps (Roadmap Implementation)

1. **Phase 2**: Task Classification & Automation Framework
2. **Phase 3**: Document & Email Automation
3. **Phase 4**: Integration Layer (Google Workspace, CRM, etc.)
4. **Phase 5**: Intelligent Reminder & Notification System
5. **Phase 6**: Learning & Optimization

## 📝 Sample Transcript Format

Your transcripts can be in any text format. The AI is smart enough to handle various formats:

```
Meeting: Weekly Team Sync
Date: 2024-01-15
Participants: John Smith, Sarah Johnson

John: I'll send the proposal to Acme Corp by Wednesday.
Sarah: I need to schedule a follow-up meeting with them.
John: Can you also create the NDA document?
Sarah: Sure, I'll have that ready by Friday.
```

## 🐛 Troubleshooting

### Database Connection Issues
```zsh
# Check if PostgreSQL is running
pg_isready

# Reset database
python setup.py --database

# Connect to database directly
psql $DATABASE_URL
```

### AI API Issues
```zsh
# Test AI connection
python test_setup.py --ai-only

# Check API key in .env file
grep "API_KEY" .env
```

### Permission Issues
```zsh
# Make sure all directories are writable
chmod 755 uploads/ templates/ logs/

# Check Python virtual environment
which python
echo $VIRTUAL_ENV
```

### Virtual Environment Issues
```zsh
# If you encounter activation issues, try:
source venv/bin/activate

# Or if using conda:
conda activate personal-assistant

# Verify Python path
which python
python --version
```

## 📞 Support

- Run `python test_setup.py` to diagnose issues
- Check logs in `logs/` directory
- Ensure all required environment variables are set
- Verify database connectivity and API keys

## 🎯 What's Working Now

✅ **Extract action items from meeting transcripts**  
✅ **Identify assignees, deadlines, and task types**  
✅ **Store and retrieve tasks from database**  
✅ **Confidence scoring for extracted items**  
✅ **Support for multiple AI providers (OpenAI/Anthropic)**  
✅ **Docker deployment ready**  
✅ **Extensible architecture for future automation**  

Ready to process your meeting transcripts and never miss an action item again! 🚀