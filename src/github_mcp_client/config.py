import os
import shutil
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for GitHub MCP client."""
    openai_api_key: str
    openai_base_url: str | None
    github_token: str
    model: str

    @classmethod
    def from_env(cls, model: str = "gpt-4.1") -> "Config":
        """Load configuration from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing OPENAI_API_KEY environment variable. "
                "Set it in your .env file or environment."
            )
        
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        if not github_token:
            raise ValueError(
                "Missing GITHUB_PERSONAL_ACCESS_TOKEN environment variable. "
                "Set it in your .env file or environment."
            )
        
        if not shutil.which("docker"):
            raise ValueError(
                "Docker not found. Please install Docker and ensure it's in your PATH."
            )
        
        return cls(
            openai_api_key=api_key,
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            github_token=github_token,
            model=model,
        )