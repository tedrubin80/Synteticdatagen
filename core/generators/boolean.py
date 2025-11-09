"""Boolean data generator."""

import random
from .base import BaseGenerator


class BooleanGenerator(BaseGenerator):
    """Generate random boolean values."""

    def generate(self) -> bool:
        """Generate a random boolean."""
        probability = self.constraints.get('true_probability', 0.5)
        return random.random() < probability
