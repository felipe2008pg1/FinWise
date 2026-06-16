// Redireciona se já estiver logado
if (Auth.isLoggedIn() && !window.location.pathname.includes('dashboard')) {
  window.location.href = '/pages/dashboard.html';
}

// ===== LOGIN =====
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('loginBtn');
    const error = document.getElementById('loginError');

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div>';
    error.classList.add('hidden');

    try {
      await Auth.login(
        document.getElementById('email').value,
        document.getElementById('password').value
      );
      window.location.href = '/pages/dashboard.html';
    } catch (err) {
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
    const btn = document.getElementById('registerBtn');
    const error = document.getElementById('registerError');
    const success = document.getElementById('registerSuccess');

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner"></div>';
    error.classList.add('hidden');
    success.classList.add('hidden');

    try {
      await Auth.register(
        document.getElementById('email').value,
        document.getElementById('password').value,
        document.getElementById('full_name').value
      );
      success.textContent = 'Cadastro realizado! Faça login.';
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