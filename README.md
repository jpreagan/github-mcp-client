# GitHub MCP Client

A minimal example of a simple command line chatbot that speaks the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), spins up the GitHub MCP server in Docker, and chats with an LLM that can decide when to call GitHub tools.

## 🔧 Prerequisites

- Python ≥ 3.10
- Docker
- OpenAI compatible API key (e.g. Groq, OpenAI, Together)

## 🚀 Quick start

```bash
# clone & enter repo
git clone https://github.com/jpreagan/github-mcp-client.git
cd github-mcp-client

# optional: create virtual environment
python -m venv .venv && source .venv/bin/activate

# install deps (pip or uv)
pip install -r requirements.txt
```

Create a file called **.env**:

```dotenv
LLM_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXX
```

Then run:

```bash
python main.py
```

Example interaction:

```
You: create a private repo called demo-mcp
Assistant: Repository **demo-mcp** created ✅ (private)
```

## 📄 License

MIT - see [LICENSE](./LICENSE).

## 🧑‍💻 Contributing

Contributions welcome! Please open an issue or PR if you have suggestions or improvements.
