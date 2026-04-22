# 🌸 Elaa Abidi — Portfolio

A diary-aesthetic portfolio with AI chat integration, Flask MVC backend, and SQLite/MySQL database.

## ✦ Features

- **Diary aesthetic** — ruled-paper UI with your pink/blush/sky palette
- **AI Chat bubble** — powered by NVIDIA LLaMA, answers questions about you
- **Admin panel** — password-protected; add/delete projects, certs, and skills live
- **MVC architecture** — clean separation via Flask + SQLAlchemy + Jinja2
- **SQLite locally, MySQL in production**

---

## 🚀 Local Setup (XAMPP or Laragon optional)

### 1. Clone & enter project
```bash
git clone https://github.com/YOUR_USERNAME/portfolio.git
cd portfolio
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# then edit .env and fill in your NVIDIA_API_KEY and other values
```

### 5. Run the app
```bash
python app.py
# → http://127.0.0.1:5000
```

> The SQLite database is created automatically at `instance/portfolio.db` on first run with seed data.

---

## 🌐 Deploy to Railway (recommended free option)

1. Push your repo to GitHub (`.env` is in `.gitignore` — safe)
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variables in Railway's dashboard (same keys as `.env.example`)
4. Railway auto-detects Flask and deploys. Done.

---

## 🔑 Admin Panel

Click **✦ Admin** in the nav and enter your password (set in `.env`).

---

## 🤖 AI Chat

The chat bubble uses your NVIDIA API key to answer recruiter questions about your portfolio in **English, French, or Arabic**. It reads live data from your database for every response — no hardcoding needed.

Get your free NVIDIA API key at: https://build.nvidia.com

---

## 📁 Project Structure

```
portfolio/
├── app.py                  # Flask app — Model + Controller
├── templates/
│   └── index.html          # Jinja2 View
├── instance/
│   └── portfolio.db        # SQLite DB (auto-created, git-ignored)
├── requirements.txt
├── .env                    # Secret values (git-ignored)
├── .env.example            # Template to share
└── .gitignore
```

---

## 🛠 Switching to MySQL (production)

1. Change `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=mysql+pymysql://user:password@localhost/portfolio_db
   ```
2. Import `portfolio_db.sql` into your MySQL server
3. That's it — SQLAlchemy handles the rest
