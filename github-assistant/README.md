# GitHub MCP Assistant

A GitHub repository explorer powered by **MCP (Model Context Protocol)** and **Claude AI**. Ask questions about your repos in plain English — Claude autonomously decides which tools to call, fetches data from GitHub, and gives you a synthesized answer.

---

## What it does

- List all your GitHub repositories
- List and read files in any repo
- Search for keywords across a codebase
- Summarize what a repo does

**Example:**
```
You: summarize George-Soros-chatbot and find where the main logic is

[tool] Calling summarize_repo...
[tool] Calling list_all_files...
[tool] Calling read_file: financials_api/interface.py
[tool] Calling read_file: financials_api/rag_generator.py
[tool] Calling read_file: financials_api/rag_retriever.py

Claude: This is a RAG-based chatbot using ChromaDB + Gemini.
        The main logic lives in interface.py (SorosRAGChatbot class)...
```

---

## Project Structure

```
MCP/
├── server.py        # MCP server — defines all GitHub tools
├── client.py        # Manual CLI client — human picks tools from a menu
├── agent_main.py    # AI agent — Claude autonomously decides which tools to call
├── .env             # GitHub token + Anthropic API key (never committed)
└── requirements.txt
```

---

## How it works

### The tool layer — `server.py`
Built with **FastMCP**. Defines 6 tools that wrap the GitHub API:
`list_repos`, `list_files`, `list_all_files`, `read_file`, `search_code`, `summarize_repo`.

This file never changes. It just exposes capabilities and waits to be called.

### The manual client — `client.py`
A numbered menu CLI. The human decides which tool to call and when. No AI involved — this was the first version of the project.

### The AI agent — `agent_main.py`
The upgraded version. Uses the **Anthropic SDK** to give Claude the tool definitions. Claude reads your natural language question, decides which tools to call, calls them in sequence, reads the results, and synthesizes a final answer.

The core pattern is the **agentic loop:**
```
send question to Claude
        ↓
stop_reason == "tool_use"?  → run the tool → feed result back → loop
stop_reason == "end_turn"?  → print answer → done
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/RishikaBhatKuthyar/github-mcp-assistant.git
cd github-mcp-assistant
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file
```bash
touch .env
```

Add the following to `.env`:
```
GITHUB_TOKEN=your_github_personal_access_token
ANTHROPIC_API_KEY=your_anthropic_api_key
```

- Get a GitHub token at: github.com/settings/tokens (needs `repo` scope)
- Get an Anthropic API key at: console.anthropic.com/settings/api-keys

### 5. Set your Anthropic API key in the terminal
```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

---

## Running the project

### Run the AI agent (recommended)
```bash
python agent_main.py
```

Ask anything in natural language:
```
list my repos
summarize the JobPortal repo
find where authentication is handled in my-project
what does the README say in springAI?
```

### Run the manual client
```bash
python client.py
```

Pick tools from a numbered menu (no AI — human routes everything).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| MCP server | FastMCP (Python) |
| AI decision layer | Anthropic Claude (claude-opus-4-6) |
| GitHub integration | GitHub REST API |
| Runtime | Python 3.11 |