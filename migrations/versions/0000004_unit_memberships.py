from alembic import op

revision = "0000004"
down_revision = "0000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS unit_members (
            user_id UUID NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            unit_id UUID NOT NULL
                REFERENCES units(id) ON DELETE CASCADE,
            begin_at TIMESTAMPTZ NOT NULL DEFAULT now(),

            PRIMARY KEY (user_id, unit_id)
        );
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS unit_owners (
            user_id UUID NOT NULL,
            unit_id UUID NOT NULL
                REFERENCES units(id) ON DELETE CASCADE,
            begin_at TIMESTAMPTZ NOT NULL DEFAULT now(),

            PRIMARY KEY (user_id, unit_id),
            FOREIGN KEY (user_id, unit_id)
                REFERENCES unit_members(user_id, unit_id) ON DELETE CASCADE
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS unit_owners;")
    op.execute("DROP TABLE IF EXISTS unit_members;")
