# Elaa Abidi — Portfolio

A diary-aesthetic developer portfolio with an AI chat assistant, Flask MVC backend, and PostgreSQL database. Built to showcase projects, skills, and experience — and let recruiters ask questions directly to an AI that knows everything about me.

**Live:** [elaa-exe.onrender.com](https://elaa-exe.onrender.com)

---

## Features

- **Diary aesthetic UI** — ruled-paper layout with a pink/blush/lavender palette
- **AI Chat assistant** — powered by NVIDIA LLaMA 4, answers questions in English, French, or Arabic
- **Recruiter Inbox** — every chat conversation is saved; internship mentions are flagged and trigger a notification badge on the admin button
- **Full CRUD admin panel** — add, edit, and delete projects, certifications, and skills live without touching code
- **Image upload** — projects support cover images and demo links; certifications support proof images viewable in a modal
- **MVC architecture** — Flask + SQLAlchemy + Jinja2
- **PostgreSQL on Neon** — serverless database, auto-migrated and seeded on first boot

---

## Tech Stack

`Python` `Flask` `SQLAlchemy` `PostgreSQL` `Jinja2` `NVIDIA LLaMA 4` `Render` `Neon` `HTML/CSS` `JavaScript`

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/elaaabidi04/Elaa.exe.git
cd Elaa.exe
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Fill in NVIDIA_API_KEY, SECRET_KEY, and ADMIN_PASSWORD
```

### 5. Run
```bash
python app.py
# → http://127.0.0.1:5000
```

> SQLite is used locally by default — tables, migrations, and seed data run automatically on first boot.

---

## Deployment (Render + Neon)

1. Create a PostgreSQL database on [neon.tech](https://neon.tech) and copy the connection string
2. Create a **Web Service** on [render.com](https://render.com) connected to this repo
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
3. Set environment variables on Render:

```
DATABASE_URL=<Neon connection string>
SECRET_KEY=<long random string>
ADMIN_PASSWORD=<your password>
NVIDIA_API_KEY=<your key>
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-4-scout-17b-16e-instruct
```

Tables, migrations, and seed data run automatically on first boot.

---

## Admin Panel

Click **✦ Admin** in the nav → enter your password → manage content live.

- A red dot appears on the Admin button when a recruiter mentions internship in the chat
- Open the **Inbox** tab to read conversations and mark them as read

---

## AI Chat

The floating chat bubble lets anyone ask about my projects, skills, and background. It reads live data from the database and replies in the visitor's language (English, French, or Arabic).

Get a free NVIDIA API key at [build.nvidia.com](https://build.nvidia.com).

---

## Project Structure

```
portfolio/
├── app.py                  # Flask app — models, routes, AI chat, migrations
├── templates/
│   └── index.html          # Jinja2 template — full frontend
├── static/
│   └── logo.png            # Site icon
├── Procfile                # Render start command
├── requirements.txt
├── .env.example
└── .gitignore
```
