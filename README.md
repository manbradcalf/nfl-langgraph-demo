# Biz Agents

Multi-agent research workflow using LangGraph with local models.

## Features

- **NFL Agent**: Research NFL news with player validation against NFLVerse data
- **Market Research Agent**: Research technology adoption and market trends
- Shared node architecture for code reuse
- Entity extraction using GLiNER
- Summarization using Ollama LLM
- Markdown output generation

## Usage

```bash
# Interactive mode
uv run main.py

# Specify agent and query
uv run main.py --agent nfl "NFL injuries today"
uv run main.py -a market "AI adoption in healthcare"
```

## Requirements

- Python 3.10+
- Ollama with qwen3:8b model
- Dependencies managed by uv
