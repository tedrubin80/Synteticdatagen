"""Date and time generators."""

from datetime import datetime, timedelta
import random
from faker import Faker
from .base import BaseGenerator

fake = Faker()


class DateGenerator(BaseGenerator):
    """Generate random dates."""

    def generate(self) -> str:
        """Generate a random date."""
        start_date = self.constraints.get('start', '2020-01-01')
        end_date = self.constraints.get('end', '2024-12-31')
        date_format = self.constraints.get('format', '%Y-%m-%d')

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        random_date = start_date + timedelta(days=random_days)

        return random_date.strftime(date_format)


class DateTimeGenerator(BaseGenerator):
    """Generate random datetimes."""

    def generate(self) -> str:
        """Generate a random datetime."""
        start_date = self.constraints.get('start', '2020-01-01 00:00:00')
        end_date = self.constraints.get('end', '2024-12-31 23:59:59')
        datetime_format = self.constraints.get('format', '%Y-%m-%d %H:%M:%S')

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        time_between = end_date - start_date
        seconds_between = time_between.total_seconds()
        random_seconds = random.randint(0, int(seconds_between))
        random_datetime = start_date + timedelta(seconds=random_seconds)

        return random_datetime.strftime(datetime_format)
