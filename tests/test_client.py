"""Tests for Notion API client."""

import pytest
from notion_kanban_cli.client import NotionClient, NotionAPIError


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization."""
    client = NotionClient()
    assert client.api_key is not None
    await client.close()


@pytest.mark.asyncio
async def test_client_with_custom_api_key():
    """Test client with custom API key."""
    client = NotionClient(api_key="test-key")
    assert client.api_key == "test-key"
    await client.close()


def test_api_error():
    """Test NotionAPIError creation."""
    error = NotionAPIError("Test error", status_code=400)
    assert str(error) == "Test error"
    assert error.status_code == 400
