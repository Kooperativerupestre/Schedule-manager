from alembic import op

revision = "0000005"
down_revision = "0000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE workers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            workstation_id UUID NOT NULL
                REFERENCES workstations(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

            UNIQUE (user_id, workstation_id)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS workers;")
