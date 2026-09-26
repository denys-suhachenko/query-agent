from typing import Any

from django.conf import settings
from django.db import connections

ALLOWED_PREFIXES = (
    "catalog_",
    "customers_",
    "orders_",
)

DATABASE_SCHEMA = settings.AGENT_DB_SCHEMA

MAX_KNOWN_VALUES = 20

CATEGORICAL_COLUMN_NAMES = {
    "status",
    "state",
    "type",
    "kind",
    "role",
}


def list_tables() -> list[str]:
    connection = connections["agent"]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """,
            [DATABASE_SCHEMA],
        )

        tables = [row[0] for row in cursor.fetchall()]

    return [table for table in tables if table.startswith(ALLOWED_PREFIXES)]


def describe_table(table_name: str) -> dict[str, Any]:
    available_tables = set(list_tables())

    if table_name not in available_tables:
        raise ValueError(f"Table '{table_name}' is not available")

    return _describe_table(table_name)


def _describe_table(table_name: str) -> dict[str, Any]:
    connection = connections["agent"]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position;
            """,
            [DATABASE_SCHEMA, table_name],
        )

        columns = cursor.fetchall()

        cursor.execute(
            """
            SELECT a.attname
            FROM pg_constraint AS c
            JOIN pg_class AS t
                ON t.oid = c.conrelid
            JOIN pg_namespace AS n
                ON n.oid = t.relnamespace
            JOIN LATERAL unnest(c.conkey)
                WITH ORDINALITY AS cols(attnum, ord)
                ON TRUE
            JOIN pg_attribute AS a
                ON a.attrelid = t.oid
               AND a.attnum = cols.attnum
            WHERE c.contype = 'p'
              AND n.nspname = %s
              AND t.relname = %s;
            """,
            [DATABASE_SCHEMA, table_name],
        )

        primary_keys = {row[0] for row in cursor.fetchall()}

        cursor.execute(
            """
            SELECT
                source_column.attname AS source_column,
                target_table.relname AS target_table,
                target_column.attname AS target_column
            FROM pg_constraint AS c

            JOIN pg_class AS source_table
                ON source_table.oid = c.conrelid

            JOIN pg_namespace AS source_schema
                ON source_schema.oid = source_table.relnamespace

            JOIN pg_class AS target_table
                ON target_table.oid = c.confrelid

            JOIN LATERAL unnest(c.conkey)
                WITH ORDINALITY AS source_keys(attnum, ord)
                ON TRUE

            JOIN LATERAL unnest(c.confkey)
                WITH ORDINALITY AS target_keys(attnum, ord)
                ON target_keys.ord = source_keys.ord

            JOIN pg_attribute AS source_column
                ON source_column.attrelid = source_table.oid
               AND source_column.attnum = source_keys.attnum

            JOIN pg_attribute AS target_column
                ON target_column.attrelid = target_table.oid
               AND target_column.attnum = target_keys.attnum

            WHERE c.contype = 'f'
              AND source_schema.nspname = %s
              AND source_table.relname = %s;
            """,
            [DATABASE_SCHEMA, table_name],
        )

        foreign_keys = {
            source_column: {
                "table": target_table,
                "column": target_column,
            }
            for (
                source_column,
                target_table,
                target_column,
            ) in cursor.fetchall()
        }

    return {
        "table": table_name,
        "columns": [
            {
                "name": column_name,
                "type": data_type,
                "nullable": is_nullable == "YES",
                "primary_key": column_name in primary_keys,
                "foreign_key": foreign_keys.get(column_name),
                "known_values": _get_known_values(
                    table_name,
                    column_name,
                    data_type,
                ),
            }
            for (
                column_name,
                data_type,
                is_nullable,
            ) in columns
        ],
    }


def _get_known_values(
    table_name: str,
    column_name: str,
    data_type: str,
) -> list[Any] | None:
    if not _is_categorical_column(
        column_name,
        data_type,
    ):
        return None

    connection = connections["agent"]

    quote = connection.ops.quote_name

    schema = quote(DATABASE_SCHEMA)
    table = quote(table_name)
    column = quote(column_name)

    query = f"""
        SELECT DISTINCT {column}
        FROM {schema}.{table}
        WHERE {column} IS NOT NULL
        ORDER BY {column}
        LIMIT %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            [MAX_KNOWN_VALUES + 1],
        )

        values = [row[0] for row in cursor.fetchall()]

    if len(values) > MAX_KNOWN_VALUES:
        return None

    return values


def _is_categorical_column(
    column_name: str,
    data_type: str,
) -> bool:
    if data_type not in {
        "character varying",
        "text",
        "character",
    }:
        return False

    normalized_name = column_name.lower()

    return any(
        normalized_name == candidate or normalized_name.endswith(f"_{candidate}")
        for candidate in CATEGORICAL_COLUMN_NAMES
    )


def inspect_schema() -> dict[str, Any]:
    tables = list_tables()

    return {
        "schema": DATABASE_SCHEMA,
        "tables": [_describe_table(table_name) for table_name in tables],
    }


def format_schema_for_llm(
    schema: dict[str, Any],
) -> str:
    tables = []

    for table in schema["tables"]:
        columns = []

        for column in table["columns"]:
            parts = [
                column["name"],
                column["type"],
            ]

            if column["primary_key"]:
                parts.append("PK")

            foreign_key = column["foreign_key"]

            if foreign_key:
                parts.append(f"FK -> {foreign_key['table']}.{foreign_key['column']}")

            known_values = column["known_values"]

            if known_values:
                formatted_values = ", ".join(repr(value) for value in known_values)

                parts.append(f"values=[{formatted_values}]")

            columns.append(" ".join(parts))

        formatted_columns = ",\n  ".join(columns)

        tables.append(f"{table['table']}(\n  {formatted_columns}\n)")

    return "\n\n".join(tables)
