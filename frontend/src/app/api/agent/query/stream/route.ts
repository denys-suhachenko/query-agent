import { backendFetch } from '@/shared/api/backend';

export async function POST(request: Request) {
  const body = await request.text();

  const response = await backendFetch('/api/agent/query/stream/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body,
    cache: 'no-store',
  });

  if (!response.ok) {
    const error = await response.text();

    return Response.json(
      {
        error: error || 'Agent request failed',
      },
      {
        status: response.status,
      },
    );
  }

  if (!response.body) {
    return Response.json(
      {
        error: 'Backend returned no response stream',
      },
      {
        status: 500,
      },
    );
  }

  return new Response(response.body, {
    status: 200,
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'X-Accel-Buffering': 'no',
    },
  });
}
