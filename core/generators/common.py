"""Generic generators shared across domains."""

import random
from typing import Any, Dict, List, Optional
from .base import BaseGenerator


def weighted_choice(constraints: Dict[str, Any], default_choices: List[str],
                     default_weights: Optional[List[float]] = None) -> Any:
    """Pick a random value, letting constraints override the choice pool/weights.

    Domain generators (gender, sentiment, call_outcome, ...) ship with a
    realistic default distribution but stay fully overridable via
    `constraints={'choices': [...], 'weights': [...]}`.
    """
    choices = constraints.get('choices', default_choices)
    weights = constraints.get('weights', default_weights if choices is default_choices else None)

    if weights and len(weights) == len(choices):
        return random.choices(choices, weights=weights, k=1)[0]
    return random.choice(choices)


class CategoryGenerator(BaseGenerator):
    """Generate values sampled from a set of choices, optionally weighted.

    Powers domain field types (gender, sentiment, ...) as well as the
    Kaggle schema learner, which infers `choices`/`weights` from real data.
    """

    def generate(self) -> Any:
        """Generate a random category value."""
        choices = self.constraints.get('choices', ['A', 'B'])
        weights = self.constraints.get('weights')

        if weights and len(weights) == len(choices):
            return random.choices(choices, weights=weights, k=1)[0]
        return random.choice(choices)
