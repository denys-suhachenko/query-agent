export type AgentQueryRequest = {
  message: string;
};

export type SqlExecution = {
  sql: string;
  columns: string[];
  rows: unknown[][];
  rows_count: number;
  truncated: boolean;
};

export type AgentStep = {
  tool: string;
  arguments: Record<string, unknown>;
  output: unknown;
};

export type AgentQueryResponse = {
  answer: string;
  sql_executions: SqlExecution[];
  steps: AgentStep[];
};
