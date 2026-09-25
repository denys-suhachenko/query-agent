from typing import Any

from django.conf import settings
from django.db import connections

ALLOWED_PREFIXES = (
    "catalog_",
    "customers_",
    "orders_",
)

DATABASE_SCHEMA = settings.AGENT_DB_SCHEMA


def list_tables() -> list[str]:
    connection = connections["agent"]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
        )

        tables = [row[0] for row in cursor.fetchall()]

    return [table for table in tables if table.startswith(ALLOWED_PREFIXES)]


def describe_table(table_name: str) -> dict[str, Any]:
    if table_name not in list_tables():
        raise ValueError(f"Table '{table_name}' is not available")

    connection = connections["agent"]

    with connection.cursor() as cursor:
        # Columns
        cursor.execute(
            """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position;
            """,
            [DATABASE_SCHEMA, table_name],
        )

        columns = cursor.fetchall()

        # Primary keys
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

        # Foreign keys
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
                "default": column_default,
                "max_length": max_length,
                "numeric_precision": numeric_precision,
                "numeric_scale": numeric_scale,
                "primary_key": column_name in primary_keys,
                "foreign_key": foreign_keys.get(column_name),
            }
            for (
                column_name,
                data_type,
                is_nullable,
                column_default,
                max_length,
                numeric_precision,
                numeric_scale,
            ) in columns
        ],
    }


def get_relationships(table_name: str) -> dict[str, Any]:
    available_tables = set(list_tables())

    if table_name not in available_tables:
        raise ValueError(f"Table '{table_name}' is not available")

    connection = connections["agent"]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                source_table.relname AS source_table,
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

            JOIN pg_namespace AS target_schema
                ON target_schema.oid = target_table.relnamespace

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
              AND target_schema.nspname = %s
              AND (
                  source_table.relname = %s
                  OR target_table.relname = %s
              )
            ORDER BY
                source_table.relname,
                source_column.attname;
            """,
            [
                DATABASE_SCHEMA,
                DATABASE_SCHEMA,
                table_name,
                table_name,
            ],
        )

        rows = cursor.fetchall()

    outgoing = []
    incoming = []

    for (
        source_table,
        source_column,
        target_table,
        target_column,
    ) in rows:
        # Не expose-имо relationship до таблиці,
        # яку сам agent не має права бачити.
        if source_table not in available_tables or target_table not in available_tables:
            continue

        relationship = {
            "source_table": source_table,
            "source_column": source_column,
            "target_table": target_table,
            "target_column": target_column,
        }

        if source_table == table_name:
            outgoing.append(relationship)

        if target_table == table_name:
            incoming.append(relationship)

    return {
        "table": table_name,
        "outgoing": outgoing,
        "incoming": incoming,
    }
