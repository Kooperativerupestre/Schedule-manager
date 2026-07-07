CREATE TABLE units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    phone_number TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);