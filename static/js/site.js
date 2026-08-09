const fallbackSrc = '/static/fallback.jpg';

export function initDarkMode() {
  const btn = document.getElementById('dark-toggle');
  if (!btn) return;
  btn.onclick = () => document.body.classList.toggle('dark');
}

export function applyFallback(img) {
  if (!img) return;
  img.onerror = () => {
    if (img.src !== fallbackSrc) {
      img.src = fallbackSrc;
    }
  };
}

export async function loadJSON(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      console.error('Failed to load JSON', url, response.status);
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading', url, error);
    return null;
  }
}

export function showLoading(el, message = 'Loading…') {
  if (!el) return;
  el.innerHTML = `<div class="empty-state">${message}</div>`;
}

export function showNoResults(el, message = 'No results found.') {
  if (!el) return;
  el.innerHTML = `<div class="empty-state">${message}</div>`;
}

export async function loadComponent(id, url) {
  const container = document.getElementById(id);
  if (!container) return;
  try {
    const response = await fetch(url);
    if (!response.ok) return;
    container.innerHTML = await response.text();
  } catch (error) {
    console.error('Failed to load component', url, error);
  }
}

export async function loadLayout() {
  await Promise.all([
    loadComponent('nav', '/static/components/nav.html'),
    loadComponent('footer', '/static/components/footer.html'),
  ]);
  initDarkMode();
}
