@@ -1,133 +1,250 @@
if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

let transactions = [];
let categories = [];
let selectedType = 'income';

document.getElementById('txDate').valueAsDate = new Date();

function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('pt-BR');
}

function setType(type) {
  selectedType = type;
  document.getElementById('btnIncome').className = 'type-btn' + (type === 'income' ? ' active-income' : '');
  document.getElementById('btnExpense').className = 'type-btn' + (type === 'expense' ? ' active-expense' : '');
  populateCategorySelect();
}

function openModal() {
  document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
  document.getElementById('formError').classList.add('hidden');
}

function populateCategorySelect() {
  const select = document.getElementById('txCategory');
  const filtered = categories.filter(c => c.type === selectedType);
  select.innerHTML = '<option value="">Sem categoria</option>' +
    filtered.map(c => `<option value="${escHtml(c.id)}">${escHtml(c.icon)} ${escHtml(c.name)}</option>`).join('');
}

function renderTransactions() {
  const typeFilter = document.getElementById('filterType').value;
  const catFilter = document.getElementById('filterCategory').value;

  let filtered = transactions;
  if (typeFilter !== 'all') filtered = filtered.filter(t => t.type === typeFilter);
  if (catFilter !== 'all') filtered = filtered.filter(t => t.category_id === catFilter);

  const container = document.getElementById('transactionsList');

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>💸</p>
        <span>Nenhuma transação encontrada</span>
      </div>`;
    return;
  }

  container.innerHTML = filtered.map(t => `
    <div class="transaction-item">
      <div class="transaction-info">
        <div class="transaction-icon">${escHtml(t.categories?.icon) || (t.type === 'income' ? '📈' : '📉')}</div>
        <div>
          <p class="transaction-title">${escHtml(t.title)}</p>
          <p class="transaction-date">${escHtml(formatDate(t.date))} ${t.categories ? '· ' + escHtml(t.categories.name) : ''}</p>
        </div>
              <div style="display:flex;align-items:center;gap:12px">
        <span class="transaction-amount ${t.type === 'income' ? 'text-success' : 'text-danger'}">
          ${t.type === 'income' ? '+' : '-'} ${escHtml(formatMoney(t.amount))}
        </span>
        <button class="delete-btn" onclick="deleteTransaction('${escHtml(t.id)}')">🗑</button>
          `).join('');
}

async function saveTransaction() {
  const btn = document.getElementById('saveBtn');
  const error = document.getElementById('formError');
  const title = document.getElementById('txTitle').value.trim();
  const amount = parseFloat(document.getElementById('txAmount').value);
  const date = document.getElementById('txDate').value;
  const category_id = document.getElementById('txCategory').value || null;
  const notes = document.getElementById('txNotes').value.trim() || null;

  if (!title || !amount || !date) {
    error.textContent = 'Preencha título, valor e data.';
    error.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div>';
  error.classList.add('hidden');

  try {
    await Transactions.create({ title, amount, type: selectedType, date, category_id, notes });
    closeModal();
    await loadData();
  } catch (err) {
    error.textContent = err.message;
    error.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Salvar';
  }
}

async function deleteTransaction(id) {
  if (!confirm('Deletar esta transação?')) return;
  await Transactions.delete(id);
  await loadData();
}

async function loadData() {
  [transactions, categories] = await Promise.all([
    Transactions.getAll(),
    Categories.getAll()
  ]);

  const filterCat = document.getElementById('filterCategory');
  filterCat.innerHTML = '<option value="all">Todas categorias</option>' +
    categories.map(c => `<option value="${escHtml(c.id)}">${escHtml(c.name)}</option>`).join('');

  populateCategorySelect();
  renderTransactions();
}

loadData();
