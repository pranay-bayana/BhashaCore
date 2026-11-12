"""add temporary server-side guest sessions

Revision ID: 7a4f4fe9e7d2
Revises: 2636fcb607c4
Create Date: 2026-11-03

Guest rows contain only temporary, expiry-bound chat state. They are separate
from authenticated conversations and are deleted when a guest converts or
expires.
"""

from alembic import op
import sqlalchemy as sa


revision = "7a4f4fe9e7d2"
down_revision = "2636fcb607c4"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "guest_sessions" not in inspector.get_table_names():
        op.create_table(
            "guest_sessions",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("data_json", sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        inspector = sa.inspect(bind)
    if not any(index["name"] == "ix_guest_sessions_expires_at"
               for index in inspector.get_indexes("guest_sessions")):
        op.create_index("ix_guest_sessions_expires_at", "guest_sessions", ["expires_at"], unique=False)


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if "guest_sessions" in inspector.get_table_names():
        if any(index["name"] == "ix_guest_sessions_expires_at"
               for index in inspector.get_indexes("guest_sessions")):
            op.drop_index("ix_guest_sessions_expires_at", table_name="guest_sessions")
        op.drop_table("guest_sessions")
