"""Demographic data generators."""

import random
from .base import BaseGenerator
from .common import weighted_choice

# Ordered youngest to oldest; weights below approximate current US population share.
_GENERATIONS = [
    'Generation Alpha', 'Generation Z', 'Millennial',
    'Generation X', 'Baby Boomer', 'Silent Generation',
]


class AgeGenerator(BaseGenerator):
    """Generate an age in years, roughly matching an adult population skew."""

    def generate(self) -> int:
        min_val = self.constraints.get('min', 18)
        max_val = self.constraints.get('max', 90)
        # Triangular skews the bulk of ages toward working-age adults
        # rather than a flat spread across the whole range.
        mode = self.constraints.get('mode', min(min_val + 25, max_val))
        return int(random.triangular(min_val, max_val, mode))


class GenderGenerator(BaseGenerator):
    """Generate a gender identity."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
            default_weights=[0.48, 0.48, 0.02, 0.02],
        )


class EthnicityGenerator(BaseGenerator):
    """Generate a race/ethnicity category (US Census-style buckets by default)."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=[
                'White', 'Hispanic or Latino', 'Black or African American',
                'Asian', 'American Indian or Alaska Native',
                'Native Hawaiian or Other Pacific Islander', 'Two or More Races',
            ],
            default_weights=[0.58, 0.19, 0.12, 0.06, 0.01, 0.002, 0.038],
        )


class MaritalStatusGenerator(BaseGenerator):
    """Generate a marital status."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['Single', 'Married', 'Divorced', 'Widowed', 'Separated'],
            default_weights=[0.35, 0.45, 0.12, 0.05, 0.03],
        )


class EducationLevelGenerator(BaseGenerator):
    """Generate a highest-education-attained level."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=[
                'Less than High School', 'High School Diploma', 'Some College',
                "Associate Degree", "Bachelor's Degree", "Master's Degree", 'Doctorate',
            ],
            default_weights=[0.1, 0.27, 0.2, 0.1, 0.22, 0.09, 0.02],
        )


class EmploymentStatusGenerator(BaseGenerator):
    """Generate an employment status."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=[
                'Employed Full-time', 'Employed Part-time', 'Self-employed',
                'Unemployed', 'Retired', 'Student',
            ],
            default_weights=[0.5, 0.12, 0.08, 0.06, 0.14, 0.1],
        )


class IncomeBracketGenerator(BaseGenerator):
    """Generate a household income bracket label."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=[
                'Under $25,000', '$25,000-$49,999', '$50,000-$74,999',
                '$75,000-$99,999', '$100,000-$149,999', '$150,000+',
            ],
            default_weights=[0.17, 0.22, 0.19, 0.15, 0.16, 0.11],
        )


class HouseholdSizeGenerator(BaseGenerator):
    """Generate the number of people in a household."""

    def generate(self) -> int:
        min_val = self.constraints.get('min', 1)
        max_val = self.constraints.get('max', 7)
        choices = list(range(min_val, max_val + 1))
        base_weights = [0.28, 0.34, 0.16, 0.13, 0.06, 0.02, 0.01]
        weights = (base_weights + [0.005] * len(choices))[:len(choices)]
        return int(weighted_choice(self.constraints, choices, weights))


class LanguagePreferenceGenerator(BaseGenerator):
    """Generate a preferred language, defaulting to a US-market mix."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['English', 'Spanish', 'Mandarin', 'Vietnamese', 'Other'],
            default_weights=[0.78, 0.13, 0.03, 0.02, 0.04],
        )


class GenerationGenerator(BaseGenerator):
    """Generate a generational cohort label (Gen Z, Millennial, ...)."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=_GENERATIONS,
            default_weights=[0.14, 0.18, 0.22, 0.2, 0.21, 0.05],
        )
