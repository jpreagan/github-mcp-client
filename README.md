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
>>> Tell me about my GitHub profile.
2025-05-13 21:11:21,187 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-13 21:11:21,196 - INFO - 🔧 Calling tool: get_me with params: {}
2025-05-13 21:11:21,726 - INFO - ✅ Tool 'get_me' executed successfully
2025-05-13 21:11:24,406 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
You have 8 public repositories, 20 followers, and are following 1 user, with your account being created on December 27, 2018, and last updated on May 12, 2025.

>>> Create a private repo called my-cool-repo.
2025-05-13 21:11:28,857 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-13 21:11:28,860 - INFO - 🔧 Calling tool: create_repository with params: {"autoInit": true, "description": "null", "name": "my-cool-repo", "private": true}
2025-05-13 21:11:30,243 - INFO - ✅ Tool 'create_repository' executed successfully
2025-05-13 21:11:50,880 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
The private repository "my-cool-repo" has been created.

>>> What was the first issue filed in the vllm-project/vllm repo?
2025-05-13 21:11:57,573 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-13 21:11:57,576 - INFO - 🔧 Calling tool: get_issue with params: {"issue_number": 1, "owner": "vllm-project", "repo": "vllm"}
2025-05-13 21:11:57,894 - INFO - ✅ Tool 'get_issue' executed successfully
2025-05-13 21:12:02,042 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
The first issue filed in the vllm-project/vllm repo is "Fix a bug in tying OPT embeddings" and it was filed by WoosukKwon. The issue is closed and was merged on February 25, 2023.

>>> What is the most recent commit in that same project?
i2025-05-13 21:12:08,317 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
2025-05-13 21:12:08,320 - INFO - 🔧 Calling tool: list_commits with params: {"owner": "vllm-project", "page": 1, "perPage": 1, "repo": "vllm", "sha": "main"}
2025-05-13 21:12:08,706 - INFO - ✅ Tool 'list_commits' executed successfully
2025-05-13 21:12:17,107 - INFO - HTTP Request: POST https://api.together.xyz/v1/chat/completions "HTTP/1.1 200 OK"
he most recent commit in the vllm-project/vllm repo is "e7ef61c1f039a8eac98602a9e5ab7517027e7278". It was committed by majianpeng on May 14, 2025, and the commit message is "[Bugfix][Example] make lmcache v0 work. (#18051)".
```

## 📄 License

MIT - see [LICENSE](./LICENSE).

## 🧑‍💻 Contributing

Contributions welcome! Please open an issue or PR if you have suggestions or improvements.
