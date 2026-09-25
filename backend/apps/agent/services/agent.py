import json
import os
from typing import Any, TypedDict

from openai import OpenAI

from apps.agent.tools.registry import TOOLS, execute_tool

client = OpenAI()

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)

MAX_STEPS = 10

INSTRUCTIONS = """
You are a database analysis agent.

Rules:
- Never assume the database schema.
- Inspect only the tables and relationships necessary to answer the question.
- Do not inspect unrelated tables.
- Do not execute exploratory SQL unless it is necessary to resolve ambiguity.
- If the schema already provides enough information to construct the query,
  execute the final query directly.
- Use execute_sql when actual database data is required.
- Generate PostgreSQL-compatible SQL.
- Never invent tables, columns, or relationships.
- Prefer explicit JOIN conditions.
- Request only the columns needed.
- Avoid unnecessarily large result sets.
- Do not modify database data or schema.
- Base the final answer on actual tool results.
- Do not query row-level or aggregate business data when the user's question
  can be answered entirely from schema metadata.
- When calculating business metrics such as revenue, inspect relevant status fields
  and determine whether cancelled, failed, pending, or refunded records should be excluded.
- Do not assume that every stored record should contribute to the metric.
"""


class SQLExecution(TypedDict):
    sql: str
    columns: list[str]
    rows: list[list[Any]]
    rows_count: int
    truncated: bool


class AgentResult(TypedDict):
    answer: str
    steps: list[AgentStep]
    sql_executions: list[SQLExecution]


class AgentStep(TypedDict):
    tool: str
    arguments: dict[str, Any]
    output: Any


class AgentResult(TypedDict):
    answer: str
    steps: list[AgentStep]


def run_agent(message: str) -> AgentResult:
    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=message,
        tools=TOOLS,
    )

    steps: list[AgentStep] = []
    sql_executions: list[SQLExecution] = []

    for _ in range(MAX_STEPS):
        tool_calls = [item for item in response.output if item.type == "function_call"]

        tool_outputs = []

        if not tool_calls:
            return {
                "answer": response.output_text,
                "steps": steps,
                "sql_executions": sql_executions,
            }

        for tool_call in tool_calls:
            arguments = json.loads(tool_call.arguments or "{}")

            try:
                result = execute_tool(
                    tool_call.name,
                    arguments,
                )

                output = {
                    "success": True,
                    "result": result,
                }

                steps.append(
                    {
                        "tool": tool_call.name,
                        "arguments": arguments,
                        "output": result,
                    }
                )

                if tool_call.name == "execute_sql":
                    sql_executions.append(result)
            except Exception as exc:
                output = {
                    "success": False,
                    "error": str(exc),
                }

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(
                        output,
                        default=str,
                    ),
                }
            )

        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
        )

    raise RuntimeError(f"Agent exceeded {MAX_STEPS} tool steps")
