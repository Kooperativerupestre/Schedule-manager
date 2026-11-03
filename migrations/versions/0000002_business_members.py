from alembic import op

revision = "0000002"
down_revision = "0000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS business_members (
            user_id UUID NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            business_id UUID NOT NULL
                REFERENCES businesses(id) ON DELETE CASCADE,
            begin_at TIMESTAMPTZ NOT NULL DEFAULT now(),

            PRIMARY KEY (user_id, business_id)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS business_members;")
