CREATE EXTENSION IF NOT EXISTS btree_gist;


CREATE TABLE workstations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    name TEXT NOT NULL,
    description TEXT
);


CREATE TABLE workstation_holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workstation_id UUID NOT NULL
        REFERENCES workstations(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    description TEXT,
    holiday_range TSTZRANGE NOT NULL,

    CONSTRAINT no_overlapping_workstation_holidays
        EXCLUDE USING gist (
            workstation_id WITH =,
            holiday_range WITH &&
        ),

    CONSTRAINT valid_workstation_holiday_range
        CHECK (NOT isempty(holiday_range))
);


CREATE TABLE workstation_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workstation_id UUID NOT NULL
        REFERENCES workstations(id) ON DELETE CASCADE,

    status TEXT NOT NULL,
    exception_range TSTZRANGE NOT NULL,
    description TEXT,

    CONSTRAINT valid_workstation_exception_status
        CHECK (status IN ('available', 'unavailable')),

    CONSTRAINT no_overlapping_exceptions
        EXCLUDE USING gist (
            workstation_id WITH =,
            exception_range WITH &&
        ),

    CONSTRAINT valid_workstation_exception_range
        CHECK (NOT isempty(exception_range))
);


CREATE TABLE workstation_common_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workstation_id UUID NOT NULL
        REFERENCES workstations(id) ON DELETE CASCADE,

    status TEXT NOT NULL,
    hours_range TSTZRANGE NOT NULL,

    CONSTRAINT valid_workstation_common_hours_status
        CHECK (status IN ('available', 'unavailable')),

    CONSTRAINT no_overlapping_hours
        EXCLUDE USING gist (
            workstation_id WITH =,
            hours_range WITH &&
        ),

    CONSTRAINT valid_workstation_common_hours_range
        CHECK (NOT isempty(hours_range))
);


CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    workstation_id UUID NOT NULL
        REFERENCES workstations(id) ON DELETE CASCADE,

    person_id UUID NOT NULL
        REFERENCES people(id) ON DELETE CASCADE,

    schedule_range TSTZRANGE NOT NULL,

    status TEXT NOT NULL DEFAULT 'scheduled',

    active_schedule_range TSTZRANGE
        GENERATED ALWAYS AS (
            CASE
                WHEN status IN ('scheduled', 'completed')
                    THEN schedule_range
                ELSE NULL
            END
        ) STORED,

    CONSTRAINT valid_schedule_status
        CHECK (status IN ('scheduled', 'cancelled', 'completed')),

    CONSTRAINT valid_schedule_range
        CHECK (NOT isempty(schedule_range)),

    CONSTRAINT no_overlapping_schedules
        EXCLUDE USING gist (
            workstation_id WITH =,
            active_schedule_range WITH &&
        ),

    CONSTRAINT no_overlapping_same_person_schedules
        EXCLUDE USING gist (
            person_id WITH =,
            active_schedule_range WITH &&
        )
);