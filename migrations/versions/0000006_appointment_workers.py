from alembic import op

revision = "0000006"
down_revision = "0000005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM appointments) THEN
                RAISE EXCEPTION
                    'Cannot add appointment worker assignment: appointments '
                    'must be empty before this migration.';
            END IF;
        END;
        $$;
    """)
    op.execute("""
        ALTER TABLE workers
        ADD CONSTRAINT workers_id_workstation_id_key
        UNIQUE (id, workstation_id);
    """)
    op.execute("""
        ALTER TABLE appointments
        ADD COLUMN worker_id UUID;
    """)
    op.execute("""
        ALTER TABLE appointments
        ADD CONSTRAINT appointment_worker_workstation_fkey
        FOREIGN KEY (worker_id, workstation_id)
        REFERENCES workers (id, workstation_id)
        ON DELETE SET NULL (worker_id);
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE appointments
        DROP CONSTRAINT appointment_worker_workstation_fkey;
    """)
    op.execute("""
        ALTER TABLE appointments
        DROP COLUMN worker_id;
    """)
    op.execute("""
        ALTER TABLE workers
        DROP CONSTRAINT workers_id_workstation_id_key;
    """)
