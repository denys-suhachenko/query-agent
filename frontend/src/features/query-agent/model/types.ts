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

export type AgentStage = 'analysis' | 'answer';

export type AgentActivityEvent = {
  type: 'activity';
  stage: AgentStage;
  message: string;
};

export type AgentSqlEvent = {
  type: 'sql';
  data: SqlExecution;
};

export type AgentResultEvent = {
  type: 'result';
  data: AgentQueryResponse;
};

export type AgentDoneEvent = {
  type: 'done';
  duration_ms: number;
};

export type AgentErrorEvent = {
  type: 'error';
  message: string;
};

export type AgentStreamEvent =
  | AgentActivityEvent
  | AgentSqlEvent
  | AgentResultEvent
  | AgentDoneEvent
  | AgentErrorEvent;
