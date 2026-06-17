# 💰 FinWise — Plataforma de Educação Financeira

![FinWise](https://img.shields.io/badge/FinWise-v1.0-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase)
![JavaScript](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-F7DF1E?style=for-the-badge&logo=javascript)

> Plataforma completa de gestão financeira pessoal com inteligência artificial, desenvolvida para ajudar brasileiros a organizarem suas finanças.

---

## 🚀 Funcionalidades

- **📊 Dashboard** — Resumo visual de receitas, despesas e saldo com gráficos.
- **💸 Transações** — Controle completo de receitas e despesas por categoria.
- **🎯 Metas financeiras** — Defina objetivos e acompanhe seu progresso.
- **💳 Gestão de dívidas** — Cadastre dívidas e simule tempo de quitação.
- **🤖 FinBot IA** — Assistente financeiro powered by Claude (Anthropic).
- **🔒 Autenticação segura** — JWT + Row Level Security no banco de dados.
- **📧 Redefinição de senha** — Fluxo completo via email.

---

## 🛠️ Tecnologias

### Backend
- **FastAPI** — Framework Python moderno e assíncrono.
- **Supabase** — PostgreSQL gerenciado com Auth e RLS.
- **Python-Jose** — Autenticação JWT.
- **Anthropic SDK** — Integração com Claude AI.
- **Pydantic** — Validação de dados.

### Frontend
- **HTML5 + CSS3 + JavaScript** — Puro, sem frameworks.
- **Chart.js** — Gráficos interativos.
- **Google Fonts (Inter)** — Tipografia.

### Infraestrutura
- **Supabase** — Banco de dados + Auth.
- **Row Level Security (RLS)** — Isolamento de dados por usuário.

---

## 📁 Estrutura do projeto

```
FinWise/
├── backend/
│   ├── app/
│   │   ├── main.py           # Entrada da aplicação
│   │   ├── config.py         # Variáveis de ambiente
│   │   ├── database.py       # Conexão Supabase
│   │   ├── dependencies.py   # Middleware de autenticação
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── transactions.py
│   │       ├── categories.py
│   │       ├── goals.py
│   │       ├── debts.py
│   │       └── ai_assistant.py
│   └── requirements.txt
│
└── frontend/
    ├── index.html            # Landing page
    ├── pages/
    │   ├── login.html
    │   ├── register.html
    │   ├── dashboard.html
    │   ├── transactions.html
    │   ├── goals.html
    │   ├── debts.html
    │   ├── ai-chat.html
    │   ├── forgot-password.html
    │   └── reset-password.html
    ├── css/
    │   ├── global.css
    │   └── dashboard.css
    └── js/
        ├── api.js
        ├── auth.js
        ├── dashboard.js
        ├── transactions.js
        ├── goals.js
        ├── debts.js
        └── ai-chat.js
```

---

## ⚙️ Como rodar localmente

### Pré-requisitos
- Python 3.10+
- Conta no [Supabase](https://supabase.com).
- Chave de API da [Anthropic](https://console.anthropic.com) (opcional para IA).

### 1. Clone o repositório
```bash
git clone https://github.com/felipe2008pg1/FinWise.git
cd FinWise
```

### 2. Configure o backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Crie o arquivo `.env` na pasta `backend`:
```env
SUPABASE_URL=sua_url_aqui
SUPABASE_ANON_KEY=sua_anon_key_aqui
SUPABASE_SERVICE_KEY=sua_service_key_aqui
JWT_SECRET=seu_jwt_secret_aqui
ANTHROPIC_API_KEY=sua_chave_aqui
```

### 3. Configure o banco de dados
Execute o SQL abaixo no **SQL Editor** do Supabase:

```sql
CREATE TABLE categories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  type TEXT CHECK (type IN ('income', 'expense')) NOT NULL,
  color TEXT DEFAULT '#6366f1',
  icon TEXT DEFAULT '💰',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  type TEXT CHECK (type IN ('income', 'expense')) NOT NULL,
  date DATE NOT NULL,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE goals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  target_amount NUMERIC(12,2) NOT NULL,
  current_amount NUMERIC(12,2) DEFAULT 0,
  deadline DATE,
  status TEXT CHECK (status IN ('active', 'completed', 'cancelled')) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE debts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  total_amount NUMERIC(12,2) NOT NULL,
  remaining_amount NUMERIC(12,2) NOT NULL,
  interest_rate NUMERIC(5,2) DEFAULT 0,
  monthly_payment NUMERIC(12,2),
  due_day INT CHECK (due_day BETWEEN 1 AND 31),
  status TEXT CHECK (status IN ('active', 'paid')) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role TEXT CHECK (role IN ('user', 'assistant')) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE debts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_categories" ON categories FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "users_own_transactions" ON transactions FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "users_own_goals" ON goals FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "users_own_debts" ON debts FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "users_own_ai_messages" ON ai_messages FOR ALL USING (auth.uid() = user_id);
```

### 4. Rode o backend
```bash
python -m uvicorn app.main:app --reload
```
API disponível em: `http://localhost:8000`
Documentação Swagger: `http://localhost:8000/docs`

### 5. Rode o frontend
```bash
cd ../frontend
python -m http.server 3000
```
Acesse: `http://localhost:3000`

---

## 🔐 Segurança

- Senhas armazenadas com hash bcrypt pelo Supabase Auth.
- Tokens JWT com expiração de 1 hora.
- Row Level Security — cada usuário acessa apenas seus próprios dados.
- Variáveis sensíveis em `.env` (nunca commitadas).

---

## 🗺️ Roadmap

- [ ] Deploy no Render (backend) + Vercel (frontend).
- [ ] Exportação de relatórios em PDF.
- [ ] Calculadoras de FGTS, férias e 13º salário.
- [ ] Alertas de gastos por categoria.
- [ ] App mobile (PWA).
- [ ] Configuração de SMTP para emails reais.

---

## 👨‍💻 Autor

**Felipe** — [GitHub](https://github.com/felipe2008pg1)

---

## 📄 Licença

MIT License — sinta-se livre para usar e modificar.
