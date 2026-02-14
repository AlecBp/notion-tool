"""Notion API client wrapper."""

import httpx

from .config import NOTION_API_BASE_URL, NOTION_API_VERSION, get_api_key


class NotionAPIError(Exception):
    """Error raised when the Notion API returns an error."""

    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class NotionClient:
    """Client for interacting with the Notion API."""

    def __init__(self, api_key: str | None = None):
        """Initialize the Notion client.

        Args:
            api_key: Notion API key. If None, reads from NOTION_API_KEY env var.
        """
        self.api_key = api_key or get_api_key()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=NOTION_API_BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Notion-Version": NOTION_API_VERSION,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make a request to the Notion API.

        Args:
            method: HTTP method (GET, POST, PATCH, etc.)
            path: API endpoint path
            **kwargs: Additional arguments for httpx.request

        Returns:
            The JSON response as a dictionary

        Raises:
            NotionAPIError: If the API returns an error
        """
        client = await self._get_client()
        response = await client.request(method, path, **kwargs)

        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code >= 400:
            message = data.get("message", f"HTTP {response.status_code}")
            raise NotionAPIError(
                message=message,
                status_code=response.status_code,
                response_data=data,
            )

        return data

    async def get_page(self, page_id: str) -> dict:
        """Get a page from Notion.

        Args:
            page_id: The ID of the page to fetch

        Returns:
            Page data including properties
        """
        return await self._request("GET", f"/pages/{page_id}")

    async def get_database(self, database_id: str) -> dict:
        """Get database schema.

        Args:
            database_id: The ID of the database

        Returns:
            Database schema data
        """
        return await self._request("GET", f"/databases/{database_id}")

    async def query_database(
        self,
        database_id: str,
        filter_obj: dict | None = None,
        sorts: list[dict] | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> dict:
        """Query a database.

        Args:
            database_id: The ID of the database
            filter_obj: Filter object for the query
            sorts: Sort configurations
            start_cursor: Cursor for pagination
            page_size: Number of results per page

        Returns:
            Query results with pages and next_cursor
        """
        body: dict = {}
        if filter_obj is not None:
            body["filter"] = filter_obj
        if sorts is not None:
            body["sorts"] = sorts
        if start_cursor is not None:
            body["start_cursor"] = start_cursor
        if page_size is not None:
            body["page_size"] = page_size

        return await self._request("POST", f"/databases/{database_id}/query", json=body)

    async def update_page(self, page_id: str, properties: dict) -> dict:
        """Update a page's properties.

        Args:
            page_id: The ID of the page to update
            properties: Properties to update (partial update)

        Returns:
            Updated page data
        """
        return await self._request("PATCH", f"/pages/{page_id}", json={"properties": properties})

    async def add_comment(self, parent_id: str, discussion_id: str, text: str) -> dict:
        """Add a comment to a page.

        Args:
            parent_id: The ID of the page/block containing the discussion
            discussion_id: The ID of the discussion thread
            text: The comment text

        Returns:
            Created comment data
        """
        return await self._request(
            "POST",
            "/comments",
            json={
                "parent": {"page_id": parent_id},
                "discussion_id": discussion_id,
                "rich_text": [{"type": "text", "text": {"content": text}}],
            },
        )

    async def list_discussions(self, block_id: str) -> dict:
        """List discussions on a block.

        Args:
            block_id: The ID of the block

        Returns:
            List of discussions
        """
        return await self._request("GET", f"/blocks/{block_id}/comments")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
