#!/usr/bin/env python3
"""
Personal Assistant Agent Setup Script
This script helps you set up the development environment and database.
"""

import os
import sys
import subprocess
import asyncio
import asyncpg
from pathlib import Path
import json

def run_command(command, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error output: {result.stderr}")
        sys.exit(1)
    return result

def check_requirements():
    """Check if required software is installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print("✅ Python version OK")
    
    # Check if PostgreSQL is available
    result = run_command("psql --version", check=False)
    if result.returncode != 0:
        print("⚠️  PostgreSQL not found. Please install PostgreSQL.")
        print("   On macOS: brew install postgresql")
        print("   On Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        print("   On Windows: Download from https://www.postgresql.org/download/")
    else:
        print("✅ PostgreSQL available")
    
    # Check if Redis is available
    result = run_command("redis-server --version", check=False)
    if result.returncode != 0:
        print("⚠️  Redis not found. Please install Redis.")
        print("   On macOS: brew install redis")
        print("   On Ubuntu: sudo apt-get install redis-server")
        print("   On Windows: Download from https://redis.io/download")
    else:
        print("✅ Redis available")

def setup_virtual_environment():
    """Set up Python virtual environment"""
    print("\n🐍 Setting up virtual environment...")
    
    if not os.path.exists("venv"):
        run_command("python -m venv venv")
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment instructions
    if os.name == 'nt':  # Windows
        activate_cmd = ".\\venv\\Scripts\\activate"
    else:  # Unix/MacOS
        activate_cmd = "source venv/bin/activate"
    
    print(f"📝 To activate the virtual environment, run: {activate_cmd}")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Determine pip command
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    
    if not os.path.exists(pip_cmd.split('/')[0] if '/' in pip_cmd else pip_cmd.split('\\')[0]):
        print("❌ Virtual environment not found. Please run setup_virtual_environment() first.")
        return
    
    run_command(f"{pip_cmd} install --upgrade pip")
    run_command(f"{pip_cmd} install -r requirements.txt")
    print("✅ Dependencies installed")

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Setting up environment configuration...")
    
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            run_command("cp .env.example .env")
            print("✅ .env file created from template")
            print("📝 Please edit .env file with your actual configuration values")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "uploads",
        "templates",
        "backups",
        "logs",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/")

async def setup_database():
    """Set up the database"""
    print("\n🗄️  Setting up database...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/assistant_db")
    
    try:
        # Parse database URL to get connection details
        import urllib.parse as urlparse
        url = urlparse.urlparse(database_url)
        
        # Connect to PostgreSQL (default database)
        default_db_url = f"postgresql://{url.username}:{url.password}@{url.hostname}:{url.port}/postgres"
        
        conn = await asyncpg.connect(default_db_url)
        
        # Create database if it doesn't exist
        db_name = url.path[1:]  # Remove leading slash
        try:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created")
        except asyncpg.exceptions.DuplicateDatabaseError:
            print(f"✅ Database '{db_name}' already exists")
        
        await conn.close()
        
        # Now connect to the actual database and run the schema
        print("🔧 Setting up database schema...")
        from main import PersonalAssistantAgent
        agent = PersonalAssistantAgent()
        await agent.initialize()
        print("✅ Database schema created")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("Please ensure PostgreSQL is running and check your DATABASE_URL in .env")

def create_sample_files():
    """Create sample files for testing"""
    print("\n📋 Creating sample files...")
    
    # Sample meeting transcript
    sample_transcript = """
Meeting: Weekly Team Sync
Date: 2024-01-15
Participants: John Smith, Sarah Johnson, Mike Chen

John: Alright, let's start with the project updates. Sarah, how's the client onboarding going?

Sarah: Good progress! I've completed the initial requirements gathering with Acme Corp. I need to send them our standard NDA by Wednesday so they can review it before our next meeting. Mike, can you help me find the latest template?

Mike: Absolutely! I'll send you the updated NDA template right after this meeting. Also, I need to schedule a technical review session with their team next week. John, are you available Thursday afternoon?

John: Thursday works for me. I'll also follow up with the legal team about the contract terms we discussed. Sarah, please remind me to review the pricing proposal before we send it to Acme Corp.

Sarah: Will do! I'll also create a project timeline document to share with the client. Should be ready by Friday.

Mike: Perfect. One more thing - I need to research their current tech stack to prepare for the integration discussion. I'll have that analysis done by Monday.

John: Great work everyone. Sarah, don't forget to send that follow-up email to schedule our next client meeting.

Sarah: I'll send that today. Thanks everyone!
"""
    
    with open("data/sample_transcript.txt", "w") as f:
        f.write(sample_transcript)
    print("✅ Sample transcript created at data/sample_transcript.txt")
    
    # Sample configuration
    config_sample = {
        "user_preferences": {
            "name": "John Smith",
            "email": "john@company.com",
            "timezone": "America/New_York",
            "reminder_preferences": {
                "email": True,
                "slack": False,
                "default_reminder_time": "09:00"
            }
        },
        "automation_rules": {
            "auto_execute_threshold": 0.85,
            "require_approval": ["legal_documents", "external_emails"],
            "auto_reminder_days": 3
        }
    }
    
    with open("data/config_sample.json", "w") as f:
        json.dump(config_sample, f, indent=2)
    print("✅ Sample configuration created at data/config_sample.json")

def main():
    """Main setup function"""
    print("🚀 Personal Assistant Agent Setup")
    print("=" * 40)
    
    try:
        check_requirements()
        setup_virtual_environment()
        install_dependencies()
        create_env_file()
        create_directories()
        create_sample_files()
        
        print("\n✅ Basic setup complete!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your configuration")
        print("2. Set up your database: python setup.py --database")
        print("3. Test the setup: python main.py")
        
        # Check if user wants to set up database now
        if "--database" in sys.argv:
            asyncio.run(setup_database())
        
        print("\n🎉 Setup complete! Your personal assistant agent is ready to use.")
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()