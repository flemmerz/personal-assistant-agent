# zsh Setup Guide for Personal Assistant Agent

This guide provides zsh-specific optimizations and configurations for the Personal Assistant Agent.

## 🚀 Quick Setup for zsh Users

### 1. Clone and Setup
```zsh
git clone https://github.com/flemmerz/personal-assistant-agent.git
cd personal-assistant-agent
python setup.py
```

### 2. Add Helpful Aliases to ~/.zshrc

Add these lines to your `~/.zshrc` file for a better development experience:

```zsh
# Personal Assistant Agent - Development Aliases
# Add these to ~/.zshrc for faster development workflow

# Basic commands
alias pa-activate="source venv/bin/activate"
alias pa-test="python test_setup.py"
alias pa-run="python main.py"
alias pa-setup="python setup.py"
alias pa-db="python setup.py --database"

# Development workflow
alias pa-format="black . && isort ."
alias pa-lint="flake8 ."
alias pa-check="python test_setup.py && black . && isort . && flake8 ."

# Logs and monitoring
alias pa-logs="tail -f logs/*.log"
alias pa-status="python test_setup.py --db-only"

# Docker shortcuts
alias pa-docker-up="docker-compose up -d"
alias pa-docker-down="docker-compose down"
alias pa-docker-logs="docker-compose logs -f assistant_api"
alias pa-docker-build="docker-compose up -d --build"

# Git workflow for the project
alias pa-git-status="git status"
alias pa-git-push="git push origin"
alias pa-git-pull="git pull origin main"

# Quick project navigation (if you have multiple projects)
alias cdpa="cd ~/path/to/personal-assistant-agent"  # Update path as needed

# Environment management
alias pa-env-check="env | grep -E '(DATABASE|API_KEY|OPENAI|ANTHROPIC)'"
alias pa-env-edit="code .env"  # or vim .env, nano .env

# Function to quickly setup a new development session
pa-dev() {
    pa-activate
    echo "🚀 Personal Assistant Agent Development Environment"
    echo "📍 Current directory: $(pwd)"
    echo "🐍 Python: $(which python)"
    echo "📦 Virtual env: $VIRTUAL_ENV"
    echo ""
    echo "💡 Available commands:"
    echo "   pa-test     - Run tests"
    echo "   pa-run      - Start the agent"
    echo "   pa-logs     - View logs"
    echo "   pa-check    - Run full check (test + format + lint)"
}

# Function to quickly process a transcript
pa-process() {
    if [[ -z "$1" ]]; then
        echo "Usage: pa-process <transcript-file> [meeting-title]"
        return 1
    fi
    
    local transcript_file="$1"
    local meeting_title="${2:-Meeting $(date +%Y-%m-%d)}"
    
    pa-activate
    python -c "
import asyncio
from main import PersonalAssistantAgent

async def process():
    agent = PersonalAssistantAgent()
    await agent.initialize()
    items = await agent.process_new_transcript('$transcript_file', '$meeting_title')
    print(f'✅ Processed transcript: {len(items)} action items extracted')
    for i, item in enumerate(items, 1):
        print(f'  {i}. {item.assignee}: {item.description}')

asyncio.run(process())
"
}

# Function to check system status
pa-health() {
    echo "🔍 Personal Assistant Agent Health Check"
    echo "========================================"
    
    # Check if we're in the right directory
    if [[ ! -f "main.py" ]]; then
        echo "❌ Not in Personal Assistant Agent directory"
        return 1
    fi
    
    # Check virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo "✅ Virtual environment active: $VIRTUAL_ENV"
    else
        echo "⚠️  Virtual environment not active (run: pa-activate)"
    fi
    
    # Check Python version
    python_version=$(python --version 2>&1)
    echo "🐍 Python: $python_version"
    
    # Check database connection
    if python -c "import asyncpg; print('✅ asyncpg available')" 2>/dev/null; then
        echo "✅ Database client available"
    else
        echo "❌ Database client not available"
    fi
    
    # Check AI dependencies
    if python -c "import openai; print('✅ OpenAI client available')" 2>/dev/null; then
        echo "✅ OpenAI client available"
    elif python -c "import anthropic; print('✅ Anthropic client available')" 2>/dev/null; then
        echo "✅ Anthropic client available"
    else
        echo "⚠️  No AI client available"
    fi
    
    # Check environment file
    if [[ -f ".env" ]]; then
        echo "✅ Environment file exists"
    else
        echo "⚠️  Environment file missing (copy .env.example to .env)"
    fi
    
    echo ""
    echo "💡 Run 'pa-test' for comprehensive testing"
}
```

### 3. Reload Your zsh Configuration

```zsh
source ~/.zshrc
```

## 🎯 Quick Start Workflow

Now you can use these commands:

```zsh
# Navigate to your project
cdpa  # (if you set up the alias)

# Start development session
pa-dev

# Check system health
pa-health

# Process a transcript
pa-process data/sample_transcript.txt "Team Meeting"

# Run tests
pa-test

# Format and check code
pa-check

# View logs
pa-logs

# Docker workflow
pa-docker-up
pa-docker-logs
```

## 🔧 Advanced zsh Configuration

### Oh My Zsh Plugin

If you use Oh My Zsh, you can create a custom plugin:

