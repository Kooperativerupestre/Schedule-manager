CREATE TABLE authentication (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID REFERENCES people(id) ON DELETE CASCADE NOT NULL,
    provider TEXT NOT NULL,
    credentials JSONB NOT NULL,
    UNIQUE (person_id, provider)
);