if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

let categories = [];
let selectedType = 'income';
let selectedIcon = '💰';
let selectedColor = '#6366f1';

const ICONS = ['💰','💻','📈','✨','🏠','🍔','🚗','💊','🎮','📚','🛍️','📦','🐶','✈️','🎓','🎁','⚡','📱','👕','🏋️','🍿','🧾'];
const COLORS = ['#6366f1','#22c55e','#ef4444','#f97316','#eab308','#14b8a6','#3b82f6','#a855f7','#ec4899','#06b6d4','#84cc16','#64748b'];

function renderPickers() {
  const iconPicker = document.getElementById('iconPicker');
  iconPicker.innerHTML = ICONS.map(icon => `
    <button type="button" class="icon-option ${icon === selectedIcon ? 'selected' : ''}" onclick="selectIcon('${icon}')">${icon}</button>
  `).join('');

  const colorPicker = document.getElementById('colorPicker');
  colorPicker.innerHTML = COLORS.map(color => `
    <button type="button" class="color-option ${color === selectedColor ? 'selected' : ''}" style="background:${color}" onclick="selectColor('${color}')"></button>
  `).join('');
}

function selectIcon(icon) {
  selectedIcon = icon;
  renderPickers();
}

function selectColor(color) {
  selectedColor = color;
  renderPickers();
}

function setType(type) {
  selectedType = type;
  document.getElementById('btnIncome').className = 'type-btn' + (type === 'income' ? ' active-income' : '');
  document.getElementById('btnExpense').className = 'type-btn' + (type === 'expense' ? ' active-expense' : '');
}

function openModal() {
  document.getElementById('modalTitle').textContent = 'Nova categoria';
  document.getElementById('editingId').value = '';
  document.getElementById('catName').value = '';
  selectedIcon = '💰';
  selectedColor = '#6366f1';
  setType('income');
  renderPickers();
  document.getElementById('formError').classList.add('hidden');
  document.getElementById('modalOverlay').classList.add('active');
}

function openEditModal(id) {
  const cat = categories.find(c => c.id === id);
  if (!cat) return;

  document.getElementById('modalTitle').textContent = 'Editar categoria';
  document.getElementById('editingId').value = cat.id;
  document.getElementById('catName').value = cat.name;
  selectedIcon = cat.icon || '💰';
  selectedColor = cat.color || '#6366f1';
  setType(cat.type);
  renderPickers();
  document.getElementById('formError').classList.add('hidden');
  document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
}

function renderCategories() {
  const incomeContainer = document.getElementById('incomeCategories');
  const expenseContainer = document.getElementById('expenseCategories');

  const incomeCats = categories.filter(c => c.type === 'income');
  const expenseCats = categories.filter(c => c.type === 'expense');

  incomeContainer.innerHTML = incomeCats.length
    ? incomeCats.map(renderCard).join('')
    : '<p class="empty-state">Nenhuma categoria de receita ainda.</p>';

  expenseContainer.innerHTML = expenseCats.length
    ? expenseCats.map(renderCard).join('')
    : '<p class="empty-state">Nenhuma categoria de despesa ainda.</p>';
}

function renderCard(cat) {
  return `
    <div class="category-card">
      <div class="category-icon" style="background:${cat.color}25; color:${cat.color}">${cat.icon}</div>
      <span class="category-name">${cat.name}</span>
      <div class="category-actions">
        <button class="icon-btn" onclick="openEditModal('${cat.id}')">✏️</button>
        <button class="icon-btn" onclick="removeCategory('${cat.id}')">🗑</button>
      </div>
    </div>
  `;
}

async function saveCategory() {
  const btn = document.getElementById('saveBtn');
  const error = document.getElementById('formError');
  const name = document.getElementById('catName').value.trim();
  const editingId = document.getElementById('editingId').value;

  if (!name) {
    error.textContent = 'Digite um nome para a categoria.';
    error.classList.remove('hidden');
    return;
  }

  const payload = { name, type: selectedType, color: selectedColor, icon: selectedIcon };

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div>';
  error.classList.add('hidden');

  try {
    if (editingId) {
      await Categories.update(editingId, payload);
    } else {
      await Categories.create(payload);
    }
    closeModal();
    await loadCategories();
  } catch (err) {
    error.textContent = err.message;
    error.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Salvar categoria';
  }
}

async function removeCategory(id) {
  if (!confirm('Excluir esta categoria? Transações que usam ela ficarão sem categoria.')) return;
  await Categories.delete(id);
  await loadCategories();
}

async function loadCategories() {
  categories = await Categories.getAll();
  renderCategories();
}

renderPickers();
loadCategories();