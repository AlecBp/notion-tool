"""Main CLI entry point for Notion Kanban CLI tool."""

import asyncio
import json
import sys
from typing import Any

import typer
from typing_extensions import Annotated

from .client import NotionAPIError, NotionClient
from .schema import DatabaseSchema, get_database_schema
from .transform import transform_property_value

app = typer.Typer(
    name="notion-tool",
    help="CLI tool for interacting with Notion kanban boards",
    add_completion=False,
)


def output_json(success: bool, data: Any = None, error: dict | None = None) -> None:
    """Output JSON response to stdout.

    Args:
        success: Whether the operation succeeded
        data: The response data (if successful)
        error: Error information (if failed)
    """
    response: dict[str, Any] = {
        "success": success,
        "data": data,
        "error": error,
    }
    print(json.dumps(response, indent=2, default=str))


@app.command()
def read(
    database: Annotated[str, typer.Option("--database", "-d", help="Notion database ID")],
    item_id: Annotated[str, typer.Argument(help="ID of the item to read")],
) -> None:
    """Read and display item details.

    Example:
        notion-tool read --database 0509def271a84947b6a55ddf1caee4df page-id
    """

    async def _read() -> None:
        async with NotionClient() as client:
            try:
                page = await client.get_page(item_id)

                # Transform properties to more useful format
                properties: dict[str, Any] = {}
                for prop_name, prop_data in page.get("properties", {}).items():
                    properties[prop_name] = transform_property_value(prop_data)

                output_json(
                    success=True,
                    data={
                        "id": page.get("id"),
                        "created_time": page.get("created_time"),
                        "last_edited_time": page.get("last_edited_time"),
                        "archived": page.get("archived"),
                        "properties": properties,
                        "url": page.get("url"),
                    },
                )
            except NotionAPIError as e:
                output_json(
                    success=False,
                    error={"message": str(e), "status_code": e.status_code},
                )
            except Exception as e:
                output_json(success=False, error={"message": str(e)})

    asyncio.run(_read())


@app.command()
def update_status(
    database: Annotated[str, typer.Option("--database", "-d", help="Notion database ID")],
    item_id: Annotated[str, typer.Argument(help="ID of the item to update")],
    status: Annotated[str, typer.Argument(help="New status value")],
) -> None:
    """Update item status.

    Example:
        notion-tool update-status --database 0509def271a84947b6a55ddf1caee4df page-id "In Progress"
    """

    async def _update_status() -> None:
        async with NotionClient() as client:
            try:
                # Get database schema to find status property
                schema = await get_database_schema(client, database)
                status_prop_name = schema.get_status_property_name()

                if not status_prop_name:
                    output_json(
                        success=False,
                        error={"message": "No status property found in database"},
                    )
                    return

                # Check if status is valid
                status_options = schema.get_status_options()
                if status_options and status not in status_options:
                    output_json(
                        success=False,
                        error={
                            "message": f"Invalid status '{status}'",
                            "available_options": status_options,
                        },
                    )
                    return

                # Update the page
                await client.update_page(item_id, {status_prop_name: {"status": {"name": status}}})

                output_json(
                    success=True,
                    data={
                        "id": item_id,
                        "status": status,
                        "property": status_prop_name,
                    },
                )
            except NotionAPIError as e:
                output_json(
                    success=False,
                    error={"message": str(e), "status_code": e.status_code},
                )
            except Exception as e:
                output_json(success=False, error={"message": str(e)})

    asyncio.run(_update_status())


