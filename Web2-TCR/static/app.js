// ── THEME ─────────────────────────────────────────────────────────────────────
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const next = isDark ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  document.getElementById('themeLabel').textContent = isDark ? 'Light Mode' : 'Dark Mode';
  document.querySelector('.toggle-icon').textContent = isDark ? '☀️' : '🌙';
}

// ── AUTH ──────────────────────────────────────────────────────────────────────
async function doLogin() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  const res = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (res.ok) {
    const data = await res.json();
    showDashboard(data.username || username);
    pollWhoami(); // start polling server for role changes
  } else {
    const err = document.getElementById('errorMsg');
    err.classList.add('show');
    setTimeout(() => err.classList.remove('show'), 3000);
  }
}

async function doLogout() {
  await fetch('/api/logout', { method: 'POST' });
  clearInterval(window._pollInterval);
  document.getElementById('loginCard').style.display = '';
  document.getElementById('dashboard').classList.remove('visible');
  document.getElementById('adminPanel').classList.remove('visible');
  document.getElementById('flagBox').textContent = '';
  document.getElementById('username').value = '';
  document.getElementById('password').value = '';
}

function showDashboard(username) {
  document.getElementById('loginCard').style.display = 'none';
  document.getElementById('dashboard').classList.add('visible');
  document.getElementById('avatarText').textContent = username.charAt(0).toUpperCase();
  document.getElementById('usernameDisplay').textContent = username;
}

// ── SERVER POLLING ─────────────────────────────────────────────────────────────
// Asks the server every second to check the current cookie.
// Flag only arrives here if server says role == admin.
async function pollWhoami() {
  clearInterval(window._pollInterval);
  window._pollInterval = setInterval(async () => {
    try {
      const res = await fetch('/api/whoami');
      if (!res.ok) return;
      const data = await res.json();

      if (data.role === 'admin' && data.flag) {
        document.getElementById('flagBox').textContent = data.flag;
        document.getElementById('adminPanel').classList.add('visible');
      } else {
        document.getElementById('adminPanel').classList.remove('visible');
        document.getElementById('flagBox').textContent = '';
      }
    } catch (_) { /* network error, ignore */ }
  }, 1000);
}

// ── ON LOAD: restore session if cookie still valid ────────────────────────────
window.addEventListener('DOMContentLoaded', async () => {
  // Enter key support
  ['username', 'password'].forEach(id => {
    document.getElementById(id).addEventListener('keydown', e => {
      if (e.key === 'Enter') doLogin();
    });
  });

  // Try to restore session from existing cookie
  try {
    const res = await fetch('/api/whoami');
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated) {
        showDashboard('player');
        pollWhoami();
        if (data.role === 'admin' && data.flag) {
          document.getElementById('flagBox').textContent = data.flag;
          document.getElementById('adminPanel').classList.add('visible');
        }
      }
    }
  } catch (_) { /* no session */ }
});
