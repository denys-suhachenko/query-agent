import { AgentQueryRequest, AgentQueryResponse } from '../model/types';

export async function queryAgent(
  payload: AgentQueryRequest,
): Promise<AgentQueryResponse> {
  const response = await fetch('/api/agent/query/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error('Failed to query agent');
  }

  return data;
}
