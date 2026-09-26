import 'server-only';

const BACKEND_URL = process.env.BACKEND_URL;

export async function backendFetch(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  if (!BACKEND_URL) {
    throw new Error('BACKEND_URL is not configured');
  }

  return fetch(`${BACKEND_URL}${path}`, init);
}
