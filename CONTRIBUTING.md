# Contributing to Personal Assistant Agent

Thank you for your interest in contributing to the Personal Assistant Agent! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
- Check the [existing issues](https://github.com/flemmerz/personal-assistant-agent/issues) to avoid duplicates
- Run `python test_setup.py` to verify your setup is correct

**When submitting a bug report, include:**
- Clear description of the issue
- Steps to reproduce the behavior
- Expected vs. actual behavior
- Environment details (OS, Python version, shell type)
- Relevant logs or error messages

### Suggesting Features

**Before suggesting a feature:**
- Check the [roadmap](README.md#next-steps-roadmap-implementation) to see if it's already planned
- Search existing issues for similar suggestions

**When suggesting a feature:**
- Clearly describe the feature and its benefits
- Provide use cases and examples
- Consider implementation complexity
- Discuss potential alternatives

### Contributing Code

#### Development Setup

1. **Fork the repository**
   ```zsh
   git clone https://github.com/your-username/personal-assistant-agent.git
   cd personal-assistant-agent
   ```

2. **Set up development environment**
   ```zsh
   python setup.py
   python setup.py --database
   python test_setup.py
   ```

3. **Create a feature branch**
   ```zsh
   git checkout -b feature/your-feature-name
   ```

#### Code Guidelines

**Python Style:**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible

**Example of good code style:**
```python
async def extract_action_items(
    self, 
    transcript_text: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> List[ActionItem]:
    """
    Extract action items from a meeting transcript using AI.
    
    Args:
        transcript_text: The raw transcript content
        metadata: Optional meeting metadata
        
    Returns:
        List of extracted action items with confidence scores
        
    Raises:
        AIProcessingError: If AI processing fails
    """
    if not transcript_text.strip():
        raise ValueError("Transcript text cannot be empty")
    
    # Implementation here...
```

**Database Guidelines:**
- Use async/await for all database operations
- Handle connection errors gracefully
- Use parameterized queries to prevent SQL injection
- Include proper foreign key constraints

**AI Integration Guidelines:**
- Handle API rate limits and errors
- Validate AI responses before processing
- Include confidence scores for extracted data
- Provide fallback behavior for AI failures

#### Testing

**Writing Tests:**
```python
import pytest
from main import PersonalAssistantAgent

@pytest.mark.asyncio
async def test_action_item_extraction():
    """Test that action items are correctly extracted from transcripts."""
    agent = PersonalAssistantAgent()
    await agent.initialize()
    
    # Test with sample transcript
    action_items = await agent.process_new_transcript(
        "data/sample_transcript.txt",
        "Test Meeting"
    )
    
    assert len(action_items) > 0
    assert all(item.confidence_score > 0.5 for item in action_items)
```

**Running Tests:**
```zsh
# Run setup verification
python test_setup.py

# Run unit tests (when available)
python -m pytest tests/

# Run specific test
python -m pytest tests/test_processors.py::test_action_item_extraction

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=main
```

#### Documentation

**Code Documentation:**
- Write clear docstrings for all public APIs
- Include examples in docstrings when helpful
- Document complex algorithms and business logic
- Update the README if adding major features

**API Documentation:**
```python
class TaskProcessor:
    """Processes different types of tasks extracted from meetings.
    
    This class handles the automation and execution of various task types
    including email follow-ups, document creation, and meeting scheduling.
    
    Example:
        >>> processor = TaskProcessor(config)
        >>> await processor.process_task(action_item)
    """
    
    async def process_task(self, action_item: ActionItem) -> TaskResult:
        """Process a single action item.
        
        Args:
            action_item: The action item to process
            
        Returns:
            TaskResult containing execution status and results
            
        Raises:
            TaskProcessingError: If task processing fails
        """
```

#### Pull Request Process

1. **Before submitting:**
   ```zsh
   # Ensure all tests pass
   python test_setup.py
   
   # Run code formatting
   black .
   isort .
   
   # Check for issues
   flake8 .
   ```

2. **Pull Request Description:**
   ```markdown
   ## Description
   Brief description of changes made.
   
   ## Type of Change
   - [ ] Bug fix (non-breaking change which fixes an issue)
   - [ ] New feature (non-breaking change which adds functionality)
   - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
   - [ ] Documentation update
   
   ## Testing
   - [ ] Tests pass locally with my changes
   - [ ] I have added tests that prove my fix is effective or that my feature works
   
   ## Checklist
   - [ ] My code follows the style guidelines of this project
   - [ ] I have performed a self-review of my own code
   - [ ] I have commented my code, particularly in hard-to-understand areas
   - [ ] I have made corresponding changes to the documentation
   ```

3. **Review Process:**
   - All PRs require at least one review
   - Address feedback promptly
   - Keep PRs focused and reasonably sized
   - Rebase and resolve conflicts as needed

## 🏗️ Architecture Guidelines

### Adding New Integrations

When adding support for new meeting transcription services:

1. **Create integration module:**
   ```python
   # integrations/your_service.py
   class YourServiceIntegration:
       async def fetch_transcripts(self) -> List[MeetingTranscript]:
           """Fetch new transcripts from the service."""
           pass
   ```

2. **Add configuration:**
   ```python
   # In Config class
   YOUR_SERVICE_API_KEY: str = os.getenv("YOUR_SERVICE_API_KEY", "")
   ```

3. **Register in main application:**
   ```python
   # In PersonalAssistantAgent.__init__
   if self.config.YOUR_SERVICE_API_KEY:
       self.your_service = YourServiceIntegration(self.config)
   ```

### Adding New Task Types

1. **Extend enum:**
   ```python
   class TaskType(Enum):
       YOUR_NEW_TYPE = "your_new_type"
   ```

2. **Create processor:**
   ```python
   class YourTaskProcessor:
       async def process(self, action_item: ActionItem) -> TaskResult:
           """Process your specific task type."""
           pass
   ```

3. **Update AI prompts:**
   - Add the new task type to extraction prompts
   - Include examples in the prompt template

### Database Schema Changes

1. **Create migration script:**
   ```python
   # migrations/add_your_table.py
   async def upgrade(connection):
       await connection.execute('''
           CREATE TABLE your_new_table (
               id SERIAL PRIMARY KEY,
               -- your columns
           );
       ''')
   ```

2. **Update DatabaseManager:**
   ```python
   # Add to create_tables method
   await conn.execute('''CREATE TABLE IF NOT EXISTS...''')
   ```

## 🧪 Testing Guidelines

### Test Categories

**Unit Tests:**
- Test individual functions and methods
- Mock external dependencies
- Focus on business logic

**Integration Tests:**
- Test component interactions
- Use test database
- Test AI integration with mock responses

**End-to-End Tests:**
- Test complete workflows
- Use real (but test) data
- Verify database state changes

### Test Data

**Creating Test Fixtures:**
```python
# tests/fixtures.py
def create_test_transcript() -> MeetingTranscript:
    return MeetingTranscript(
        title="Test Meeting",
        content="John: I'll send the report by Friday.",
        participants=["John", "Sarah"],
        metadata={"test": True}
    )
```

**Mock External Services:**
```python
# tests/mocks.py
class MockAIClient:
    async def extract_action_items(self, text: str) -> List[ActionItem]:
        return [
            ActionItem(
                assignee="John",
                description="Send report",
                confidence_score=0.9
            )
        ]
```

## 📋 Code Review Checklist

### For Reviewers

**Functionality:**
- [ ] Code solves the intended problem
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance impact is acceptable

**Code Quality:**
- [ ] Code is readable and well-organized
- [ ] Functions have single responsibilities
- [ ] Variable names are descriptive
- [ ] Comments explain complex logic

**Testing:**
- [ ] Tests cover new functionality
- [ ] Tests are meaningful and not just for coverage
- [ ] Mock usage is appropriate
- [ ] Test data is realistic

**Documentation:**
- [ ] Public APIs are documented
- [ ] README is updated if needed
- [ ] Breaking changes are noted

### For Contributors

**Before Requesting Review:**
```zsh
# Checklist commands
python test_setup.py          # All tests pass
black . && isort .            # Code formatting
flake8 .                      # Linting
git diff --name-only          # Review changed files
```

## 🚀 Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
```zsh
# Update version and create release
git tag v1.0.0
git push origin v1.0.0

# Build and test
docker build -t personal-assistant-agent:v1.0.0 .
python test_setup.py
```

## 💬 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Celebrate contributions of all sizes

### Communication
- Use GitHub Issues for bug reports and feature requests
- Use Pull Requests for code contributions
- Be patient with response times
- Provide context in your communications

## 📚 Resources

### Learning Materials
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Tools
- **IDE**: VS Code with Python extension
- **Database**: pgAdmin or psql
- **API Testing**: Postman or curl
- **Code Quality**: black, flake8, mypy

## ❓ Getting Help

**For development questions:**
- Check the [Developer Guide](DEVELOPER_GUIDE.md)
- Search existing GitHub Issues
- Create a new issue with the "question" label

**For setup issues:**
- Run `python test_setup.py` for diagnostics
- Check the troubleshooting section in README
- Verify your environment configuration

**For feature discussions:**
- Open a GitHub Issue with the "enhancement" label
- Provide clear use cases and requirements
- Be open to feedback and alternative approaches

## 🛠️ zsh Users - Helpful Aliases

Add these to your `~/.zshrc` for faster development:

```zsh
# Personal Assistant Agent aliases
alias pa-activate="source venv/bin/activate"
alias pa-test="python test_setup.py"
alias pa-run="python main.py"
alias pa-setup="python setup.py"
alias pa-db="python setup.py --database"
alias pa-logs="tail -f logs/*.log"

# Development workflow
alias pa-format="black . && isort ."
alias pa-lint="flake8 ."
alias pa-check="python test_setup.py && black . && isort . && flake8 ."

# Docker shortcuts
alias pa-docker-up="docker-compose up -d"
alias pa-docker-down="docker-compose down"
alias pa-docker-logs="docker-compose logs -f assistant_api"

# Git shortcuts for the project
alias pa-status="git status"
alias pa-push="git push origin"
alias pa-pull="git pull origin main"
```

Then reload your configuration:
```zsh
source ~/.zshrc
```

Thank you for contributing to Personal Assistant Agent! 🎉