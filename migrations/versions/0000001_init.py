from alembic import op

revision = "0000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE businesses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE business_owners (
            business_id UUID NOT NULL
                REFERENCES businesses(id) ON DELETE CASCADE,
            owner_id UUID NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            begin_at TIMESTAMPTZ NOT NULL DEFAULT now(),

            PRIMARY KEY (business_id, owner_id)
        );
    """)

    op.execute("""
        CREATE TABLE business_members (
            user_id UUID NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            business_id UUID NOT NULL
                REFERENCES businesses(id) ON DELETE CASCADE,
            begin_at TIMESTAMPTZ NOT NULL DEFAULT now(),

            PRIMARY KEY (user_id, business_id)
        );
    """)

    op.execute("""
        CREATE TABLE units (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            business_id UUID NOT NULL
                REFERENCES businesses(id) ON DELETE CASCADE
        );
    """)

    op.execute("""
        CREATE TABLE workstations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            unit_id UUID NOT NULL
                REFERENCES units(id) ON DELETE CASCADE
        );
    """)

    op.execute("""
        CREATE TYPE appointment_status AS ENUM (
            'pending',
            'cancelled',
            'successful'
        );
    """)

    op.execute("""
        CREATE TABLE appointments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            made_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            maker_id UUID NOT NULL REFERENCES users(id),
            workstation_id UUID NOT NULL
                REFERENCES workstations(id) ON DELETE CASCADE,
            period TSTZRANGE NOT NULL,
            status appointment_status NOT NULL DEFAULT 'pending',
            

            CONSTRAINT valid_period CHECK (
                NOT isempty(period)
                AND NOT lower_inf(period)
                AND NOT upper_inf(period)
                AND lower_inc(period)
                AND NOT upper_inc(period)
            ),
        CONSTRAINT no_overlapping_appointments
            EXCLUDE USING gist (
                workstation_id WITH =,
                period WITH &&
            )
            WHERE (status <> 'cancelled')
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE appointments;")
    op.execute("DROP TYPE appointment_status;")
    op.execute("DROP TABLE workstations;")
    op.execute("DROP TABLE units;")
    op.execute("DROP TABLE IF EXISTS business_members;")
    op.execute("DROP TABLE business_owners;")
    op.execute("DROP TABLE businesses;")
    op.execute("DROP TABLE users;")

    op.execute("DROP EXTENSION IF EXISTS btree_gist;")
