# 💰 FinWise — Plataform for Finance Education

![FinWise](https://img.shields.io/badge/FinWise-v1.1-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase)
![JavaScript](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-F7DF1E?style=for-the-badge&logo=javascript)

> A comprehensive personal financial management platform powered by artificial intelligence, developed to help Brazilians organize their finances.
---

## 🚀 Features

- **📊 Dashboard** — Visual summary of income, expenses, and balance with charts.
- **💸 Transactions** — Complete control over income and expenses by category.
- **🏷️ Categories** — Create, edit, and organize custom income/expense categories.
- **🎯 Financial Goals** — Set goals and track your progress.
- **💳 Debt Management** — Register your debts and simulate repayment times.
- **🤖 FinBot IA** — Finance Assistent powered by Claude (Anthropic).
- **🔒 Secure Authentication** — JWT + Row Level Security in database.
- **📧 Password Reset** — Complete flow via email.

---

## 🛠️ Technologies

### Backend
- **FastAPI** — Modern and asynchronous Python framework.
- **Supabase** — PostgreSQL maneged with Auth e RLS.
- **Python-Jose** — Autentication JWT.
- **Anthropic SDK** — Integration with Claude AI.
- **Pydantic** — Data validation.

### Frontend
- **HTML5 + CSS3 + JavaScript** — Pure.not frameworks.
- **Chart.js** — Interactive graphics.
- **Google Fonts (Inter)** — Typography.

### Infraestrure
- **Supabase** — Database + Auth.
- **Row Level Security (RLS)** — User-based data isolation.

---

## 📁 Project Estruture

```
FinWise/
├── backend/
│   ├── app/
│   │   ├── main.py           # Application entry
│   │   ├── config.py         # Environment variables
│   │   ├── database.py       # Conection Supabase
│   │   ├── dependencies.py   # Middleware for autentication
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
    │   ├── categories.html
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
        ├── categories.js
        ├── goals.js
        ├── debts.js
        └── ai-chat.js
```

---

## ⚙️ How to run locally

### Prerequisites
- Python 3.10+
- Account in [Supabase](https://supabase.com).
- Key API by [Anthropic](https://console.anthropic.com) (opcional for IA).

### 1. Clone the repository
```bash
git clone https://github.com/felipe2008pg1/FinWise.git
cd FinWise
```

### 2. Config the Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create the file `.env` in folder `backend`:
```env
SUPABASE_URL=your_url_here
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here
JWT_SECRET=your_jwt_secret_here
ANTHROPIC_API_KEY=your_key_here
```

### 3. Config the database
Execute the SQL below in the Supabase **SQL Editor**:

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

### 4. Run the backend
```bash
python -m uvicorn app.main:app --reload
```
API available in: `http://localhost:8000` | 
Documentation Swagger: `http://localhost:8000/docs`

### 5. Run the frontend
```bash
cd ../frontend
python -m http.server 3000
```
Open: `http://localhost:3000`

---

## 🔐 Security

- Passwords stored with bcrypt hash by Supabase Auth.
- Tokens JWT with expiration for 1 hour.
- Row Level Security — Each user only accesses their own data.
- Sensitive variables in `.env` (Never committed).

---

## 🗺️ Roadmap

- [ ] Deploy in Render (backend) + Vercel (frontend).
- [ ] Exportation for relatories in PDF.
- [ ] Calculators with FGTS, vacations e 13º wage.
- [ ] Spending alerts by category.
- [ ] App mobile (PWA).
- [ ] Configuration with SMTP for really emails.

---

## 👨‍💻 Owner

**Felipe** — [GitHub](https://github.com/felipe2008pg1)

## ⚠️ Warning

The exhibition of frontend are in Portuguese because is a system created for Brazilians, but the all documentation are written in English.

---

## 📄 Licence

MIT License — Feel free to use and modify..
