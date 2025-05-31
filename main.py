# Personal Assistant Agent - Core Infrastructure
# This sets up the foundational components for your meeting transcript processing system

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
import logging
from pathlib import Path

# Configuration Management
@dataclass
class Config:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/assistant_db")
    
    # AI/LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4")
    AI_TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 1000
    
    # Google Workspace
    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
    GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    
    # Task Management
    AUTO_EXECUTE_THRESHOLD: float = 0.85
    HUMAN_REVIEW_REQUIRED: List[str] = None
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    def __post_init__(self):
        if self.HUMAN_REVIEW_REQUIRED is None:
            self.HUMAN_REVIEW_REQUIRED = ["legal_documents", "high_value_contracts", "external_communications"]

# Data Models
class TaskType(Enum):
    EMAIL_FOLLOW_UP = "email_follow_up"
    DOCUMENT_CREATION = "document_creation"
    MEETING_SCHEDULING = "meeting_scheduling"
    RESEARCH = "research"
    PHONE_CALL = "phone_call"
    REMINDER = "reminder"
    OTHER = "other"

class UrgencyLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"

@dataclass
class ActionItem:
    id: Optional[int] = None
    transcript_id: int = None
    assignee: str = ""
    description: str = ""
    task_type: TaskType = TaskType.OTHER
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM
    estimated_deadline: Optional[datetime] = None
    actual_deadline: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    automation_level: str = "manual"  # manual, semi_auto, full_auto
    context: Dict[str, Any] = None
    entities: Dict[str, Any] = None
    confidence_score: float = 0.0
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.entities is None:
            self.entities = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class MeetingTranscript:
    id: Optional[int] = None
    title: str = ""
    date: datetime = None
    participants: List[str] = None
    content: str = ""
    source: str = ""  # google_meet, fellow, tactiq, etc.
    source_file_path: str = ""
    metadata: Dict[str, Any] = None
    processed: bool = False
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.metadata is None:
            self.metadata = {}
        if self.date is None:
            self.date = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()