@app.command()
def add_note(
    database: Annotated[str, typer.Option("--database", "-d", help="Notion database ID")],
    item_id: Annotated[str, typer.Argument(help="ID of the item to add note to")],
    note: Annotated[str, typer.Argument(help="Note content")],
) -> None:
    """Add a note/comment to an item.

    Example:
        notion-tool add-note --database 0509def271a84947b6a55ddf1caee4df page-id "Task completed"
    """

    async def _add_note() -> None:
        async with NotionClient() as client:
            try:
                # First, get existing discussions
                discussions = await client.list_discussions(item_id)
                discussion_id = None

                # Use the first discussion or create a new one
                if discussions.get("results"):
                    discussion_id = discussions["results"][0]["id"]

                # Note: Notion API currently requires an existing discussion_id
                # This is a limitation of the current API
                output_json(
                    success=False,
                    error={
                        "message": "Adding comments requires a discussion_id. This feature is currently limited.",
                        "note": "Please use the Notion web UI to add comments.",
                    },
                )
            except NotionAPIError as e:
                output_json(
                    success=False,
                    error={"message": str(e), "status_code": e.status_code},
                )
            except Exception as e:
                output_json(success=False, error={"message": str(e)})

    asyncio.run(_add_note())


@app.command()
def query(
    database: Annotated[str, typer.Option("--database", "-d", help="Notion database ID")],
    status: Annotated[str | None, typer.Option("--status", "-s", help="Filter by status")] = None,
    tags: Annotated[str | None, typer.Option("--tags", "-t", help="Filter by tags (comma-separated)")] = None,
    filter: Annotated[str | None, typer.Option("--filter", "-f", help="Custom filter (e.g., 'priority=high')")] = None,
    limit: Annotated[int | None, typer.Option("--limit", "-l", help="Maximum number of results")] = None,
) -> None:
    """Query items from the database.

    Example:
        notion-tool query --database 0509def271a84947b6a55ddf1caee4df --status "In Progress"
        notion-tool query --database 0509def271a84947b6a55ddf1caee4df --tags "urgent,important"
        notion-tool query --database 0509def271a84947b6a55ddf1caee4df --limit 5
    """

    async def _query() -> None:
        async with NotionClient() as client:
            try:
                # Get database schema
                schema = await get_database_schema(client, database)

                # Build filter
                filter_obj = None

                if status:
                    status_prop_name = schema.get_status_property_name()
                    if status_prop_name:
                        filter_obj = {
                            "property": status_prop_name,
                            "status": {"equals": status},
                        }

                if tags:
                    tag_props = schema.get_tag_property_names()
                    if tag_props:
                        tag_list = [t.strip() for t in tags.split(",")]
                        tag_prop_name = tag_props[0]  # Use first tag property
                        if len(tag_list) == 1:
                            filter_obj = {
                                "property": tag_prop_name,
                                "multi_select": {"contains": tag_list[0]},
                            }
                        else:
                            filter_obj = {
                                "and": [
                                    {"property": tag_prop_name, "multi_select": {"contains": tag}}
                                    for tag in tag_list
                                ]
                            }

                if filter:
                    # Parse custom filter like "priority=high"
                    if "=" in filter:
                        prop_name, value = filter.split("=", 1)
                        prop_name = prop_name.strip()
                        value = value.strip()

                        prop_def = schema.find_property_by_name(prop_name)
                        if prop_def:
                            prop_type = prop_def.get("type")
                            if prop_type == "status":
                                filter_obj = {"property": prop_name, "status": {"equals": value}}
                            elif prop_type == "select":
                                filter_obj = {"property": prop_name, "select": {"equals": value}}
                            elif prop_type == "multi_select":
                                filter_obj = {"property": prop_name, "multi_select": {"contains": value}}
                            else:
                                filter_obj = {"property": prop_name, "title": {"equals": value}}

                # Query the database
                result = await client.query_database(database, filter_obj=filter_obj, page_size=limit)

                # Transform results
                items = []
                for page in result.get("results", []):
                    properties: dict[str, Any] = {}
                    for prop_name, prop_data in page.get("properties", {}).items():
                        properties[prop_name] = transform_property_value(prop_data)

                    items.append(
                        {
                            "id": page.get("id"),
                            "created_time": page.get("created_time"),
                            "last_edited_time": page.get("last_edited_time"),
                            "archived": page.get("archived"),
                            "properties": properties,
                            "url": page.get("url"),
                        }
                    )

                output_json(
                    success=True,
                    data={
                        "items": items,
                        "next_cursor": result.get("next_cursor"),
                        "has_more": result.get("has_more"),
                    },
                )
            except NotionAPIError as e:
                output_json(
                    success=False,
                    error={"message": str(e), "status_code": e.status_code},
                )
            except Exception as e:
                output_json(success=False, error={"message": str(e)})

    asyncio.run(_query())


