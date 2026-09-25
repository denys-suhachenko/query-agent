from typing import Any

from django.db import connections, transaction

MAX_ROWS = 500


def execute_sql(sql: str) -> dict[str, Any]:
    sql = sql.strip()

    if not sql:
        raise ValueError("SQL query cannot be empty")

    connection = connections["agent"]

    with transaction.atomic(using="agent"):
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout = '5s'")

            cursor.execute("SET TRANSACTION READ ONLY")

            cursor.execute(sql)

            if cursor.description is None:
                raise ValueError("Query did not return any result set")

            columns = [column.name for column in cursor.description]

            rows = cursor.fetchmany(MAX_ROWS + 1)

        truncated = len(rows) > MAX_ROWS

        rows = rows[:MAX_ROWS]

        return {
            "sql": sql,
            "columns": columns,
            "rows": [list(row) for row in rows],
            "rows_count": len(rows),
            "truncated": truncated,
        }
