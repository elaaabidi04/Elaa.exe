import pymysql
import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from openai import OpenAI
from functools import wraps

# ── Bootstrap ──────────────────────────────────────────────────────────────────
load_dotenv()
print("MODEL:", os.getenv("NVIDIA_MODEL"))
print("KEY:", os.getenv("NVIDIA_API_KEY", "")[:10])  # only prints first 10 chars
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-fallback-key")

_db_url = os.getenv("DATABASE_URL", "sqlite:///portfolio.db")
# Railway provides mysql:// — SQLAlchemy needs mysql+pymysql://
if _db_url.startswith("mysql://"):
    _db_url = _db_url.replace("mysql://", "mysql+pymysql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"]        = _db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ── NVIDIA / OpenAI-compatible client ─────────────────────────────────────────
nvidia_client = OpenAI(
    api_key  = os.getenv("NVIDIA_API_KEY", ""),
    base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
)
NVIDIA_MODEL   = os.getenv("NVIDIA_MODEL", "meta/llama-4-scout-17b-16e-instruct")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
import pymysql

# ══════════════════════════════════════════════════════════════════════════════
# MODEL
# ══════════════════════════════════════════════════════════════════════════════

class Project(db.Model):
    __tablename__ = "projects"
    id          = db.Column(db.Integer,     primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    emoji       = db.Column(db.String(10),  default="✦")
    description = db.Column(db.Text,        nullable=False)
    tags        = db.Column(db.String(300), default="")
    url         = db.Column(db.String(300), default="")

    def to_dict(self):
        return {
            "id":    self.id,
            "name":  self.name,
            "emoji": self.emoji,
            "desc":  self.description,
            "tags":  [t.strip() for t in self.tags.split(",") if t.strip()],
            "url":   self.url,
        }


class Certification(db.Model):
    __tablename__ = "certifications"
    id     = db.Column(db.Integer,     primary_key=True)
    name   = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(100), nullable=False)
    year   = db.Column(db.String(4),   nullable=False)
    icon   = db.Column(db.String(10),  default="🏅")

    def to_dict(self):
        return {"id": self.id, "name": self.name,
                "issuer": self.issuer, "year": self.year, "icon": self.icon}


class Skill(db.Model):
    __tablename__ = "skills"
    id       = db.Column(db.Integer,    primary_key=True)
    name     = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(20), default="other")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "cat": self.category}


# ── Seed default data ──────────────────────────────────────────────────────────
def _seed():
    if Project.query.count() > 0:
        return
    for name, emoji, desc, tags, url in [
        ("Wellness",        "🌿", "Full-stack web app for cancer patient excursion management using MVC architecture.",                               "HTML,CSS,JS,PHP,MySQL,MVC",             ""),
        ("Vaxera",          "💉", "Qt/C++ desktop app for vaccination centers with Arduino temperature monitoring and keypad access control.",         "C++,Qt,Arduino,Hardware",               ""),
        ("SmartHeal",       "🏥", "Java desktop app + Symfony website for medical tourism, covering the full medical services module.",                "Java,Symfony,MySQL,MVC",                ""),
        ("Elmo AI Chatbot", "🤖", "Context-aware chatbot with conversation memory using SQLite. Full-stack AI integration with multi-turn dialogue.", "Python,Flask,SQLite,NVIDIA API",        "https://github.com/elaaabidi04/Elmo"),
        ("Biblio-AI",       "🎬", "AI-powered movie & book recommender using NVIDIA LLaMA 4, TMDB and Open Library. Deployed on Render/Aiven.",      "Flask,MySQL,NVIDIA LLaMA 4,TMDB,Render","https://github.com/elaaabidi04/biblio-ai"),
    ]:
        db.session.add(Project(name=name, emoji=emoji, description=desc, tags=tags, url=url))

    for name, issuer, year, icon in [
        ("Machine Learning Certificate", "NVIDIA",     "2026", "🏅"),
        ("Generative AI Certification",  "Go My Code", "2026", "✨"),
    ]:
        db.session.add(Certification(name=name, issuer=issuer, year=year, icon=icon))

    for name, cat in [
        ("HTML","language"),("CSS","language"),("JavaScript","language"),
        ("Python","language"),("PHP","language"),("Java","language"),
        ("C++","language"),("C","language"),("SQL","language"),
        ("Laravel","framework"),("Symfony","framework"),("Flask","framework"),("Qt","framework"),
        ("Make","tool"),("XAMPP","tool"),("Arduino","tool"),
    ]:
        db.session.add(Skill(name=name, category=cat))

    db.session.commit()

def _ensure_db_exists():
    url = os.getenv("DATABASE_URL", "")
    # Only needed for MySQL connections
    if "mysql" not in url:
        return
    try:
        # Parse credentials from the DATABASE_URL
        # Format: mysql+pymysql://user:pass@host/dbname
        from urllib.parse import urlparse
        parsed = urlparse(url)
        conn = pymysql.connect(
            host=parsed.hostname,
            user=parsed.username,
            password=parsed.password or "",
            port=parsed.port or 3306,
        )
        db_name = parsed.path.lstrip("/")
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()
        print(f"✔ Database '{db_name}' ready.")
    except Exception as e:
        print(f"⚠ Could not auto-create database: {e}")