@app.command()
def list_status(
    database: Annotated[str, typer.Option("--database", "-d", help="Notion database ID")],
) -> None:
    """List all available status options.

    Example:
        notion-tool list-status --database 0509def271a84947b6a55ddf1caee4df
    """

    async def _list_status() -> None:
        async with NotionClient() as client:
            try:
                schema = await get_database_schema(client, database)
                status_options = schema.get_status_options()

                if not status_options:
                    output_json(
                        success=False,
                        error={"message": "No status property found in database"},
                    )
                    return

                output_json(
                    success=True,
                    data={
                        "property_name": schema.get_status_property_name(),
                        "options": status_options,
                    },
                )
            except NotionAPIError as e:
                output_json(
                    success=False,
                    error={"message": str(e), "status_code": e.status_code},
                )
            except Exception as e:
                output_json(success=False, error={"message": str(e)})

    asyncio.run(_list_status())


@app.command()
def list_tags(
    database: Annotated[str, typer.Option("--database", "-d", help="Notion database ID")],
) -> None:
    """List all available tag options.

    Example:
        notion-tool list-tags --database 0509def271a84947b6a55ddf1caee4df
    """

    async def _list_tags() -> None:
        async with NotionClient() as client:
            try:
                schema = await get_database_schema(client, database)
                tag_props = schema.get_tag_property_names()

                if not tag_props:
                    output_json(
                        success=False,
                        error={"message": "No tag properties found in database"},
                    )
                    return

                tags_by_property = {}
                for tag_prop in tag_props:
                    tags_by_property[tag_prop] = schema.get_tag_options(tag_prop)

                output_json(
                    success=True,
                    data={
                        "properties": tag_props,
                        "tags_by_property": tags_by_property,
                    },
                )
            except NotionAPIError as e:
                output_json(
                    success=False,
                    error={"message": str(e), "status_code": e.status_code},
                )
            except Exception as e:
                output_json(success=False, error={"message": str(e)})

    asyncio.run(_list_tags())


@app.command()
def schema(
    database: Annotated[str, typer.Option("--database", "-d", help="Notion database ID")],
) -> None:
    """Get database schema.

    Example:
        notion-tool schema --database 0509def271a84947b6a55ddf1caee4df
    """

    async def _schema() -> None:
        async with NotionClient() as client:
            try:
                schema_data = await client.get_database(database)

                # Simplify the schema output
                properties = {}
                for prop_name, prop_def in schema_data.get("properties", {}).items():
                    prop_type = prop_def.get("type")
                    properties[prop_name] = {"type": prop_type}

                    # Add options for select/multi_select/status
                    if prop_type == "select":
                        options = prop_def.get("select", {}).get("options", [])
                        properties[prop_name]["options"] = [opt.get("name") for opt in options]
                    elif prop_type == "multi_select":
                        options = prop_def.get("multi_select", {}).get("options", [])
                        properties[prop_name]["options"] = [opt.get("name") for opt in options]
                    elif prop_type == "status":
                        options = prop_def.get("status", {}).get("options", [])
                        properties[prop_name]["options"] = [opt.get("name") for opt in options]

                output_json(
                    success=True,
                    data={
                        "id": schema_data.get("id"),
                        "title": schema_data.get("title", [{}])[0].get("plain_text", ""),
                        "properties": properties,
                    },
                )
            except NotionAPIError as e:
                output_json(
                    success=False,
                    error={"message": str(e), "status_code": e.status_code},
                )
            except Exception as e:
                output_json(success=False, error={"message": str(e)})

    asyncio.run(_schema())


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
