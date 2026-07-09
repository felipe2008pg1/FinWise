// Redirect if already logged in
if (Auth.isLoggedIn() && !window.location.pathname.includes('dashboard')) {
  window.location.href = '/pages/dashboard.html';
}

// ===== LOGIN =====
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn   = document.getElementById('loginBtn');
    const error = document.getElementById('loginError');
    const email    = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    // Frontend validation — prevents unnecessary requests, not a security boundary
    if (!email || !password) {
      error.textContent = 'Please fill in all fields.';
      error.classList.remove('hidden');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div>';
    error.classList.add('hidden');

    try {
      await Auth.login(email, password);
      window.location.href = '/pages/dashboard.html';
    } catch (err) {
      // Display the sanitized error message from the backend
      error.textContent = err.message;
      error.classList.remove('hidden');
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Entrar';
    }
  });
}

// ===== REGISTER =====
const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn     = document.getElementById('registerBtn');
    const error   = document.getElementById('registerError');
    const success = document.getElementById('registerSuccess');
    const email     = document.getElementById('email').value.trim();
    const password  = document.getElementById('password').value;
    const full_name = document.getElementById('full_name').value.trim();

    // Frontend validation — backend validates again independently
    if (!email || !password || !full_name) {
      error.textContent = 'Please fill in all fields.';
      error.classList.remove('hidden');
      return;
    }
    if (password.length < 6) {
      error.textContent = 'Password must be at least 6 characters.';
      error.classList.remove('hidden');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div>';
    error.classList.add('hidden');
    success.classList.add('hidden');

    try {
      await Auth.register(email, password, full_name);
      success.textContent = 'Registration complete! Please check your email to confirm your account.';
      success.classList.remove('hidden');
      registerForm.reset();
    } catch (err) {
      error.textContent = err.message;
      error.classList.remove('hidden');
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Criar conta';
    }
  });
}
