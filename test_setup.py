#!/usr/bin/env python3
"""
Test script to verify the Personal Assistant Agent setup
"""

import asyncio
import os
import sys
from datetime import datetime
import json

async def test_database_connection():
    """Test database connectivity"""
    print("🔍 Testing database connection...")
    try:
        from main import PersonalAssistantAgent
        agent = PersonalAssistantAgent()
        await agent.initialize()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_ai_client():
    """Test AI client initialization"""
    print("🤖 Testing AI client...")
    try:
        from main import AIClientManager, Config
        config = Config()
        
        if not config.OPENAI_API_KEY and not config.ANTHROPIC_API_KEY:
            print("⚠️  No AI API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
            return False
        
        ai_client = AIClientManager(config)
        await ai_client.initialize()
        print("✅ AI client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ AI client initialization failed: {e}")
        return False

async def test_transcript_processing():
    """Test transcript processing with sample data"""
    print("📝 Testing transcript processing...")
    try:
        from main import PersonalAssistantAgent, MeetingTranscript
        
        # Sample transcript content
        sample_content = """
Meeting: Test Meeting
Participants: John, Sarah

John: I'll send the proposal to the client by Friday.
Sarah: I need to schedule a follow-up meeting with them next week.
John: Can you also create a summary document of our discussion?
Sarah: Sure, I'll have that ready by Wednesday.
"""
        
        agent = PersonalAssistantAgent()
        await agent.initialize()
        
        # Create sample transcript
        transcript = MeetingTranscript(
            title="Test Meeting",
            content=sample_content,
            source="test",
            metadata={"test": True}
        )
        
        # Process transcript
        action_items = await agent.processor.process_transcript(transcript)
        
        print(f"✅ Processed transcript successfully, extracted {len(action_items)} action items")
        
        # Display extracted action items
        for i, item in enumerate(action_items, 1):
            print(f"   {i}. {item.assignee}: {item.description} ({item.task_type.value})")
        
        return True
    except Exception as e:
        print(f"❌ Transcript processing failed: {e}")
        return False

async def test_file_processing():
    """Test file-based transcript processing"""
    print("📁 Testing file processing...")
    try:
        sample_file = "data/sample_transcript.txt"
        
        if not os.path.exists(sample_file):
            print(f"⚠️  Sample file {sample_file} not found. Run setup.py first.")
            return False
        
        from main import PersonalAssistantAgent
        agent = PersonalAssistantAgent()
        await agent.initialize()
        
        action_items = await agent.process_new_transcript(
            sample_file, 
            "Sample Meeting",
            {"source": "test_file"}
        )
        
        print(f"✅ File processing successful, extracted {len(action_items)} action items")
        return True
    except Exception as e:
        print(f"❌ File processing failed: {e}")
        return False

async def test_task_management():
    """Test task retrieval and management"""
    print("📋 Testing task management...")
    try:
        from main import PersonalAssistantAgent
        agent = PersonalAssistantAgent()
        await agent.initialize()
        
        # Get pending tasks
        pending_tasks = await agent.get_pending_tasks()
        print(f"✅ Retrieved {len(pending_tasks)} pending tasks")
        
        # If there are tasks, test completing one
        if pending_tasks:
            task_id = pending_tasks[0]['id']
            await agent.complete_task(task_id)
            print(f"✅ Successfully marked task {task_id} as completed")
        
        return True
    except Exception as e:
        print(f"❌ Task management failed: {e}")
        return False

def test_environment_config():
    """Test environment configuration"""
    print("⚙️  Testing environment configuration...")
    
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please copy .env.example to .env and configure it.")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "DATABASE_URL",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration looks good")
    return True

async def run_comprehensive_test():
    """Run all tests"""
    print("🧪 Personal Assistant Agent - Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Environment Config", test_environment_config),
        ("Database Connection", test_database_connection),
        ("AI Client", test_ai_client),
        ("Transcript Processing", test_transcript_processing),
        ("File Processing", test_file_processing),
        ("Task Management", test_task_management),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Personal Assistant Agent is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Configure your meeting transcription tool (Fellow, Tactiq, etc.)")
        print("2. Set up Google Workspace integration")
        print("3. Start processing your meeting transcripts!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above and fix the issues.")
        print("💡 Common issues:")
        print("   - Missing API keys in .env file")
        print("   - Database not running or misconfigured")
        print("   - Missing dependencies")
    
    return passed == len(results)

def show_usage():
    """Show usage instructions"""
    print("Personal Assistant Agent - Test Suite")
    print("\nUsage:")
    print("  python test_setup.py [options]")
    print("\nOptions:")
    print("  --db-only       Test only database connection")
    print("  --ai-only       Test only AI client")
    print("  --no-ai         Skip AI-related tests")
    print("  --help, -h      Show this help message")

async def main():
    """Main test function"""
    if "--help" in sys.argv or "-h" in sys.argv:
        show_usage()
        return
    
    if "--db-only" in sys.argv:
        await test_database_connection()
    elif "--ai-only" in sys.argv:
        await test_ai_client()
    elif "--no-ai" in sys.argv:
        # Run tests without AI components
        test_environment_config()
        await test_database_connection()
        await test_task_management()
    else:
        # Run comprehensive test
        success = await run_comprehensive_test()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())