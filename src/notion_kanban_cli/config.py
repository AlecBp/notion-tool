"""Configuration management for Notion Kanban CLI."""

import os
from pathlib import Path


def get_api_key() -> str:
    """Get Notion API key from environment."""
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise ValueError(
            "NOTION_API_KEY environment variable not set. "
            "Please set it in your shell configuration."
        )
    return api_key


NOTION_API_BASE_URL = "https://api.notion.com/v1"
NOTION_API_VERSION = "2022-06-28"
