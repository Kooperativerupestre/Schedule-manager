CREATE TABLE person_capabilities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    person_id UUID REFERENCES people(id) ON DELETE CASCADE NOT NULL,
    capability_id INTEGER REFERENCES capabilities(id) ON DELETE CASCADE NOT NULL,

    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    workstation_id UUID REFERENCES workstations(id) ON DELETE CASCADE,

    begin_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    end_at TIMESTAMPTZ DEFAULT NULL,

    CONSTRAINT check_single_target CHECK (
        num_nonnulls(business_id, unit_id, workstation_id) = 1
    )
);

CREATE INDEX idx_capabilities_business ON person_capabilities (person_id, business_id)
WHERE business_id IS NOT NULL;

CREATE INDEX idx_capabilities_unit ON person_capabilities (person_id, unit_id)
WHERE unit_id IS NOT NULL;

CREATE INDEX idx_capabilities_workstation ON person_capabilities (person_id, workstation_id)
WHERE workstation_id IS NOT NULL;
