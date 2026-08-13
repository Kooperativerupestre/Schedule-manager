from schedule_manager.holidays.repository import HolidayRepositoryContext
from psycopg import sql
from schedule_manager.workstations.workstation.errors import WorkstationNotFoundError

HolidayConfigWorkstationHolidays = HolidayRepositoryContext(
    table_name=sql.Identifier("workstation_holidays"),
    owner_column=sql.Identifier("workstation_id"),
    foreign_key_error=WorkstationNotFoundError
)

