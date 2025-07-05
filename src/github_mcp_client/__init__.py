import asyncio
import logging
import sys

import click

from .client import chat_loop


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-m", "--model", default="gpt-4.1", show_default=True, help="OpenAI model"
)
@click.option("-v", "--verbose", count=True, help="Increase verbosity (‑v, ‑vv)")
def main(verbose: int, model: str) -> None:
    """GitHub MCP Client - Interactive client for GitHub MCP server"""
    level = logging.WARNING - min(verbose, 2) * 10
    logging.basicConfig(stream=sys.stderr, level=level, format="%(message)s")

    asyncio.run(chat_loop(model))
