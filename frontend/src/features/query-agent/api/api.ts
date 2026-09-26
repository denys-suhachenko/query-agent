import {
  AgentQueryRequest,
  AgentQueryResponse,
  AgentStreamEvent,
} from '../model/types';

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

export async function streamAgentQuery(
  payload: AgentQueryRequest,
  onEvent: (event: AgentStreamEvent) => void,
): Promise<void> {
  const response = await fetch('/api/agent/query/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);

    throw new Error(data?.error ?? 'Failed to query agent');
  }

  if (!response.body) {
    throw new Error('Streaming response is unavailable');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      buffer += decoder.decode();
      break;
    }

    buffer += decoder.decode(value, {
      stream: true,
    });

    const chunks = buffer.split('\n\n');

    buffer = chunks.pop() ?? '';

    for (const chunk of chunks) {
      handleEventChunk(chunk, onEvent);
    }
  }

  if (buffer.trim()) {
    handleEventChunk(buffer, onEvent);
  }
}

function handleEventChunk(
  chunk: string,
  onEvent: (event: AgentStreamEvent) => void,
) {
  const data = chunk
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.replace(/^data:\s?/, ''))
    .join('\n');

  if (!data) {
    return;
  }

  const event = JSON.parse(data) as AgentStreamEvent;

  onEvent(event);
}
