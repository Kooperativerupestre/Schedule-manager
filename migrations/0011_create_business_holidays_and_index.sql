CREATE TABLE business_holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    holiday_range DATERANGE NOT NULL,
    
    CONSTRAINT no_overlapping_business_holidays
    EXCLUDE USING gist (
    (business_id) WITH =,
    (holiday_range) WITH &&
    )
);
