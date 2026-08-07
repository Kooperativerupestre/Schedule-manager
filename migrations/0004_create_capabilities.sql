CREATE TABLE capabilities (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capability VARCHAR(100) NOT NULL UNIQUE CHECK (
        capability IN (
            'business_read',
            'business_manage',

            'unit_read',
            'unit_manage',

            'workstation_read',
            'workstation_manage',

            'business_holidays_read',
            'business_holidays_manage',

            'unit_holidays_read',
            'unit_holidays_manage',

            'workstation_holidays_read',
            'workstation_holidays_manage',

            'members_invite',
            'members_manage',
            'members_read',

            'unit_lifecycle_manage',
            'workstation_lifecycle_manage',

            'workstation_work_manage',
            'workstation_work_read'
        )
    )
);

INSERT INTO capabilities (capability)
VALUES
    ('business_read'),
    ('business_manage'),
    ('unit_read'),
    ('unit_manage'),
    ('workstation_read'),
    ('workstation_manage'),
    ('business_holidays_read'),
    ('business_holidays_manage'),
    ('unit_holidays_read'),
    ('unit_holidays_manage'),
    ('workstation_holidays_read'),
    ('workstation_holidays_manage'),
    ('members_invite'),
    ('members_manage'),
    ('members_read'),
    ('unit_lifecycle_manage'),
    ('workstation_lifecycle_manage'),
    ('workstation_work_manage'),
    ('workstation_work_read');
    