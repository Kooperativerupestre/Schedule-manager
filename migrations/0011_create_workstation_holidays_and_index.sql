CREATE TABLE workstation_holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workstation_id UUID REFERENCES workstations(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    holiday_range TSTZRANGE NOT NULL,

    CONSTRAINT no_overlapping_workstation_holidays
    EXCLUDE USING gist (
    (workstation_id) WITH =,
    (holiday_range) WITH &&
    ),
    CHECK (NOT isempty(holiday_range))
);
