import { API_BASE_URL } from '../constants.js';

export async function fetchAuctions() {
  const res = await fetch(`${API_BASE_URL}/auctions/`);
  if (!res.ok) throw new Error('Failed to fetch auctions');
  return await res.json();
}
