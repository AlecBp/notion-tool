"""Property transformation utilities for Notion API responses."""

from datetime import datetime
from typing import Any


def transform_property_value(prop_data: dict[str, Any]) -> Any:
    """Transform a Notion property value to a more useful format."""
    prop_type = prop_data.get("type")

    if prop_type == "title":
        titles = prop_data.get("title", [])
        return "".join(t.get("plain_text", "") for t in titles)

    if prop_type == "rich_text":
        texts = prop_data.get("rich_text", [])
        return "".join(t.get("plain_text", "") for t in texts)

    if prop_type == "number":
        return prop_data.get("number")

    if prop_type == "select":
        select_data = prop_data.get("select")
        return select_data.get("name") if select_data else None

    if prop_type == "multi_select":
        return [s.get("name") for s in prop_data.get("multi_select", [])]

    if prop_type == "status":
        status_data = prop_data.get("status")
        return status_data.get("name") if status_data else None

    if prop_type == "date":
        date_data = prop_data.get("date")
        if date_data:
            start = date_data.get("start")
            if start:
                try:
                    return datetime.fromisoformat(start).isoformat()
                except ValueError:
                    return start
        return None

    if prop_type == "checkbox":
        return prop_data.get("checkbox")

    if prop_type == "url":
        return prop_data.get("url")

    if prop_type == "email":
        return prop_data.get("email")

    if prop_type == "phone_number":
        return prop_data.get("phone_number")

    if prop_type == "formula":
        return transform_property_value(prop_data.get("formula", {}))

    if prop_type == "relation":
        return [r.get("id") for r in prop_data.get("relation", [])]

    if prop_type == "people":
        return [p.get("id") for p in prop_data.get("people", [])]

    if prop_type == "files":
        return [f.get("name") for f in prop_data.get("files", [])]

    if prop_type == "created_time":
        return prop_data.get("created_time")

    if prop_type == "created_by":
        return prop_data.get("created_by")

    if prop_type == "last_edited_time":
        return prop_data.get("last_edited_time")

    if prop_type == "last_edited_by":
        return prop_data.get("last_edited_by")

    # For unknown types, return raw data
    return prop_data
