/**
 * client.js
 * API communication layer for SatQuery AI.
 */

export const API_BASE_HOST = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
export const API_BASE = `${API_BASE_HOST}/api`;

/**
 * Resolves relative sample or report paths into full backend URLs
 */
export function getFullApiUrl(path) {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_HOST}${cleanPath}`;
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function fetchDemos() {
  const res = await fetch(`${API_BASE}/demos`);
  if (!res.ok) throw new Error('Failed to load demo scenarios');
  return res.json();
}

export async function runDemoScenario(demoId) {
  const res = await fetch(`${API_BASE}/demos/run/${demoId}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Demo execution failed' }));
    throw new Error(err.detail || 'Demo execution failed');
  }
  return res.json();
}

export async function analyzeCustomQuery(query, files) {
  const formData = new FormData();
  formData.append('query', query);
  for (const f of files) {
    formData.append('files', f);
  }

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail || 'Analysis failed');
  }
  return res.json();
}

export async function prescanFiles(files) {
  const formData = new FormData();
  for (const f of files) {
    formData.append('files', f);
  }

  const res = await fetch(`${API_BASE}/prescan`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Prescan failed' }));
    throw new Error(err.detail || 'Prescan failed');
  }
  return res.json();
}
