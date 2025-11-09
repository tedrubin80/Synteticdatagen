"""Numeric data generators."""

import random
from .base import BaseGenerator


class IntegerGenerator(BaseGenerator):
    """Generate random integers."""

    def generate(self) -> int:
        """Generate a random integer within constraints."""
        min_val = self.constraints.get('min', 0)
        max_val = self.constraints.get('max', 1000)
        return random.randint(min_val, max_val)


class FloatGenerator(BaseGenerator):
    """Generate random floats."""

    def generate(self) -> float:
        """Generate a random float within constraints."""
        min_val = self.constraints.get('min', 0.0)
        max_val = self.constraints.get('max', 1000.0)
        precision = self.constraints.get('precision', 2)

        value = random.uniform(min_val, max_val)
        return round(value, precision)
