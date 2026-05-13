import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from openai import OpenAI
from functools import wraps

# ── Bootstrap ──────────────────────────────────────────────────────────────────
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-fallback-key")

_db_url = os.getenv("DATABASE_URL", "sqlite:///portfolio.db")
# Neon (and some platforms) provide postgres:// — SQLAlchemy needs postgresql+psycopg2://
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
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
    demo_url    = db.Column(db.String(300), default="")
    image       = db.Column(db.Text,        default="")

    def to_dict(self):
        return {
            "id":       self.id,
            "name":     self.name,
            "emoji":    self.emoji,
            "desc":     self.description,
            "tags":     [t.strip() for t in self.tags.split(",") if t.strip()],
            "url":      self.url,
            "demo_url": self.demo_url or "",
            "image":    self.image or "",
        }


class Certification(db.Model):
    __tablename__ = "certifications"
    id     = db.Column(db.Integer,     primary_key=True)
    name   = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(100), nullable=False)
    year   = db.Column(db.String(4),   nullable=False)
    icon   = db.Column(db.String(10),  default="🏅")
    image  = db.Column(db.Text,        default="")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "issuer": self.issuer,
                "year": self.year, "icon": self.icon, "image": self.image or ""}


class Skill(db.Model):
    __tablename__ = "skills"
    id       = db.Column(db.Integer,    primary_key=True)
    name     = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(20), default="other")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "cat": self.category}


class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    id         = db.Column(db.String(36), primary_key=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    flagged    = db.Column(db.Boolean, default=False)
    read       = db.Column(db.Boolean, default=False)
    messages   = db.relationship("ChatMessage", backref="session", lazy=True, order_by="ChatMessage.id")

    def to_dict(self):
        msgs = [m.to_dict() for m in self.messages]
        preview = (msgs[0]["content"][:80] + "…") if msgs else ""
        return {
            "id": self.id,
            "started_at": self.started_at.strftime("%b %d, %H:%M"),
            "flagged": self.flagged,
            "read": self.read,
            "preview": preview,
            "messages": msgs,
        }


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey("chat_sessions.id"), nullable=False)
    role       = db.Column(db.String(10), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"role": self.role, "content": self.content, "time": self.timestamp.strftime("%H:%M")}


