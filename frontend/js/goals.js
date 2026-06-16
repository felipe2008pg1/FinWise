if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

let goals = [];

function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function openModal() {
  document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
  document.getElementById('formError').classList.add('hidden');
}

function openAddValueModal(id, current, target) {
  document.getElementById('addValueGoalId').value = id;
  document.getElementById('addValueCurrent').value = current;
  document.getElementById('addValueTarget').value = target;
  document.getElementById('addValueInput').value = '';
  document.getElementById('addValueModal').classList.add('active');
}

function closeAddValueModal() {
  document.getElementById('addValueModal').classList.remove('active');
}

async function confirmAddValue() {
  const id = document.getElementById('addValueGoalId').value;
  const current = parseFloat(document.getElementById('addValueCurrent').value);
  const target = parseFloat(document.getElementById('addValueTarget').value);
  const add = parseFloat(document.getElementById('addValueInput').value);

  if (!add || add <= 0) return;

  const newAmount = Math.min(current + add, target);
  const goal = goals.find(g => g.id === id);

  await Goals.update(id, {
    title: goal.title,
    target_amount: goal.target_amount,
    current_amount: newAmount,
    deadline: goal.deadline || null
  });

  if (newAmount >= target) await Goals.complete(id);

  closeAddValueModal();
  await loadGoals();
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

  const active = goals.filter(g => g.status === 'active');
  const completed = goals.filter(g => g.status === 'completed');

  let html = '<div class="goals-grid">';

  active.forEach(g => {
    const pct = Math.min((g.current_amount / g.target_amount) * 100, 100).toFixed(0);
    html += `
      <div class="goal-card">
        <div class="goal-card-header">
          <div>
            <p class="goal-card-title">${g.title}</p>
            ${g.deadline ? `<p class="goal-card-deadline">📅 Prazo: ${new Date(g.deadline + 'T00:00:00').toLocaleDateString('pt-BR')}</p>` : ''}
          </div>
          <div class="goal-card-actions">
            <button class="icon-btn" onclick="openAddValueModal('${g.id}', ${g.current_amount}, ${g.target_amount})" title="Adicionar valor">➕</button>
            <button class="icon-btn" onclick="deleteGoal('${g.id}')" title="Deletar">🗑</button>
          </div>
        </div>
        <p class="goal-card-current">${formatMoney(g.current_amount)}</p>
        <p class="goal-card-target">de ${formatMoney(g.target_amount)}</p>
        <div class="progress-bar" style="margin-top:12px">
          <div class="progress-fill" style="width:${pct}%"></div>
        </div>
        <p class="goal-card-pct">${pct}% concluído</p>
      </div>`;
  });

  if (completed.length > 0) {
    html += '</div><h2 style="margin:24px 0 16px;font-size:16px;color:var(--text-muted)">✅ Concluídas</h2><div class="goals-grid">';
    completed.forEach(g => {
      html += `
        <div class="goal-card goal-completed">
          <div class="goal-card-header">
            <p class="goal-card-title">✅ ${g.title}</p>
            <button class="icon-btn" onclick="deleteGoal('${g.id}')">🗑</button>
          </div>
          <p class="goal-card-current">${formatMoney(g.target_amount)}</p>
          <p class="goal-card-target">Meta atingida!</p>
          <div class="progress-bar" style="margin-top:12px">
            <div class="progress-fill" style="width:100%;background:var(--success)"></div>
          </div>
        </div>`;
    });
  }

  html += '</div>';
  container.innerHTML = html;
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