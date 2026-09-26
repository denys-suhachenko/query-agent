import json
import os
from typing import Any, TypedDict

from openai import OpenAI

from apps.agent.tools.registry import TOOLS, execute_tool
from apps.agent.tools.schema import (
    format_schema_for_llm,
    inspect_schema,
)

client = OpenAI()

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)

MAX_STEPS = 6


INSTRUCTIONS = """
You are a database analysis agent.

The current database schema is provided together with the user's question.

Rules:
- For straightforward ranking, aggregation, counting, or grouping questions,
  execute one final SQL query whenever possible.
- Do not run separate queries merely to inspect status values, totals, or related
  records if the requested result can be computed correctly in one SQL statement.
- Execute additional SQL only if the previous query failed, returned insufficient
  information, or a genuine ambiguity cannot be resolved from the schema.
- Never invent categorical or enum-like values such as statuses, types, states,
  roles, or categories.
- Do not assume values such as "completed", "paid", "cancelled", or "success"
  unless those values were provided by the schema context or observed in actual
  query results.
- If filtering by a categorical value materially affects the answer and the
  valid values are unknown, inspect the actual values before applying such a filter.
- Known categorical values may be provided in the schema as values=[...].
- Treat values=[...] as the observed valid values available to you.
- Never invent categorical or enum-like values such as statuses, states,
  types, roles, or kinds.
- Never assume values such as "completed", "paid", "cancelled", "success",
  or similar unless they are explicitly present in the provided schema or
  returned by a tool.
- When filtering by a categorical value, use only values supported by the
  provided schema or actual query results.
- If categorical values are unknown, do not guess them.
"""


class SQLExecution(TypedDict):
    sql: str
    columns: list[str]
    rows: list[list[Any]]
    rows_count: int
    truncated: bool


class AgentStep(TypedDict):
    tool: str
    arguments: dict[str, Any]
    output: Any


class AgentResult(TypedDict):
    answer: str
    steps: list[AgentStep]
    sql_executions: list[SQLExecution]


# Schema tools can remain registered for other/debug use,
# but this agent only exposes SQL execution to the model.
AGENT_TOOLS = [tool for tool in TOOLS if tool.get("name") == "execute_sql"]


def run_agent(message: str) -> AgentResult:

    schema = inspect_schema()

    schema = inspect_schema()
    schema_context = format_schema_for_llm(schema)

    agent_input = f"""
    DATABASE SCHEMA:

    {schema_context}

    USER QUESTION:

    {message}
    """

    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=agent_input,
        tools=AGENT_TOOLS,
    )

    steps: list[AgentStep] = []
    sql_executions: list[SQLExecution] = []

    for _ in range(MAX_STEPS):
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            return {
                "answer": response.output_text,
                "steps": steps,
                "sql_executions": sql_executions,
            }

        tool_outputs = []

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
            tools=AGENT_TOOLS,
        )

    raise RuntimeError(f"Agent exceeded {MAX_STEPS} tool steps")