# Database Manager
class DatabaseManager:
    def __init__(self, config: Config):
        self.config = config
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool and create tables"""
        self.pool = await asyncpg.create_pool(self.config.DATABASE_URL)
        await self.create_tables()
        
    async def create_tables(self):
        """Create all necessary database tables"""
        async with self.pool.acquire() as conn:
            # Meeting transcripts table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS meeting_transcripts (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    date TIMESTAMP NOT NULL,
                    participants JSONB DEFAULT '[]',
                    content TEXT NOT NULL,
                    source VARCHAR(100) NOT NULL,
                    source_file_path VARCHAR(500),
                    metadata JSONB DEFAULT '{}',
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            # Action items table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS action_items (
                    id SERIAL PRIMARY KEY,
                    transcript_id INTEGER REFERENCES meeting_transcripts(id),
                    assignee VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    task_type VARCHAR(100) NOT NULL,
                    urgency_level VARCHAR(20) NOT NULL,
                    estimated_deadline DATE,
                    actual_deadline DATE,
                    status VARCHAR(50) DEFAULT 'pending',
                    automation_level VARCHAR(20) DEFAULT 'manual',
                    context JSONB DEFAULT '{}',
                    entities JSONB DEFAULT '{}',
                    confidence_score FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );
            ''')
            
            # Document templates table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS document_templates (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    placeholders JSONB DEFAULT '{}',
                    usage_count INTEGER DEFAULT 0,
                    success_rate FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            # Task execution log
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS task_execution_log (
                    id SERIAL PRIMARY KEY,
                    action_item_id INTEGER REFERENCES action_items(id),
                    execution_type VARCHAR(100) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    result JSONB DEFAULT '{}',
                    error_message TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
    async def insert_transcript(self, transcript: MeetingTranscript) -> int:
        """Insert a new meeting transcript"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow('''
                INSERT INTO meeting_transcripts 
                (title, date, participants, content, source, source_file_path, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            ''', transcript.title, transcript.date, json.dumps(transcript.participants),
            transcript.content, transcript.source, transcript.source_file_path,
            json.dumps(transcript.metadata))
            return result['id']
    
    async def insert_action_item(self, action_item: ActionItem) -> int:
        """Insert a new action item"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow('''
                INSERT INTO action_items 
                (transcript_id, assignee, description, task_type, urgency_level,
                 estimated_deadline, status, automation_level, context, entities, confidence_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id
            ''', action_item.transcript_id, action_item.assignee, action_item.description,
            action_item.task_type.value, action_item.urgency_level.value,
            action_item.estimated_deadline, action_item.status.value,
            action_item.automation_level, json.dumps(action_item.context),
            json.dumps(action_item.entities), action_item.confidence_score)
            return result['id']
    
    async def get_pending_action_items(self, assignee: str = None) -> List[Dict]:
        """Get all pending action items, optionally filtered by assignee"""
        async with self.pool.acquire() as conn:
            if assignee:
                query = '''
                    SELECT * FROM action_items 
                    WHERE status = 'pending' AND assignee = $1
                    ORDER BY urgency_level DESC, estimated_deadline ASC
                '''
                rows = await conn.fetch(query, assignee)
            else:
                query = '''
                    SELECT * FROM action_items 
                    WHERE status = 'pending'
                    ORDER BY urgency_level DESC, estimated_deadline ASC
                '''
                rows = await conn.fetch(query)
            
            return [dict(row) for row in rows]
    
    async def update_action_item_status(self, item_id: int, status: TaskStatus, completed_at: datetime = None):
        """Update action item status"""
        async with self.pool.acquire() as conn:
            if completed_at:
                await conn.execute('''
                    UPDATE action_items 
                    SET status = $1, completed_at = $2
                    WHERE id = $3
                ''', status.value, completed_at, item_id)
            else:
                await conn.execute('''
                    UPDATE action_items 
                    SET status = $1
                    WHERE id = $2
                ''', status.value, item_id)

# AI Client Manager
class AIClientManager:
    def __init__(self, config: Config):
        self.config = config
        self.client = None
        
    async def initialize(self):
        """Initialize AI client based on configuration"""
        if self.config.AI_MODEL.startswith("gpt"):
            import openai
            openai.api_key = self.config.OPENAI_API_KEY
            self.client = openai
        elif self.config.AI_MODEL.startswith("claude"):
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
    
    async def extract_action_items(self, transcript_text: str, meeting_metadata: Dict = None) -> List[ActionItem]:
        """Extract action items from transcript using AI"""
        
        system_prompt = """You are an expert meeting assistant. Analyze this transcript and extract action items.

For each action item, identify:
1. **Assignee**: Who is responsible (focus on "I will", "I'll", user's name)
2. **Task Description**: Clear, specific description
3. **Context**: Meeting context and background
4. **Urgency Level**: high/medium/low
5. **Task Type**: email_follow_up, document_creation, meeting_scheduling, research, phone_call, reminder, other
6. **Dependencies**: Any mentioned prerequisites
7. **Mentioned Entities**: People, companies, documents, deadlines

Return as JSON array with confidence scores for each item (0.0-1.0).

Example output:
[
  {
    "assignee": "John",
    "description": "Send NDA template to Acme Corp",
    "task_type": "document_creation",
    "urgency_level": "medium",
    "entities": {
      "company": "Acme Corp",
      "document_type": "NDA",
      "contact_person": "Sarah Johnson"
    },
    "context": "Discussed partnership opportunity with Acme Corp",
    "estimated_days_to_complete": 2,
    "confidence_score": 0.9
  }
]"""

        user_prompt = f"""
Meeting Transcript:
{transcript_text}

Meeting Metadata:
{json.dumps(meeting_metadata or {}, indent=2)}

Extract all action items from this transcript following the format specified.
"""

        try:
            if self.config.AI_MODEL.startswith("gpt"):
                response = await self.client.ChatCompletion.acreate(
                    model=self.config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.config.AI_TEMPERATURE,
                    max_tokens=self.config.MAX_TOKENS
                )
                content = response.choices[0].message.content
            else:
                # Claude API call
                response = await self.client.messages.create(
                    model=self.config.AI_MODEL,
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.AI_TEMPERATURE,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                content = response.content[0].text
            
            # Parse JSON response
            action_items_data = json.loads(content)
            action_items = []
            
            for item_data in action_items_data:
                # Convert days to deadline
                estimated_deadline = None
                if 'estimated_days_to_complete' in item_data:
                    days = item_data.get('estimated_days_to_complete', 3)
                    estimated_deadline = datetime.now() + timedelta(days=days)
                
                action_item = ActionItem(
                    assignee=item_data.get('assignee', ''),
                    description=item_data.get('description', ''),
                    task_type=TaskType(item_data.get('task_type', 'other')),
                    urgency_level=UrgencyLevel(item_data.get('urgency_level', 'medium')),
                    estimated_deadline=estimated_deadline,
                    entities=item_data.get('entities', {}),
                    context=item_data.get('context', {}),
                    confidence_score=item_data.get('confidence_score', 0.0)
                )
                action_items.append(action_item)
            
            return action_items
            
        except Exception as e:
            logging.error(f"Error extracting action items: {e}")
            return []

# Core Transcript Processor
class TranscriptProcessor:
    def __init__(self, config: Config, db_manager: DatabaseManager, ai_client: AIClientManager):
        self.config = config
        self.db = db_manager
        self.ai = ai_client
        
    async def process_transcript(self, transcript: MeetingTranscript) -> List[ActionItem]:
        """Main transcript processing pipeline"""
        try:
            # 1. Store transcript in database
            transcript_id = await self.db.insert_transcript(transcript)
            
            # 2. Extract action items using AI
            action_items = await self.ai.extract_action_items(
                transcript.content, 
                transcript.metadata
            )
            
            # 3. Store action items
            for action_item in action_items:
                action_item.transcript_id = transcript_id
                await self.db.insert_action_item(action_item)
            
            # 4. Mark transcript as processed
            async with self.db.pool.acquire() as conn:
                await conn.execute(
                    'UPDATE meeting_transcripts SET processed = TRUE WHERE id = $1',
                    transcript_id
                )
            
            logging.info(f"Processed transcript {transcript_id}, extracted {len(action_items)} action items")
            return action_items
            
        except Exception as e:
            logging.error(f"Error processing transcript: {e}")
            return []

# Main Application Class
class PersonalAssistantAgent:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.db = DatabaseManager(self.config)
        self.ai = AIClientManager(self.config)
        self.processor = TranscriptProcessor(self.config, self.db, self.ai)
        
    async def initialize(self):
        """Initialize all components"""
        await self.db.initialize()
        await self.ai.initialize()
        
    async def process_new_transcript(self, transcript_file_path: str, title: str = "", metadata: Dict = None) -> List[ActionItem]:
        """Process a new transcript file"""
        # Read transcript content
        with open(transcript_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create transcript object
        transcript = MeetingTranscript(
            title=title or f"Meeting {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            content=content,
            source="file_upload",
            source_file_path=transcript_file_path,
            metadata=metadata or {}
        )
        
        # Process transcript
        return await self.processor.process_transcript(transcript)
    
    async def get_pending_tasks(self, assignee: str = None) -> List[Dict]:
        """Get all pending action items"""
        return await self.db.get_pending_action_items(assignee)
    
    async def complete_task(self, task_id: int):
        """Mark a task as completed"""
        await self.db.update_action_item_status(
            task_id, 
            TaskStatus.COMPLETED, 
            datetime.utcnow()
        )

# Example usage and testing
async def main():
    """Example usage of the personal assistant agent"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize agent
    agent = PersonalAssistantAgent()
    await agent.initialize()
    
    # Example: Process a transcript file
    # transcript_path = "./sample_meeting_transcript.txt"
    # action_items = await agent.process_new_transcript(transcript_path, "Weekly Team Meeting")
    
    # Example: Get pending tasks
    # pending_tasks = await agent.get_pending_tasks()
    # print(f"Found {len(pending_tasks)} pending tasks")
    
    # Example: Complete a task
    # await agent.complete_task(1)
    
    print("Personal Assistant Agent initialized successfully!")
    print("Ready to process meeting transcripts and extract action items.")

if __name__ == "__main__":
    asyncio.run(main())