"""Production-capable user, conversation, and authentication persistence."""
import json
import re
import hashlib
import secrets
from datetime import timedelta
from datetime import datetime, timezone
from functools import wraps

from flask import flash, redirect, request, session, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

class Base(DeclarativeBase): pass
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Conversation(db.Model):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False, default="New chat")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user: Mapped[User] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_conversation_user_updated", "user_id", "updated_at"),)

class Message(db.Model):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    used_at: Mapped[datetime | None] = mapped_column()

class GuestSession(db.Model):
    """Temporary server-side guest session storage with automatic TTL expiry."""
    __tablename__ = "guest_sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # guest_id
    message_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    data_json: Mapped[str | None] = mapped_column(Text, default="{}")

def init_auth(app):
    db.init_app(app)
    migrate.init_app(app, db)
    # Schema lifecycle is owned by Alembic in every environment. Calling
    # create_all here makes a fresh database look initialized while leaving
    # alembic_version unset, causing the first `flask db upgrade` to fail.

def create_user(name, email, password):
    name, email = name.strip(), email.strip().lower()
    if len(name) < 2 or len(name) > 100: return False, "Enter a name between 2 and 100 characters."
    if not EMAIL_RE.fullmatch(email): return False, "Enter a valid email address."
    if len(password) < 12: return False, "Use a password with at least 12 characters."
    if db.session.scalar(db.select(User).where(User.email == email)): return False, "An account already exists for that email address."
    db.session.add(User(name=name, email=email, password_hash=generate_password_hash(password))); db.session.commit()
    return True, ""

def authenticate(email, password):
    user = db.session.scalar(db.select(User).where(User.email == email.strip().lower()))
    return user if user and check_password_hash(user.password_hash, password) else None

def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if isinstance(user_id, int) else None

def get_owned_conversation(user, conversation_id):
    return db.session.scalar(db.select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id))

def create_reset_token(email):
    """Create a one-time token. Caller may send it, but never log it."""
    user = db.session.scalar(db.select(User).where(User.email == email.strip().lower()))
    if not user: return None
    raw = secrets.token_urlsafe(32)
    db.session.execute(db.delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None)))
    db.session.add(PasswordResetToken(user_id=user.id, token_hash=hashlib.sha256(raw.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)))
    db.session.commit()
    return raw

def reset_password(raw_token, password):
    if len(password) < 12: return False, "Use a password with at least 12 characters."
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    token = db.session.scalar(db.select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used_at.is_(None)))
    expiry = token.expires_at if token else None
    if expiry and expiry.tzinfo is None: expiry = expiry.replace(tzinfo=timezone.utc)
    if not token or expiry < datetime.now(timezone.utc): return False, "This reset link is invalid or expired."
    user = db.session.get(User, token.user_id)
    user.password_hash = generate_password_hash(password); token.used_at = datetime.now(timezone.utc)
    db.session.commit()
    return True, ""

