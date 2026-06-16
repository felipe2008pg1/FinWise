if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

const chatBox = document.getElementById('chatBox');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

function formatTime() {
  return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function addMessage(role, content) {
  const welcome = chatBox.querySelector('.welcome-message');
  if (welcome) welcome.remove();

  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.innerHTML = `
    <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
    <div>
      <div class="message-content">${content.replace(/\n/g, '<br>')}</div>
      <div class="message-time">${formatTime()}</div>
    </div>
  `;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'message assistant';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) indicator.remove();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function sendSuggestion(btn) {
  chatInput.value = btn.textContent;
  sendMessage();
}

async function sendMessage() {
  const content = chatInput.value.trim();
  if (!content) return;

  chatInput.value = '';
  sendBtn.disabled = true;

  addMessage('user', content);
  showTyping();

  try {
    const res = await AI.chat(content);
    removeTyping();
    addMessage('assistant', res.reply);
  } catch (err) {
    removeTyping();
    document.getElementById('noCredits').style.display = 'block';
    addMessage('assistant', '⚠️ Não consegui processar sua mensagem. Verifique se há créditos na conta Anthropic.');
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

async function clearHistory() {
  if (!confirm('Limpar todo o histórico do chat?')) return;
  await AI.clearHistory();
  chatBox.innerHTML = `
    <div class="welcome-message">
      <h3>👋 Olá! Sou o FinBot</h3>
      <p>Histórico limpo! Como posso te ajudar?</p>
      <div class="suggestions">
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Como estão minhas finanças?</button>
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Onde posso economizar?</button>
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Me ajude a criar um orçamento</button>
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Como quitar minhas dívidas?</button>
      </div>
    </div>`;
}

// Carrega histórico anterior
async function loadHistory() {
  try {
    const history = await AI.getHistory();
    history.forEach(msg => addMessage(msg.role, msg.content));
  } catch (err) {
    console.log('Sem histórico');
  }
}

loadHistory();