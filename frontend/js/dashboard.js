// Check authentication
if (!Auth.isLoggedIn()) {
  window.location.href = '/pages/login.html';
}

// Current date
document.getElementById('currentDate').textContent = new Date().toLocaleDateString('pt-BR', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

// Username
const user = getUser();
if (user) {
  document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;
}

// Format currency
function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

// Format date
function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('pt-BR');
}

// ===== LOAD DASHBOARD =====
async function loadDashboard() {
  try {
    const [transactions, goals] = await Promise.all([
      Transactions.getAll(),
      Goals.getAll()
    ]);

    // Summary
    const income  = transactions.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
    const expense = transactions.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
    document.getElementById('totalIncome').textContent  = formatMoney(income);
    document.getElementById('totalExpense').textContent = formatMoney(expense);
    document.getElementById('totalBalance').textContent = formatMoney(income - expense);

    // Recent transactions — all data escaped before inserting into the DOM
    const recent = transactions.slice(0, 8);
    const container = document.getElementById('recentTransactions');
    if (recent.length === 0) {
      container.innerHTML = '<p class="text-muted text-center">Nenhuma transação ainda</p>';
    } else {
      container.innerHTML = recent.map(t => `
        <div class="transaction-item">
          <div class="transaction-info">
            <div class="transaction-icon">${escHtml(t.categories?.icon) || (t.type === 'income' ? '📈' : '📉')}</div>
            <div>
              <p class="transaction-title">${escHtml(t.title)}</p>
              <p class="transaction-date">${escHtml(formatDate(t.date))}</p>
            </div>
          </div>
          <span class="transaction-amount ${t.type === 'income' ? 'text-success' : 'text-danger'}">
            ${t.type === 'income' ? '+' : '-'} ${escHtml(formatMoney(t.amount))}
          </span>
        </div>
      `).join('');
    }

    // Expense chart by category
    const expensesByCategory = {};
    transactions.filter(t => t.type === 'expense').forEach(t => {
      const cat = t.categories?.name || 'Others';
      expensesByCategory[cat] = (expensesByCategory[cat] || 0) + t.amount;
    });
    const ctx = document.getElementById('categoryChart').getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        // Category names are not inserted via innerHTML — Chart.js handles rendering safely
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

    // Active goals — all data escaped before inserting into the DOM
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
              <span class="goal-title">${escHtml(g.title)}</span>
              <span class="goal-values">${escHtml(formatMoney(g.current_amount))} / ${escHtml(formatMoney(g.target_amount))} (${escHtml(pct)}%)</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${escHtml(pct)}%"></div>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (err) {
    // Error logged to console only — never exposed to the user
    console.error('Dashboard load error:', err);
  }
}

loadDashboard();
