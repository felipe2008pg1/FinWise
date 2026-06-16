// Verifica autenticação
if (!Auth.isLoggedIn()) {
  window.location.href = '/pages/login.html';
}

// Data atual
document.getElementById('currentDate').textContent = new Date().toLocaleDateString('pt-BR', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

// Nome do usuário
const user = getUser();
if (user) {
  document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;
}

// Formata moeda
function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

// Formata data
function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('pt-BR');
}

// ===== CARREGA DASHBOARD =====
async function loadDashboard() {
  try {
    const [transactions, goals] = await Promise.all([
      Transactions.getAll(),
      Goals.getAll()
    ]);

    // Resumo
    const income = transactions.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
    const expense = transactions.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);

    document.getElementById('totalIncome').textContent = formatMoney(income);
    document.getElementById('totalExpense').textContent = formatMoney(expense);
    document.getElementById('totalBalance').textContent = formatMoney(income - expense);

    // Transações recentes
    const recent = transactions.slice(0, 8);
    const container = document.getElementById('recentTransactions');

    if (recent.length === 0) {
      container.innerHTML = '<p class="text-muted text-center">Nenhuma transação ainda</p>';
    } else {
      container.innerHTML = recent.map(t => `
        <div class="transaction-item">
          <div class="transaction-info">
            <div class="transaction-icon">${t.categories?.icon || (t.type === 'income' ? '📈' : '📉')}</div>
            <div>
              <p class="transaction-title">${t.title}</p>
              <p class="transaction-date">${formatDate(t.date)}</p>
            </div>
          </div>
          <span class="transaction-amount ${t.type === 'income' ? 'text-success' : 'text-danger'}">
            ${t.type === 'income' ? '+' : '-'} ${formatMoney(t.amount)}
          </span>
        </div>
      `).join('');
    }

    // Gráfico por categoria
    const expensesByCategory = {};
    transactions.filter(t => t.type === 'expense').forEach(t => {
      const cat = t.categories?.name || 'Outros';
      expensesByCategory[cat] = (expensesByCategory[cat] || 0) + t.amount;
    });

    const ctx = document.getElementById('categoryChart').getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(expensesByCategory),
        datasets: [{
          data: Object.values(expensesByCategory),
          backgroundColor: ['#6366f1','#22c55e','#f59e0b','#ef4444','#8b5cf6','#ec4899'],
          borderWidth: 0
        }]
      },
      options: {
        plugins: {
          legend: { labels: { color: '#94a3b8', font: { size: 13 } } }
        }
      }
    });

    // Metas
    const goalsContainer = document.getElementById('goalsList');
    const activeGoals = goals.filter(g => g.status === 'active');

    if (activeGoals.length === 0) {
      goalsContainer.innerHTML = '<p class="text-muted text-center">Nenhuma meta cadastrada</p>';
    } else {
      goalsContainer.innerHTML = activeGoals.map(g => {
        const pct = Math.min((g.current_amount / g.target_amount) * 100, 100).toFixed(0);
        return `
          <div class="goal-item">
            <div class="goal-header">
              <span class="goal-title">${g.title}</span>
              <span class="goal-values">${formatMoney(g.current_amount)} / ${formatMoney(g.target_amount)} (${pct}%)</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${pct}%"></div>
            </div>
          </div>
        `;
      }).join('');
    }

  } catch (err) {
    console.error('Erro ao carregar dashboard:', err);
  }
}

loadDashboard();