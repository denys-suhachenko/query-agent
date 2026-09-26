import { NextRequest, NextResponse } from 'next/server';

import { backendFetch } from '@/shared/api/backend';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await backendFetch('/api/agent/query/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      cache: 'no-store',
    });

    const contentType = response.headers.get('content-type');

    if (!contentType?.includes('application/json')) {
      const text = await response.text();

      console.error(
        'Backend returned non-JSON response:',
        response.status,
        text,
      );

      return NextResponse.json(
        {
          error: 'Backend returned an invalid response',
        },
        {
          status: response.status || 500,
        },
      );
    }

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    console.error('Agent API error:', error);

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Internal server error',
      },
      { status: 500 },
    );
  }
}
