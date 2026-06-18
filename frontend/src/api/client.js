import axios from 'axios';

import { API_BASE_URL } from '../constants';

const client = axios.create({ baseURL: API_BASE_URL, timeout: 60000 });

/** POST trip inputs to the backend and return the plan, throwing a clean Error on failure. */
export async function planTrip(payload) {
  try {
    const { data } = await client.post('/api/plan-trip/', payload);
    return data;
  } catch (err) {
    throw normalizeError(err);
  }
}

function normalizeError(err) {
  if (err.response) {
    const { status, data } = err.response;
    if (data && data.error) return new Error(data.error);
    if (status === 400 && data && typeof data === 'object') {
      const [field, messages] = Object.entries(data)[0] || [];
      if (field) return new Error(`${field.replace(/_/g, ' ')}: ${[].concat(messages).join(' ')}`);
    }
    if (status === 429) return new Error('Too many requests - please wait a moment and retry.');
    return new Error(`The server returned an error (HTTP ${status}).`);
  }
  if (err.request) {
    return new Error('Could not reach the server. Is the backend running and reachable?');
  }
  return new Error(err.message || 'Something went wrong.');
}
