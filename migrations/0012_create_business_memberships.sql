CREATE TABLE business_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE NOT NULL,
    person_id UUID REFERENCES people(id) ON DELETE CASCADE NOT NULL,
    validity_range TSTZRANGE NOT NULL DEFAULT tstzrange(now(), NULL, '[)'),

    CONSTRAINT no_overlapping_active_memberships
    EXCLUDE USING GIST (
        business_id WITH =,
        person_id WITH =,
        validity_range WITH &&
    )
);


CREATE TABLE business_membership_invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE NOT NULL,
    validity_range TSTZRANGE NOT NULL DEFAULT tstzrange(now(), NULL, '[)'),
    expires_at TIMESTAMPTZ NOT NULL,
    email TEXT NOT NULL,


    CONSTRAINT no_overlapping_active_invites
    EXCLUDE USING GIST (
        business_id WITH =,
        email WITH =,
        validity_range WITH &&
    )
);

