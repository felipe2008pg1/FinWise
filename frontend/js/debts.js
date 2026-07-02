if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

let debts = [];

function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function openModal() {
  document.getElementById('modalOverlay').classList.add('active');
  document.getElementById('debtTitle').value = '';
  document.getElementById('debtTotal').value = '';
  document.getElementById('debtRemaining').value = '';
  document.getElementById('debtRate').value = '0';
  document.getElementById('debtPayment').value = '';
  document.getElementById('debtDueDay').value = '';
  document.getElementById('formError').classList.add('hidden');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
}

function renderDebts() {
  const container = document.getElementById('debtsList');

  if (debts.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>💳</p>
        <span>Nenhuma dívida cadastrada ainda</span>
      </div>`;
    return;
  }

  container.innerHTML = `<div class="debts-grid">${debts.map(d => {
    const pct = Math.min(100, Math.round(((d.total_amount - d.remaining_amount) / d.total_amount) * 100));
    return `
      <div class="debt-card ${d.status === 'paid' ? 'paid' : ''}">
        <div class="debt-card-header">
          <div class="debt-card-title">${escHtml(d.title)}</div>
          <div class="debt-actions">
            ${d.status !== 'paid' ? `<button class="icon-btn" onclick="payDebt('${escHtml(d.id)}')">✅</button>` : ''}
            <button class="icon-btn" onclick="simulateDebt('${escHtml(d.id)}')">🧮</button>
            <button class="icon-btn" onclick="deleteDebt('${escHtml(d.id)}')">🗑</button>
          </div>
        </div>
        <p class="debt-remaining">${escHtml(formatMoney(d.remaining_amount))}</p>
        <p class="debt-total">de ${escHtml(formatMoney(d.total_amount))}</p>
        <div class="progress-bar">
          <div class="progress-fill" style="width:${pct}%"></div>
        </div>
        <div class="debt-info">
          <div class="debt-info-item">Taxa<span>${escHtml(String(d.interest_rate))}% a.m.</span></div>
          <div class="debt-info-item">Parcela<span>${escHtml(formatMoney(d.monthly_payment || 0))}</span></div>
          ${d.due_day ? `<div class="debt-info-item">Vencimento<span>Dia ${escHtml(String(d.due_day))}</span></div>` : ''}
        </div>
        <div id="simulate-${escHtml(d.id)}"></div>
      </div>`;
  }).join('')}</div>`;
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
  error.classList.add('hidden');

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

async function payDebt(id) {
  if (!confirm('Marcar dívida como paga?')) return;
  await Debts.pay(id);
  await loadDebts();
}

async function simulateDebt(id) {
  const result = await Debts.simulate(id);
  const box = document.getElementById(`simulate-${id}`);
  if (!box) return;
  if (result.error) {
    box.innerHTML = `<div class="simulate-box"><p>${escHtml(result.error)}</p></div>`;
    return;
  }
  box.innerHTML = `
    <div class="simulate-box">
      <p>Simulação de pagamento</p>
      <strong>Meses para quitar: ${escHtml(String(result.months_to_pay))}</strong><br>
      <strong>Total pago: ${escHtml(formatMoney(result.total_paid))}</strong><br>
      <strong>Total de juros: ${escHtml(formatMoney(result.total_interest))}</strong>
    </div>`;
}

async function deleteDebt(id) {
  if (!confirm('Deletar esta dívida?')) return;
  await Debts.delete(id);
  await loadDebts();
}

async function loadDebts() {
  debts = await Debts.getAll();
  renderDebts();
}

loadDebts();