def delete_user(user, password):
    if not check_password_hash(user.password_hash, password):
        return False
    db.session.delete(user)
    db.session.commit()
    return True

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("signin", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def get_or_create_guest_session(session_obj, ttl_days=7) -> GuestSession:
    """Retrieve or initialize a persistent server-side guest session backed by the shared database."""
    guest_id = session_obj.get("guest_id")
    now = datetime.now(timezone.utc)
    guest_sess = None
    if guest_id:
        guest_sess = db.session.get(GuestSession, guest_id)
        if guest_sess:
            exp = guest_sess.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < now:
                # Expired: clear out temporary data
                try:
                    db.session.delete(guest_sess)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                guest_sess = None

    if not guest_sess:
        guest_id = secrets.token_hex(20)
        session_obj["guest_id"] = guest_id
        session_obj["guest_message_count"] = 0
        session_obj.permanent = True
        guest_sess = GuestSession(
            id=guest_id,
            message_count=0,
            expires_at=now + timedelta(days=ttl_days),
            data_json=json.dumps({"conversations": {}, "active_session_id": ""}),
        )
        try:
            db.session.add(guest_sess)
            db.session.commit()
        except Exception:
            db.session.rollback()
            # Retry load in case of race condition
            guest_sess = db.session.get(GuestSession, guest_id)
    else:
        # Keep session cookie in sync with backend database
        session_obj["guest_message_count"] = guest_sess.message_count

    return guest_sess


def _guest_data(guest_sess: GuestSession) -> dict:
    """Read bounded guest metadata without allowing malformed old rows to fail chat."""
    try:
        data = json.loads(guest_sess.data_json or "{}")
    except (TypeError, json.JSONDecodeError):
        data = {}
    data.setdefault("conversations", {})
    data.setdefault("pending_requests", {})
    data.setdefault("completed_requests", {})
    return data


def reserve_guest_response(session_obj, request_key: str, limit: int = 3):
    """Atomically reserve one guest response without incrementing the quota.

    The row lock makes the limit safe across Gunicorn workers. A reservation is
    released when generation fails or is stopped; only a completed assistant
    response increments ``message_count``.
    """
    guest_sess = get_or_create_guest_session(session_obj)
    locked = db.session.execute(
        db.select(GuestSession).where(GuestSession.id == guest_sess.id).with_for_update()
    ).scalar_one()
    data = _guest_data(locked)
    completed = data["completed_requests"]
    pending = data["pending_requests"]

    if request_key in completed:
        return locked, "completed", completed[request_key]
    if request_key in pending:
        return locked, "in_progress", None
    if locked.message_count + len(pending) >= limit:
        return locked, "quota", None

    pending[request_key] = datetime.now(timezone.utc).isoformat()
    locked.data_json = json.dumps(data, ensure_ascii=False)
    db.session.commit()
    return locked, "reserved", None


def release_guest_response(guest_id: str, request_key: str) -> int:
    """Release a failed or stopped reservation and return completed count."""
    locked = db.session.execute(
        db.select(GuestSession).where(GuestSession.id == guest_id).with_for_update()
    ).scalar_one_or_none()
    if locked is None:
        return 0
    data = _guest_data(locked)
    if data["pending_requests"].pop(request_key, None) is not None:
        locked.data_json = json.dumps(data, ensure_ascii=False)
        db.session.commit()
    return locked.message_count


def complete_guest_response(guest_id: str, request_key: str, conversation: dict, result: dict) -> int:
    """Persist one completed temporary conversation and consume one trial slot."""
    locked = db.session.execute(
        db.select(GuestSession).where(GuestSession.id == guest_id).with_for_update()
    ).scalar_one()
    data = _guest_data(locked)
    pending = data["pending_requests"]
    completed = data["completed_requests"]
    if request_key not in completed:
        pending.pop(request_key, None)
        # The guest limit bounds this collection to three entries. Keep it
        # explicit to remain safe if the policy changes later.
        if len(completed) >= 12:
            oldest = next(iter(completed))
            completed.pop(oldest, None)
        completed[request_key] = {"result": result}
        convs = data["conversations"]
        existing = convs.get(conversation["session_id"])
        if existing:
            # A guest can keep asking in the same temporary conversation. Do
            # not replace its existing transcript when appending a turn.
            existing.setdefault("messages", []).extend(conversation.get("messages", []))
            existing["updated"] = conversation.get("updated", datetime.now(timezone.utc).timestamp())
            existing["lang"] = conversation.get("lang", existing.get("lang", "en"))
        else:
            convs[conversation["session_id"]] = conversation
        data["active_session_id"] = conversation["session_id"]
        locked.message_count += 1
    locked.data_json = json.dumps(data, ensure_ascii=False)
    db.session.commit()
    return locked.message_count


def migrate_guest_session_to_user(guest_id: str, user_id: int):
    """Seamlessly transfer temporary guest conversations to the authenticated user account upon sign-in/up."""
    if not guest_id or not user_id:
        return
    guest_sess = db.session.get(GuestSession, guest_id)
    if not guest_sess or not guest_sess.data_json:
        return
    try:
        data = json.loads(guest_sess.data_json)
        convs = data.get("conversations", {})
        for sid, cdata in convs.items():
            existing = db.session.scalar(
                db.select(Conversation).where(
                    Conversation.id == sid, Conversation.user_id == user_id
                )
            )
            if existing is None:
                new_conv = Conversation(
                    id=sid,
                    user_id=user_id,
                    title=cdata.get("title", "New chat")[:240],
                )
                db.session.add(new_conv)
                for msg in cdata.get("messages", []):
                    db.session.add(
                        Message(
                            conversation_id=sid,
                            role=msg.get("role", "user"),
                            content=msg.get("content", ""),
                            metadata_json=json.dumps({
                                "status": msg.get("status"),
                                "citations": msg.get("citations", []),
                            }),
                        )
                    )
        db.session.delete(guest_sess)
        db.session.commit()
    except Exception:
        db.session.rollback()
