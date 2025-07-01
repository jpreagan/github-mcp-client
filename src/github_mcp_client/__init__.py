import logging
import sys

import click


@click.command()
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.option("--model", default="gpt-4.1", help="LLM model to use")
def main(verbose: int, model: str) -> None:
    """GitHub MCP Client - Interactive client for GitHub MCP server"""
    import asyncio

    from .client import main as client_main

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(client_main(model))


if __name__ == "__main__":
    main()
