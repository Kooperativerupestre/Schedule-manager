CREATE TABLE unit_holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    holiday_range DATERANGE NOT NULL,

    CONSTRAINT no_overlapping_unit_holidays
    EXCLUDE USING gist (
    (unit_id) WITH =,
    (holiday_range) WITH &&
)
);

