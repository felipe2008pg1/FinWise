if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

let goals = [];

function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function formatDate(dateStr) {
  if (!dateStr) return 'Sem prazo';
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('pt-BR');
}

function openModal() {
  document.getElementById('modalOverlay').classList.add('active');
  document.getElementById('goalTitle').value = '';
  document.getElementById('goalTarget').value = '';
  document.getElementById('goalCurrent').value = '0';
  document.getElementById('goalDeadline').value = '';
  document.getElementById('formError').classList.add('hidden');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
}

function closeAddValueModal() {
  document.getElementById('addValueModal').classList.remove('active');
}

function openAddValueModal(id, current, target) {
  document.getElementById('addValueGoalId').value = id;
  document.getElementById('addValueCurrent').value = current;
  document.getElementById('addValueTarget').value = target;
  document.getElementById('addValueInput').value = '';
  document.getElementById('addValueModal').classList.add('active');
}

function renderGoals() {
  const container = document.getElementById('goalsList');

  if (goals.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>🎯</p>
        <span>Nenhuma meta cadastrada ainda</span>
      </div>`;
    return;
  }

  container.innerHTML = `<div class="goals-grid">${goals.map(g => {
    const pct = Math.min(100, Math.round((g.current_amount / g.target_amount) * 100));
    return `
      <div class="goal-card ${g.status === 'completed' ? 'goal-completed' : ''}">
        <div class="goal-card-header">
          <div>
            <p class="goal-card-title">${escHtml(g.title)}</p>
            <p class="goal-card-deadline">Prazo: ${escHtml(formatDate(g.deadline))}</p>
          </div>
          <div class="goal-card-actions">
            ${g.status !== 'completed' ? `<button class="icon-btn" onclick="openAddValueModal('${escHtml(g.id)}', ${g.current_amount}, ${g.target_amount})">➕</button>` : ''}
            <button class="icon-btn" onclick="completeGoal('${escHtml(g.id)}')">✅</button>
            <button class="icon-btn" onclick="deleteGoal('${escHtml(g.id)}')">🗑</button>
          </div>
        </div>
        <p class="goal-card-current">${escHtml(formatMoney(g.current_amount))}</p>
        <p class="goal-card-target">de ${escHtml(formatMoney(g.target_amount))}</p>
        <div class="progress-bar">
          <div class="progress-fill" style="width:${pct}%"></div>
        </div>
        <p class="goal-card-pct">${pct}% concluído</p>
      </div>`;
  }).join('')}</div>`;
}

async function saveGoal() {
  const btn = document.getElementById('saveBtn');
  const error = document.getElementById('formError');
  const title = document.getElementById('goalTitle').value.trim();
  const target_amount = parseFloat(document.getElementById('goalTarget').value);
  const current_amount = parseFloat(document.getElementById('goalCurrent').value) || 0;
  const deadline = document.getElementById('goalDeadline').value || null;

  if (!title || !target_amount) {
    error.textContent = 'Preencha título e valor alvo.';
    error.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div>';
  error.classList.add('hidden');

  try {
    await Goals.create({ title, target_amount, current_amount, deadline });
    closeModal();
    await loadGoals();
  } catch (err) {
    error.textContent = err.message;
    error.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Salvar meta';
  }
}

async function confirmAddValue() {
  const id = document.getElementById('addValueGoalId').value;
  const current = parseFloat(document.getElementById('addValueCurrent').value);
  const target = parseFloat(document.getElementById('addValueTarget').value);
  const add = parseFloat(document.getElementById('addValueInput').value);

  if (!add || add <= 0) return;

  const newCurrent = Math.min(current + add, target);
  const status = newCurrent >= target ? 'completed' : 'active';

  await Goals.update(id, {
    title: goals.find(g => g.id === id)?.title,
    target_amount: target,
    current_amount: newCurrent,
    deadline: goals.find(g => g.id === id)?.deadline
  });

  closeAddValueModal();
  await loadGoals();
}

async function completeGoal(id) {
  if (!confirm('Marcar meta como concluída?')) return;
  await Goals.complete(id);
  await loadGoals();
}

async function deleteGoal(id) {
  if (!confirm('Deletar esta meta?')) return;
  await Goals.delete(id);
  await loadGoals();
}

async function loadGoals() {
  goals = await Goals.getAll();
  renderGoals();
}

loadGoals();
