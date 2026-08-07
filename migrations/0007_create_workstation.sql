CREATE TABLE workstations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    name TEXT NOT NULL,
    description TEXT
);

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

CREATE TABLE workstation_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workstation_id UUID REFERENCES workstation(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    CHECK (status IN 'available', 'unavailable'),
    exception_range TSTZRANGE NOT NULL,
    description TEXT DEFAULT NULL,

    CONSTRAINT no_overlapping_exceptions 
    EXCLUDE USING gist (
        (workstation_id) WITH =,
        (exception_range) WITH &&
    ),

    CHECK (NOT isempty(exception_range))
);

CREATE TABLE workstation_common_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workstation_id UUID REFERENCES workstation(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    CHECK (status IN ('available', 'unavailable')),
    hours_range TSTZRANGE NOT NULL,

    CONSTRAINT no_overlapping_hours
    EXCLUDE USING gist (
        (workstation_id) WITH =,
        (hours_range) WITH &&
    ),

    CHECK (NOT isempty(hours_range))
);

CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workstation_id UUID REFERENCES workstations(id) ON DELETE CASCADE NOT NULL,
    person_id UUID REFERENCES people(id) ON DELETE CASCADE NOT NULL,
    schedule_range TSTZRANGE NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled',
    CHECK (status IN ('scheduled', 'cancelled', 'completed')),

    CONSTRAINT no_overlapping_schedules
    EXCLUDE USING gist (
        (workstation_id) with =,
        (schedule_range) WITH &&
    ) WHERE status = IN ('scheduled', 'completed'),
    CONSTRAINT no_overlapping_same_person_schedules 
    EXCLUDE USING gist (
        (person_id) WITH =,
        (schedule_range) WITH &&
    ) WHERE status = ('scheduled', 'completed'),
    CHECK (NOT isempty(schedule_range))
);