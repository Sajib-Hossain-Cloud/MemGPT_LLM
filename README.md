# Letta-Inspired Agent OS

A memory-powered AI agent operating system inspired by Letta, built with Python, FastAPI, and OpenAI.

## Features

- Long-term memory for AI agents
- Multiple memory types (facts, conversations, reflections)
- Context window management
- Agent Development Environment visualization
- Agent persistence
- RESTful API for agent interactions
- Tool integration system

## Project Structure
```
project/
├── app/                    # Main application code
│   ├── api/                # API endpoints and routes
│   ├── core/               # Core LLM service
│   ├── models/             # Agent and memory models
│   └── services/           # Agent service and visualization
├── config/                 # Configuration files
├── data/                   # Agent storage and visualizations
│   ├── agents/             # Persisted agent data
│   └── visualizations/     # Agent visualizations
├── docs/                   # Documentation
├── tests/                  # Test suite
└── utils/                  # Utility functions
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create a .env file with your OpenAI API key
echo "OPENAI_API=your_api_key_here" > .env
```

## Running the Application

Start the API server:
```bash
python run.py
```

The server will start at http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

## API Usage

### Creating an Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Assistant",
    "persona": "I am a helpful research assistant with expertise in scientific topics."
  }'
```

### Chatting with an Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/{agent_id}/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you help me understand quantum computing?"
  }'
```

### Listing Agents

```bash
curl -X GET "http://localhost:8000/api/v1/agents"
```

## How It Works

The system provides AI agents with:

1. **Memory Management**: Stores facts, conversations, and reflections in a persistent memory system.
2. **Context Optimization**: Selects relevant memories for each user query to maximize the context window usage.
3. **Agent Persistence**: Saves agent state between interactions for true long-term memory.
4. **Visualization**: Provides JSON data that can be visualized in a frontend application.

## Extending the System

- Add custom agent tools in `app/models/agent.py`
- Implement more sophisticated memory retrieval with embeddings
- Build a frontend for the Agent Development Environment
- Add more agent types with specialized capabilities

## License
MIT