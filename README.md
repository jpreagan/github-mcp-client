# GitHub MCP Client

GitHub MCP Client is a command-line chatbot that lets you interact with GitHub using natural language using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). It launches the [GitHub MCP Server](https://github.com/github/github-mcp-server) in Docker and connects to an OpenAI-compatible LLM.

## 🔧 Prerequisites

- Python ≥ 3.10
- Docker
- OpenAI compatible API key (e.g. Together, Fireworks, Groq, OpenAI)

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
LLM_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXX
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXX
```

Then run:

```bash
python main.py
```

## 🧪 Example sessions

Let's start with a warmpup, which requires only a single tool call:

```
GitHub MCP Server running on stdio
>>> List five interesting facts about me on GitHub.
2025-05-16 17:25:53,392 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-16 17:25:53,399 - INFO - 🔧 Calling tool: get_me with params: {}
2025-05-16 17:25:53,848 - INFO - ✅ Tool 'get_me' executed successfully
2025-05-16 17:25:58,815 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
Sure, here are five interesting facts about you on GitHub:

1. **Username and Profile**: Your GitHub username is `jpreagan`, and you have a profile picture that represents you. You can be found at [this link](https://github.com/jpreagan).

2. **Location and Interests**: You are located in Hilo, Hawaii, and your bio mentions that you are an AI engineer who loves 80's music and udon noodles. You also have a personal website at [jpreagan.com](https://jpreagan.com/).

3. **Repositories and Gists**: You have 5 public repositories and no public gists. Additionally, you have 1 private repository.

4. **Followers and Following**: You have 20 followers and are following 1 person.

5. **Account History**: Your GitHub account was created on December 27, 2018, and it was last updated on May 16, 2025. You have two-factor authentication enabled, which enhances the security of your account.
```

Now let's try a query that requires multiple tool calls using dynamic toolsets:

```
GitHub MCP Server running on stdio
>>> List my public repos.
2025-05-16 17:18:53,033 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-16 17:18:53,042 - INFO - 🔧 Calling tool: get_me with params: {}
2025-05-16 17:18:53,462 - INFO - ✅ Tool 'get_me' executed successfully
2025-05-16 17:18:58,256 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-16 17:18:58,258 - INFO - 🔧 Calling tool: enable_toolset with params: {"toolset": "repos"}
2025-05-16 17:18:58,262 - INFO - ✅ Tool 'enable_toolset' executed successfully
2025-05-16 17:18:59,241 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-16 17:18:59,243 - INFO - 🔧 Calling tool: search_repositories with params: {"query": "user:jpreagan", "type": "public"}
2025-05-16 17:18:59,645 - INFO - ✅ Tool 'search_repositories' executed successfully
2025-05-16 17:19:04,193 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
Here are your public repositories:

1. **[github-mcp-client](https://github.com/jpreagan/github-mcp-client)**
   - Description: Chatbot demo that lets an LLM handle GitHub tasks from the command line using the GitHub MCP Server 🤖🐙
   - Language: Python
   - Topics: llm, mcp

2. **[llmnop](https://github.com/jpreagan/llmnop)**
   - Description: A tool for measuring LLM performance metrics.
   - Language: Rust
   - Topics: llm, performance-metrics

3. **[notebooks](https://github.com/jpreagan/notebooks)**
   - Description: A collection of Jupyter notebooks exploring large language models (LLMs)
   - Language: Jupyter Notebook
   - Topics: jupyter-notebook, large-language-models, python

4. **[dotfiles](https://github.com/jpreagan/dotfiles)**
   - Description: My configuration files
   - Language: Lua
   - Topics: bash, dotfiles, fish, zsh
```

## 📄 License

MIT - see [LICENSE](./LICENSE).

## 🧑‍💻 Contributing

Contributions welcome! Please open an issue or PR if you have suggestions or improvements.
