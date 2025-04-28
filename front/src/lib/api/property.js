import { API_BASE_URL } from '../constants.js';

export async function fetchProperties() {
  const res = await fetch(`${API_BASE_URL}/properties/`);
  if (!res.ok) throw new Error('Failed to fetch properties');
  return await res.json();
}
