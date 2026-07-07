CREATE TABLE capabilities (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capability VARCHAR(100) NOT NULL UNIQUE CHECK (
        capability IN (
            'manage_workstation',
            'delete_workstation',
            'create_workstation',
            'delete_unit',
            'create_unit',
            'create_franchise_holiday',
            'delete_franchise_holiday',
            'create_unit_holiday',
            'delete_unit_holiday'
        )
    )
);