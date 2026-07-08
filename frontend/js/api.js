const API_URL = 'https://finwise-1cjo.onrender.com';

// ===== SECURITY: XSS ESCAPE =====
function escHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

// ===== TOKEN =====
function getToken() {
  return localStorage.getItem('finwise_token');
}

function getRefreshToken() {
  return localStorage.getItem('finwise_refresh_token');
}

function setToken(token) {
  localStorage.setItem('finwise_token', token);
}

function setRefreshToken(token) {
  localStorage.setItem('finwise_refresh_token', token);
}

function removeToken() {
  localStorage.removeItem('finwise_token');
  localStorage.removeItem('finwise_refresh_token');
  localStorage.removeItem('finwise_user');
}

function getUser() {
  const user = localStorage.getItem('finwise_user');
  return user ? JSON.parse(user) : null;
}

function setUser(user) {
  localStorage.setItem('finwise_user', JSON.stringify(user));
}

// ===== HEADERS =====
function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

// ===== REFRESH TOKEN =====
let isRefreshing = false;
let refreshQueue = [];

async function tryRefreshToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (!res.ok) return false;

    const data = await res.json();
    setToken(data.access_token);
    setRefreshToken(data.refresh_token);
    setUser(data.user);
    return true;
  } catch {
    return false;
  }
}

// ===== REQUEST BASE =====
async function request(method, path, body = null) {
  const options = {
    method,
    headers: authHeaders()
  };
  if (body) options.body = JSON.stringify(body);

  let res = await fetch(`${API_URL}${path}`, options);

  // If you receive a 401, try to automatically renew the token once.
  if (res.status === 401) {
    if (isRefreshing) {
      // Wait for the refresh in progress before trying again.
      await new Promise(resolve => refreshQueue.push(resolve));
      res = await fetch(`${API_URL}${path}`, { ...options, headers: authHeaders() });
    } else {
      isRefreshing = true;
      const refreshed = await tryRefreshToken();
      isRefreshing = false;
      refreshQueue.forEach(resolve => resolve());
      refreshQueue = [];

      if (refreshed) {
        // Retry with the new token
        res = await fetch(`${API_URL}${path}`, { ...options, headers: authHeaders() });
      } else {
        // Refresh failed — logging out
        removeToken();
        window.location.href = '/pages/login.html';
        return;
      }
    }
  }

  // If you still get a 401 error after refreshing, log out.
  if (res.status === 401) {
    removeToken();
    window.location.href = '/pages/login.html';
    return;
  }

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Unexpected error');
  return data;
}

// ===== AUTH =====
const Auth = {
  async login(email, password) {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');
    setToken(data.access_token);
    setRefreshToken(data.refresh_token);
    setUser(data.user);
    return data;
  },

  async register(email, password, full_name) {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');
    return data;
  },

  logout() {
    removeToken();
    window.location.href = '/pages/login.html';
  },

  isLoggedIn() {
    return !!getToken();
  }
};

// ===== TRANSACTIONS =====
const Transactions = {
  getAll: () => request('GET', '/transactions/'),
  create: (data) => request('POST', '/transactions/', data),
  update: (id, data) => request('PUT', `/transactions/${id}`, data),
  delete: (id) => request('DELETE', `/transactions/${id}`)
};

// ===== CATEGORIES =====
const Categories = {
  getAll: () => request('GET', '/categories/'),
  create: (data) => request('POST', '/categories/', data),
  update: (id, data) => request('PUT', `/categories/${id}`, data),
  delete: (id) => request('DELETE', `/categories/${id}`)
};

// ===== GOALS =====
const Goals = {
  getAll: () => request('GET', '/goals/'),
  create: (data) => request('POST', '/goals/', data),
  update: (id, data) => request('PUT', `/goals/${id}`, data),
  complete: (id) => request('PATCH', `/goals/${id}/complete`),
  delete: (id) => request('DELETE', `/goals/${id}`)
};

// ===== DEBTS =====
const Debts = {
  getAll: () => request('GET', '/debts/'),
  create: (data) => request('POST', '/debts/', data),
  update: (id, data) => request('PUT', `/debts/${id}`, data),
  pay: (id) => request('PATCH', `/debts/${id}/pay`),
  simulate: (id) => request('GET', `/debts/${id}/simulate`),
  delete: (id) => request('DELETE', `/debts/${id}`)
};

// ===== AI =====
const AI = {
  chat: (content) => request('POST', '/ai/chat', { content }),
  getHistory: () => request('GET', '/ai/history'),
  clearHistory: () => request('DELETE', '/ai/history')
};
