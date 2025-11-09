"""Text-based data generators."""

import random
import string
import uuid
from faker import Faker
from .base import BaseGenerator

fake = Faker()


class StringGenerator(BaseGenerator):
    """Generate random strings."""

    def generate(self) -> str:
        """Generate a random string."""
        length = self.constraints.get('length', 10)
        min_length = self.constraints.get('min_length', length)
        max_length = self.constraints.get('max_length', length)

        actual_length = random.randint(min_length, max_length) if min_length != max_length else length

        charset = self.constraints.get('charset', string.ascii_letters + string.digits)
        return ''.join(random.choices(charset, k=actual_length))


class EmailGenerator(BaseGenerator):
    """Generate random email addresses."""

    def generate(self) -> str:
        """Generate a random email address."""
        domain = self.constraints.get('domain', None)
        if domain:
            username = fake.user_name()
            return f"{username}@{domain}"
        return fake.email()


class PhoneGenerator(BaseGenerator):
    """Generate random phone numbers."""

    def generate(self) -> str:
        """Generate a random phone number."""
        format_type = self.constraints.get('format', 'US')
        if format_type == 'US':
            return fake.phone_number()
        return fake.phone_number()


class UUIDGenerator(BaseGenerator):
    """Generate UUIDs."""

    def generate(self) -> str:
        """Generate a UUID."""
        version = self.constraints.get('version', 4)
        if version == 4:
            return str(uuid.uuid4())
        return str(uuid.uuid4())


class NameGenerator(BaseGenerator):
    """Generate random names."""

    def generate(self) -> str:
        """Generate a random name."""
        name_type = self.constraints.get('type', 'full')
        if name_type == 'first':
            return fake.first_name()
        elif name_type == 'last':
            return fake.last_name()
        return fake.name()


class AddressGenerator(BaseGenerator):
    """Generate random addresses."""

    def generate(self) -> str:
        """Generate a random address."""
        return fake.address().replace('\n', ', ')


class CityGenerator(BaseGenerator):
    """Generate random city names."""

    def generate(self) -> str:
        """Generate a random city name."""
        return fake.city()


class CountryGenerator(BaseGenerator):
    """Generate random country names."""

    def generate(self) -> str:
        """Generate a random country name."""
        return fake.country()


class CompanyGenerator(BaseGenerator):
    """Generate random company names."""

    def generate(self) -> str:
        """Generate a random company name."""
        return fake.company()


class URLGenerator(BaseGenerator):
    """Generate random URLs."""

    def generate(self) -> str:
        """Generate a random URL."""
        return fake.url()
