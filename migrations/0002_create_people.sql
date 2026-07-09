CREATE TABLE people (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    last_update TIMESTAMPTZ DEFAULT now() NOT NULL,
    status BOOLEAN NOT NULL DEFAULT TRUE
);
