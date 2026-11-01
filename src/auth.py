"""Production-capable user, conversation, and authentication persistence."""
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

def init_auth(app):
    db.init_app(app); migrate.init_app(app, db)

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
