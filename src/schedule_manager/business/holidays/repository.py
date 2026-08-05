from schedule_manager.holidays.repository import HolidayRepositoryContext
from psycopg import sql
from schedule_manager.business.errors import BusinessNotFoundError

class HolidayConfigBusinesslHolidays(HolidayRepositoryContext):
    table_name = sql.Identifier("business_holidays")
    owner_column = sql.Identifier("business")

    foreign_key_error = BusinessNotFoundError

