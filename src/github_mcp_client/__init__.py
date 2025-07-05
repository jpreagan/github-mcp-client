import asyncio
import logging
import sys

import click

from .chat import chat_loop
from .config import Config


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-m",
    "--model",
    required=True,
    help="OpenAI model (e.g., gpt-4.1, llama4-maverick-instruct-basic)",
)
@click.option("-v", "--verbose", count=True, help="Increase verbosity (‑v, ‑vv)")
def main(verbose: int, model: str) -> None:
    """GitHub MCP Client - Interactive client for GitHub MCP server"""
    level = logging.WARNING - min(verbose, 2) * 10
    logging.basicConfig(stream=sys.stderr, level=level, format="%(message)s")

    try:
        config = Config.from_env(model)
        asyncio.run(chat_loop(config))
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
