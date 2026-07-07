CREATE TABLE business_owners (
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE NOT NULL,
    person_id UUID REFERENCES people(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL DEFAULT 'owner',
    begin_date TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY(business_id, person_id)
);