INTERNSHIP_KEYWORDS = {"internship", "intern", "stage", "stagiaire", "تدريب", "تربص", "staj", "intership"}


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


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _portfolio_context_str():
    proj_text  = "\n".join(f"- {p.name} ({p.tags}): {p.description}" for p in Project.query.all())
    cert_text  = "\n".join(f"- {c.name} by {c.issuer} ({c.year})"    for c in Certification.query.all())
    skill_text = ", ".join(s.name for s in Skill.query.all())
    return f"""OWNER: Elaa Abidi
ROLE: First-year CS Engineering student at ESPRIM, Monastir, Tunisia
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
    session_id   = data.get("session_id", "")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Get or create chat session
    chat_sess = db.session.get(ChatSession, session_id) if session_id else None
    if not chat_sess:
        chat_sess = ChatSession(id=str(uuid.uuid4()))
        db.session.add(chat_sess)
        db.session.flush()

    db.session.add(ChatMessage(session_id=chat_sess.id, role="user", content=user_message))
    if any(kw in user_message.lower() for kw in INTERNSHIP_KEYWORDS):
        chat_sess.flagged = True
        chat_sess.read    = False

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
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Sorry, I couldn't reach the AI right now. ({str(e)[:80]})"

    db.session.add(ChatMessage(session_id=chat_sess.id, role="assistant", content=reply))
    db.session.commit()
    return jsonify({"reply": reply, "session_id": chat_sess.id})


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
                description=d["desc"], tags=",".join(d.get("tags",[])),
                url=d.get("url",""), demo_url=d.get("demo_url",""), image=d.get("image",""))
    db.session.add(p); db.session.commit()
    return jsonify(p.to_dict()), 201

@app.route("/api/projects/<int:pid>", methods=["PUT"])
@_require_admin
def update_project(pid):
    p = db.session.get(Project, pid)
    if not p: return jsonify({"error": "Not found"}), 404
    d = request.get_json(force=True)
    if "name"     in d: p.name        = d["name"]
    if "emoji"    in d: p.emoji       = d["emoji"]
    if "desc"     in d: p.description = d["desc"]
    if "tags"     in d: p.tags        = ",".join(d["tags"]) if isinstance(d["tags"], list) else d["tags"]
    if "url"      in d: p.url         = d["url"]
    if "demo_url" in d: p.demo_url    = d["demo_url"]
    if "image"    in d: p.image       = d["image"]
    db.session.commit()
    return jsonify(p.to_dict())

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
    c = Certification(name=d["name"], issuer=d["issuer"], year=d["year"], icon=d.get("icon","🏅"), image=d.get("image",""))
    db.session.add(c); db.session.commit()
    return jsonify(c.to_dict()), 201

@app.route("/api/certifications/<int:cid>", methods=["PUT"])
@_require_admin
def update_cert(cid):
    c = db.session.get(Certification, cid)
    if not c: return jsonify({"error": "Not found"}), 404
    d = request.get_json(force=True)
    if "name"   in d: c.name   = d["name"]
    if "issuer" in d: c.issuer = d["issuer"]
    if "year"   in d: c.year   = d["year"]
    if "icon"   in d: c.icon   = d["icon"]
    if "image"  in d: c.image  = d["image"]
    db.session.commit()
    return jsonify(c.to_dict())

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

@app.route("/api/skills/<int:sid>", methods=["PUT"])
@_require_admin
def update_skill(sid):
    s = db.session.get(Skill, sid)
    if not s: return jsonify({"error": "Not found"}), 404
    d = request.get_json(force=True)
    if "name" in d: s.name     = d["name"]
    if "cat"  in d: s.category = d["cat"]
    db.session.commit()
    return jsonify(s.to_dict())

@app.route("/api/skills/<int:sid>", methods=["DELETE"])
@_require_admin
def delete_skill(sid):
    s = db.session.get(Skill, sid)
    if not s: return jsonify({"error": "Not found"}), 404
    db.session.delete(s); db.session.commit()
    return jsonify({"ok": True})


# ══════════════════════════════════════════════════════════════════════════════
# CONTROLLER — Conversations (admin)
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/admin/conversations")
@_require_admin
def get_conversations():
    convos = ChatSession.query.order_by(ChatSession.started_at.desc()).all()
    return jsonify([c.to_dict() for c in convos])

@app.route("/api/admin/conversations/unread")
@app.route("/api/admin/notifications")
@_require_admin
def unread_count():
    count = ChatSession.query.filter_by(flagged=True, read=False).count()
    return jsonify({"count": count})

@app.route("/api/admin/conversations/<sid>/read", methods=["POST"])
@_require_admin
def mark_read(sid):
    c = db.session.get(ChatSession, sid)
    if not c: return jsonify({"error": "Not found"}), 404
    c.read = True
    db.session.commit()
    return jsonify({"ok": True})


# ══════════════════════════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════════════════════════

def _migrate():
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        with db.engine.connect() as conn:
            if "projects" in tables:
                cols = {c["name"] for c in inspector.get_columns("projects")}
                if "image"    not in cols: conn.execute(text("ALTER TABLE projects ADD COLUMN image TEXT DEFAULT ''"))
                if "demo_url" not in cols: conn.execute(text("ALTER TABLE projects ADD COLUMN demo_url VARCHAR(300) DEFAULT ''"))
            if "certifications" in tables:
                cols = {c["name"] for c in inspector.get_columns("certifications")}
                if "image" not in cols: conn.execute(text("ALTER TABLE certifications ADD COLUMN image TEXT DEFAULT ''"))
            conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")

with app.app_context():
    _migrate()
    db.create_all()
    _seed()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development")