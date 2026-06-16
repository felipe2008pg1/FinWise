if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

let debts = [];

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

async function simulate(id, btn) {
  btn.disabled = true;
  btn.textContent = '⏳';

  try {
    const res = await Debts.simulate(id);
    const card = btn.closest('.debt-card');
    const existing = card.querySelector('.simulate-box');
    if (existing) existing.remove();

    const box = document.createElement('div');
    box.className = 'simulate-box';
    box.innerHTML = `
      <p>⏱ Meses para quitar: <strong>${res.months_to_pay}</strong></p>
      <p>💰 Total a pagar: <strong>${formatMoney(res.total_paid)}</strong></p>
      <p>📈 Total em juros: <strong>${formatMoney(res.total_interest)}</strong></p>
    `;
    btn.closest('.debt-actions').after(box);
  } catch (err) {
    alert('Erro ao simular: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '📊 Simular';
  }
}

async function payDebt(id) {
  if (!confirm('Marcar dívida como paga?')) return;
  await Debts.pay(id);
  await loadDebts();
}

async function deleteDebt(id) {
  if (!confirm('Deletar esta dívida?')) return;
  await Debts.delete(id);
  await loadDebts();
}

function renderDebts() {
  const container = document.getElementById('debtsList');

  if (debts.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>💳</p>
        <span>Nenhuma dívida cadastrada</span>
      </div>`;
    return;
  }

  const active = debts.filter(d => d.status === 'active');
  const paid = debts.filter(d => d.status === 'paid');

  let html = '<div class="debts-grid">';

  active.forEach(d => {
    const pct = Math.min(((d.total_amount - d.remaining_amount) / d.total_amount) * 100, 100).toFixed(0);
    html += `
      <div class="debt-card">
        <div class="debt-card-header">
          <p class="debt-card-title">💳 ${d.title}</p>
          <button class="icon-btn" onclick="deleteDebt('${d.id}')">🗑</button>
        </div>
        <p class="debt-remaining">${formatMoney(d.remaining_amount)}</p>
        <p class="debt-total">de ${formatMoney(d.total_amount)} · ${pct}% pago</p>
        <div class="progress-bar">
          <div class="progress-fill" style="width:${pct}%;background:var(--danger)"></div>
        </div>
        <div class="debt-info">
          ${d.interest_rate ? `<div class="debt-info-item">Juros<span>${d.interest_rate}% a.m.</span></div>` : ''}
          ${d.monthly_payment ? `<div class="debt-info-item">Parcela<span>${formatMoney(d.monthly_payment)}</span></div>` : ''}
          ${d.due_day ? `<div class="debt-info-item">Vencimento<span>Dia ${d.due_day}</span></div>` : ''}
        </div>
        <div class="debt-actions">
          <button class="btn btn-success btn-sm" onclick="payDebt('${d.id}')">✅ Quitar</button>
          ${d.monthly_payment ? `<button class="btn btn-ghost btn-sm" onclick="simulate('${d.id}', this)">📊 Simular</button>` : ''}
        </div>
      </div>`;
  });

  if (paid.length > 0) {
    html += '</div><h2 style="margin:24px 0 16px;font-size:16px;color:var(--text-muted)">✅ Quitadas</h2><div class="debts-grid">';
    paid.forEach(d => {
      html += `
        <div class="debt-card paid">
          <div class="debt-card-header">
            <p class="debt-card-title">✅ ${d.title}</p>
            <button class="icon-btn" onclick="deleteDebt('${d.id}')">🗑</button>
          </div>
          <p class="debt-remaining" style="color:var(--success)">${formatMoney(d.total_amount)}</p>
          <p class="debt-total">Dívida quitada!</p>
        </div>`;
    });
  }

  html += '</div>';
  container.innerHTML = html;
}

async function saveDebt() {
  const btn = document.getElementById('saveBtn');
  const error = document.getElementById('formError');
  const title = document.getElementById('debtTitle').value.trim();
  const total_amount = parseFloat(document.getElementById('debtTotal').value);
  const remaining_amount = parseFloat(document.getElementById('debtRemaining').value);
  const interest_rate = parseFloat(document.getElementById('debtRate').value) || 0;
  const monthly_payment = parseFloat(document.getElementById('debtPayment').value) || null;
  const due_day = parseInt(document.getElementById('debtDueDay').value) || null;

  if (!title || !total_amount || !remaining_amount) {
    error.textContent = 'Preencha título, valor total e valor restante.';
    error.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div>';

  try {
    await Debts.create({ title, total_amount, remaining_amount, interest_rate, monthly_payment, due_day });
    closeModal();
    await loadDebts();
  } catch (err) {
    error.textContent = err.message;
    error.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Salvar dívida';
  }
}

async function loadDebts() {
  debts = await Debts.getAll();
  renderDebts();
}

loadDebts();