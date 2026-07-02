if (!Auth.isLoggedIn()) window.location.href = '/pages/login.html';

const user = getUser();
if (user) document.getElementById('userName').textContent = user.user_metadata?.full_name || user.email;

const chatBox = document.getElementById('chatBox');

function getTime() {
  return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function appendMessage(role, content) {
  // Removes a welcome message if it exists.
  const welcome = chatBox.querySelector('.welcome-message');
  if (welcome) welcome.remove();

  const div = document.createElement('div');
  div.className = `message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = role === 'user' ? '👤' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'message-content';
  // textContent instead of innerHTML — no XSS risk
  bubble.textContent = content;

  const time = document.createElement('p');
  time.className = 'message-time';
  time.textContent = getTime();
  bubble.appendChild(time);

  div.appendChild(avatar);
  div.appendChild(bubble);
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'message';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
  const typing = document.getElementById('typingIndicator');
  if (typing) typing.remove();
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const btn = document.getElementById('sendBtn');
  const content = input.value.trim();
  if (!content) return;

  input.value = '';
  btn.disabled = true;
  appendMessage('user', content);
  showTyping();

  try {
    const res = await AI.chat(content);
    removeTyping();
    appendMessage('assistant', res.reply);
  } catch (err) {
    removeTyping();
    const noCredits = document.getElementById('noCredits');
    if (noCredits) noCredits.style.display = 'block';
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function sendSuggestion(btn) {
  document.getElementById('chatInput').value = btn.textContent;
  sendMessage();
}

async function clearHistory() {
  if (!confirm('Limpar todo o histórico de conversa?')) return;
  await AI.clearHistory();
  chatBox.innerHTML = `
    <div class="welcome-message">
      <h3>👋 Olá! Sou o FinBot</h3>
      <p>Seu assistente financeiro pessoal. Posso analisar seus gastos, sugerir economias e te ajudar a planejar seu futuro financeiro.</p>
      <div class="suggestions">
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Como estão minhas finanças?</button>
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Onde posso economizar?</button>
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Me ajude a criar um orçamento</button>
        <button class="suggestion-btn" onclick="sendSuggestion(this)">Como quitar minhas dívidas?</button>
      </div>
    </div>`;
}

// Load previous history upon opening
async function loadHistory() {
  try {
    const history = await AI.getHistory();
    if (history && history.length > 0) {
      history.forEach(msg => appendMessage(msg.role, msg.content));
    }
  } catch (e) {
    // Silent failure — empty history is not critical
  }
}

loadHistory();
