"""Schema discovery and caching for Notion databases."""

from typing import Any

from .client import NotionClient


class DatabaseSchema:
    """Represents the schema of a Notion database."""

    def __init__(self, database_id: str, schema_data: dict[str, Any]):
        self.database_id = database_id
        self.schema_data = schema_data
        self._status_property_name = None
        self._tag_property_names = []

    @property
    def properties(self) -> dict[str, Any]:
        """Get all properties from the schema."""
        return self.schema_data.get("properties", {})

    def get_status_property_name(self) -> str | None:
        """Find and cache the name of the status property."""
        if self._status_property_name is not None:
            return self._status_property_name

        for prop_name, prop_def in self.properties.items():
            if prop_def.get("type") == "status":
                self._status_property_name = prop_name
                return prop_name

        return None

    def get_tag_property_names(self) -> list[str]:
        """Find and cache the names of tag/multi_select properties."""
        if self._tag_property_names:
            return self._tag_property_names

        tag_names = []
        for prop_name, prop_def in self.properties.items():
            if prop_def.get("type") == "multi_select":
                tag_names.append(prop_name)

        self._tag_property_names = tag_names
        return tag_names

    def get_status_options(self) -> list[str]:
        """Get all available status options."""
        status_prop = self.get_status_property_name()
        if not status_prop:
            return []

        prop_def = self.properties.get(status_prop, {})
        status_options = prop_def.get("status", {}).get("options", [])
        return [opt.get("name", "") for opt in status_options if opt.get("name")]

    def get_tag_options(self, tag_property: str) -> list[str]:
        """Get all available tag options for a specific property."""
        prop_def = self.properties.get(tag_property, {})
        tag_options = prop_def.get("multi_select", {}).get("options", [])
        return [opt.get("name", "") for opt in tag_options if opt.get("name")]

    def find_property_by_name(self, name: str) -> dict[str, Any] | None:
        """Find a property definition by name (case-insensitive)."""
        name_lower = name.lower()
        for prop_name, prop_def in self.properties.items():
            if prop_name.lower() == name_lower:
                return prop_def
        return None


class SchemaCache:
    """Cache for database schemas."""

    def __init__(self):
        self._schemas: dict[str, DatabaseSchema] = {}

    def get(self, database_id: str) -> DatabaseSchema | None:
        """Get a cached schema."""
        return self._schemas.get(database_id)

    def set(self, database_id: str, schema: DatabaseSchema) -> None:
        """Cache a schema."""
        self._schemas[database_id] = schema

    def clear(self) -> None:
        """Clear the cache."""
        self._schemas.clear()


# Global schema cache
_schema_cache = SchemaCache()


async def get_database_schema(client: NotionClient, database_id: str) -> DatabaseSchema:
    """Get or fetch database schema."""
    cached = _schema_cache.get(database_id)
    if cached:
        return cached

    schema_data = await client.get_database(database_id)
    schema = DatabaseSchema(database_id, schema_data)
    _schema_cache.set(database_id, schema)
    return schema