_ensure_db_exists()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _portfolio_context_str():
    proj_text  = "\n".join(f"- {p.name} ({p.tags}): {p.description}" for p in Project.query.all())
    cert_text  = "\n".join(f"- {c.name} by {c.issuer} ({c.year})"    for c in Certification.query.all())
    skill_text = ", ".join(s.name for s in Skill.query.all())
    return f"""OWNER: Elaa Abidi
ROLE: First-year CS Engineering student at ESPRIM, Tunis, Tunisia
LOOKING FOR: Internship in full-stack / AI development

PROJECTS:
{proj_text}

CERTIFICATIONS:
{cert_text}

SKILLS: {skill_text}

LANGUAGES SPOKEN: Arabic, English, French
INTERESTS: Full-stack web dev, AI/ML integration, hardware+software projects""".strip()


def _require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)
    return wrapper


# ══════════════════════════════════════════════════════════════════════════════
# CONTROLLER — Public routes
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html",
        projects = [p.to_dict() for p in Project.query.all()],
        certs    = [c.to_dict() for c in Certification.query.all()],
        skills   = [s.to_dict() for s in Skill.query.all()],
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    data         = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    history      = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    system_prompt = f"""You are an AI assistant embedded in Elaa's portfolio website.
Your ONLY job is to answer questions about Elaa — her projects, skills, experience, and background.
Be warm, concise, and confident. Speak in first person on her behalf when appropriate.
If asked something totally unrelated to Elaa or her work, politely redirect.
Always respond in the same language the visitor uses (English, French, or Arabic).

Here is Elaa's portfolio data:
{_portfolio_context_str()}
"""
    messages = [{"role": "system", "content": system_prompt}]
    for turn in history[-10:]:
        if turn.get("role") in ("user", "assistant"):
            messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        response = nvidia_client.chat.completions.create(
            model=NVIDIA_MODEL, messages=messages, max_tokens=400, temperature=0.7,
        )
        return jsonify({"reply": response.choices[0].message.content.strip()})
    except Exception as e:
        return jsonify({"reply": f"Sorry, I couldn't reach the AI right now. ({str(e)[:80]})"}), 200


# ══════════════════════════════════════════════════════════════════════════════
# CONTROLLER — Admin auth
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    pw = (request.get_json(force=True) or {}).get("password", "")
    if pw == ADMIN_PASSWORD:
        session["admin"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Wrong password"}), 401


@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin", None)
    return jsonify({"ok": True})


# ══════════════════════════════════════════════════════════════════════════════
# CONTROLLER — Admin CRUD
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/projects", methods=["GET"])
def get_projects():
    return jsonify([p.to_dict() for p in Project.query.all()])

@app.route("/api/projects", methods=["POST"])
@_require_admin
def add_project():
    d = request.get_json(force=True)
    p = Project(name=d["name"], emoji=d.get("emoji","✦"),
                description=d["desc"], tags=",".join(d.get("tags",[])), url=d.get("url",""))
    db.session.add(p); db.session.commit()
    return jsonify(p.to_dict()), 201

@app.route("/api/projects/<int:pid>", methods=["DELETE"])
@_require_admin
def delete_project(pid):
    p = db.session.get(Project, pid)
    if not p: return jsonify({"error": "Not found"}), 404
    db.session.delete(p); db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/certifications", methods=["GET"])
def get_certs():
    return jsonify([c.to_dict() for c in Certification.query.all()])

@app.route("/api/certifications", methods=["POST"])
@_require_admin
def add_cert():
    d = request.get_json(force=True)
    c = Certification(name=d["name"], issuer=d["issuer"], year=d["year"], icon=d.get("icon","🏅"))
    db.session.add(c); db.session.commit()
    return jsonify(c.to_dict()), 201

@app.route("/api/certifications/<int:cid>", methods=["DELETE"])
@_require_admin
def delete_cert(cid):
    c = db.session.get(Certification, cid)
    if not c: return jsonify({"error": "Not found"}), 404
    db.session.delete(c); db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/skills", methods=["GET"])
def get_skills():
    return jsonify([s.to_dict() for s in Skill.query.all()])

@app.route("/api/skills", methods=["POST"])
@_require_admin
def add_skill():
    d = request.get_json(force=True)
    s = Skill(name=d["name"], category=d.get("cat","other"))
    db.session.add(s); db.session.commit()
    return jsonify(s.to_dict()), 201

@app.route("/api/skills/<int:sid>", methods=["DELETE"])
@_require_admin
def delete_skill(sid):
    s = db.session.get(Skill, sid)
    if not s: return jsonify({"error": "Not found"}), 404
    db.session.delete(s); db.session.commit()
    return jsonify({"ok": True})


# ══════════════════════════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════════════════════════

with app.app_context():
    _ensure_db_exists()
    db.create_all()
    _seed()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development")