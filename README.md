# GitHub MCP Client

This project is a command-line chatbot demo that lets you interact with GitHub using natural language using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). It launches the [GitHub MCP Server](https://github.com/github/github-mcp-server) in Docker and connects to an OpenAI-compatible LLM.

## 🔧 Prerequisites

- Python ≥ 3.10
- Docker
- OpenAI compatible API key (e.g. Fireworks, Together, Groq, OpenAI)

## 🚀 Quick start

```bash
# clone & enter repo
git clone https://github.com/jpreagan/github-mcp-client.git
cd github-mcp-client

# optional: create virtual environment
python -m venv .venv && source .venv/bin/activate

# install deps (pip or uv)
pip install -e .
```

Create a file called **.env**:

```dotenv
OPENAI_API_KEY=sk-proj-XXXXXXXXXX
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_XXXXXXXXXX
```

Then run:

```bash
python -m github_mcp_client --model gpt-4.1
```

Or run on Fireworks:

```dotenv
OPENAI_BASE_URL=https://api.fireworks.ai/inference/v1
OPENAI_API_KEY=fw_XXXXXXXXXX
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_XXXXXXXXXX
```

Then run:

```bash
python -m github_mcp_client --model accounts/fireworks/models/llama4-maverick-instruct-basic
```

## 🧪 Example sessions

Let's start with a warmpup, which requires only a single tool call:

```
GitHub MCP Server running on stdio
>>> List five interesting facts about me on GitHub.
🔧 Calling tool: get_me with params: {}
✅ Tool 'get_me' executed successfully
Here are five interesting facts about your GitHub profile:

1. **Location**: You are based in Hilo, Hawaii, which likely provides a unique perspective to your work as an AI engineer.

2. **Personal Website**: You maintain a personal blog at [jpreagan.com](https://jpreagan.com/), where you might share insights related to your projects and interests.

3. **Interests**: You're not just focused on technology! You enjoy 80's music and udon noodles 🍜, showcasing a diverse set of interests.

4. **Followers**: You have an engaging presence on GitHub with 20 followers, which is a testament to your contributions and visibility in the community.

5. **Active Since**: You've been a part of the GitHub community since December 27, 2018, giving you several years of experience and involvement in open-source projects.
```

Now let's try a query that requires multiple tool calls using dynamic toolsets:

```
GitHub MCP Server running on stdio
>>> List my public repos.
🔧 Calling tool: get_me with params: {"reason": "to retrieve the authenticated user's username for listing their public repositories."}
✅ Tool 'get_me' executed successfully
🔧 Calling tool: search_repositories with params: {"query": "user:jpreagan is:public", "perPage": 100}
✅ Tool 'search_repositories' executed successfully
Here are your public repositories:

1. [**github-mcp-client**](https://github.com/jpreagan/github-mcp-client)
   - **Description:** Chatbot demo that lets an LLM handle GitHub tasks from the command line using the GitHub MCP Server 🤖🦐
   - **Language:** Python
   - **License:** MIT License

2. [**labs**](https://github.com/jpreagan/labs)
   - **Description:** A collection of practical experiments, benchmarks, and analyses exploring real-world behavior of AI systems and large language models.
   - **Language:** Python
   - **License:** MIT License

3. [**llmnop**](https://github.com/jpreagan/llmnop)
   - **Description:** A tool for measuring LLM performance metrics.
   - **Language:** Rust
   - **License:** MIT License

4. [**dotfiles**](https://github.com/jpreagan/dotfiles)
   - **Description:** My configuration files
   - **Language:** Lua
   - **License:** MIT License

Feel free to explore them!
```
