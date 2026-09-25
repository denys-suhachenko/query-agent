from typing import Any

from apps.agent.tools.schema import (
    describe_table,
    get_relationships,
    list_tables,
)
from apps.agent.tools.sql import execute_sql

TOOL_REGISTRY = {
    "list_tables": list_tables,
    "describe_table": describe_table,
    "get_relationships": get_relationships,
    "execute_sql": execute_sql,
}

TOOLS = [
    {
        "type": "function",
        "name": "list_tables",
        "description": (
            "List the business tables that are available for analysis in the PostgreSQL database."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "describe_table",
        "description": (
            "Inspect a database table and return its columns, data types, "
            "nullability, primary keys, and foreign keys."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Exact database table name.",
                },
            },
            "required": ["table_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_relationships",
        "description": (
            "Return incoming and outgoing foreign-key relationships for a database table."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Exact database table name.",
                },
            },
            "required": ["table_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "execute_sql",
        "description": (
            "Execute a read-only PostgreSQL SELECT query "
            "and return structured query results. "
            "Use this after inspecting the database schema."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A single read-only PostgreSQL query.",
                },
            },
            "required": ["sql"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    return tool(**arguments)