```zsh
# Create plugin directory
mkdir -p ~/.oh-my-zsh/custom/plugins/personal-assistant

# Create plugin file
cat > ~/.oh-my-zsh/custom/plugins/personal-assistant/personal-assistant.plugin.zsh << 'EOF'
# Personal Assistant Agent Plugin for Oh My Zsh

# Aliases
alias pa-activate="source venv/bin/activate"
alias pa-test="python test_setup.py"
alias pa-run="python main.py"
alias pa-setup="python setup.py"
alias pa-check="python test_setup.py && black . && isort . && flake8 ."

# Auto-completion for pa-process command
_pa_process() {
    local -a transcript_files
    transcript_files=($(find . -name "*.txt" -type f))
    _describe 'transcript files' transcript_files
}
compdef _pa_process pa-process

# Set up environment when entering PA directory
chpwd_personal_assistant() {
    if [[ -f "main.py" && -f "setup.py" ]]; then
        if [[ -z "$VIRTUAL_ENV" && -d "venv" ]]; then
            echo "🤖 Personal Assistant Agent detected. Run 'pa-activate' to start."
        fi
    fi
}
add-zsh-hook chpwd chpwd_personal_assistant
EOF
```

Then add `personal-assistant` to your plugins in `~/.zshrc`:

```zsh
plugins=(... personal-assistant)
```

### Custom Prompt Integration

Add Personal Assistant Agent status to your prompt:

```zsh
# Add to ~/.zshrc
personal_assistant_prompt() {
    if [[ -f "main.py" && -f "setup.py" ]]; then
        if [[ -n "$VIRTUAL_ENV" ]]; then
            echo "%F{green}🤖%f"
        else
            echo "%F{yellow}🤖%f"
        fi
    fi
}

# Add to your existing PROMPT
PROMPT='$(personal_assistant_prompt)'$PROMPT
```

## 📊 Productivity Tips

### 1. Quick Environment Setup
```zsh
# Add this function to quickly set up environment variables
pa-env-setup() {
    echo "Setting up Personal Assistant Agent environment..."
    export DATABASE_URL="postgresql://username:password@localhost:5432/assistant_db"
    export OPENAI_API_KEY="your-key-here"
    echo "✅ Environment variables set for this session"
}
```

### 2. Transcript Processing Workflow
```zsh
# Process multiple transcripts at once
pa-process-batch() {
    for file in data/*.txt; do
        echo "Processing: $file"
        pa-process "$file" "$(basename "$file" .txt)"
    done
}
```

### 3. Development Workflow
```zsh
# Complete development check
pa-full-check() {
    echo "🔍 Running full development check..."
    pa-test && \
    pa-format && \
    pa-lint && \
    echo "✅ All checks passed!" || \
    echo "❌ Some checks failed"
}
```

### 4. Log Monitoring
```zsh
# Monitor logs with syntax highlighting (if you have bat installed)
pa-logs-fancy() {
    if command -v bat >/dev/null 2>&1; then
        tail -f logs/*.log | bat --language=log --style=plain
    else
        pa-logs
    fi
}
```

## 🐳 Docker Integration

### Docker Compose Shortcuts
```zsh
# Add these to your aliases section
alias pa-up="docker-compose up -d"
alias pa-down="docker-compose down"
alias pa-restart="docker-compose restart"
alias pa-rebuild="docker-compose up -d --build"
alias pa-shell="docker-compose exec assistant_api bash"
```

### Docker Development Workflow
```zsh
# Function for Docker development
pa-docker-dev() {
    echo "🐳 Starting Docker development environment..."
    pa-up
    echo "🔍 Checking services..."
    docker-compose ps
    echo "📝 To view logs: pa-docker-logs"
    echo "🛠️  To access shell: pa-shell"
}
```

## 🔍 Debugging Tools

### Quick Debugging
```zsh
# Function to quickly debug database issues
pa-debug-db() {
    echo "🔍 Database Debug Information"
    echo "DATABASE_URL: ${DATABASE_URL:-'Not set'}"
    
    if command -v pg_isready >/dev/null 2>&1; then
        pg_isready -d "$DATABASE_URL" && echo "✅ Database reachable" || echo "❌ Database unreachable"
    else
        echo "⚠️  pg_isready not available"
    fi
}

# Function to check AI API connectivity
pa-debug-ai() {
    echo "🤖 AI API Debug Information"
    echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+Set (hidden)} ${OPENAI_API_KEY:-Not set}"
    echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+Set (hidden)} ${ANTHROPIC_API_KEY:-Not set}"
    
    python -c "
try:
    import openai
    print('✅ OpenAI library available')
except ImportError:
    print('❌ OpenAI library not available')

try:
    import anthropic
    print('✅ Anthropic library available')
except ImportError:
    print('❌ Anthropic library not available')
"
}
```

## 📝 Final Notes

After setting up these aliases and functions:

1. **Reload your shell**: `source ~/.zshrc`
2. **Test the setup**: `pa-health`
3. **Start developing**: `pa-dev`

These configurations will significantly speed up your development workflow with the Personal Assistant Agent project!

For more advanced zsh features and customizations, check out:
- [Oh My Zsh](https://ohmyz.sh/)
- [Powerlevel10k](https://github.com/romkatv/powerlevel10k) theme
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)
- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting)