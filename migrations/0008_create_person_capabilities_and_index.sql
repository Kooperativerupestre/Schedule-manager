CREATE TABLE person_capabilities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    person_id UUID REFERENCES people(id) ON DELETE CASCADE NOT NULL,
    capability_id INTEGER REFERENCES capabilities(id) ON DELETE CASCADE NOT NULL,

    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE DEFAULT NULL,
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE DEFAULT NULL,
    workstation_id UUID REFERENCES workstations(id) ON DELETE CASCADE DEFAULT NULL,

    validity_range TSTZRANGE NOT NULL DEFAULT tstzrange(now(), NULL, '[)'),

    CONSTRAINT check_single_target CHECK (
        num_nonnulls(business_id, unit_id, workstation_id) = 1
    ),

    CONSTRAINT no_overlapping_business_capability
    EXCLUDE USING gist (
        person_id WITH =,
        capability_id WITH =,
        business_id WITH =,
        validity_range WITH &&) WHERE (business_id IS NOT NULL),
    
    CONSTRAINT no_overlapping_unit_capability
    EXCLUDE USING gist (
        person_id WITH =,
        capability_id WITH =,
        unit_id WITH =,
        validity_range WITH &&
    ) WHERE (unit_id IS NOT NULL),

    CONSTRAINT no_overlapping_workstation_capability
    EXCLUDE USING gist (
        person_id WITH =,
        capability_id WITH =,
        workstation_id WITH =,
        validity_range WITH &&
    ) WHERE (workstation_id IS NOT NULL)
);

CREATE TABLE admins (
    id UUID REFERENCES people(id) ON DELETE CASCADE PRIMARY KEY
);

