"""Call center metrics generators (durations, queue/agent info, outcomes, scores)."""

import math
import random
from .base import BaseGenerator
from .common import weighted_choice


def _lognormal_duration(mean: float, min_val: int, max_val: int, sigma: float = 0.6) -> int:
    """Model a duration (seconds) with the right-skewed shape real call times have.

    Most calls cluster near `mean` with a long tail of outliers, rather than
    the uniform spread a plain randint would produce.
    """
    mu = math.log(max(mean, 1)) - (sigma ** 2) / 2
    value = random.lognormvariate(mu, sigma)
    return int(min(max(value, min_val), max_val))


class CallDurationGenerator(BaseGenerator):
    """Generate total call handle time in seconds."""

    def generate(self) -> int:
        min_val = self.constraints.get('min', 15)
        max_val = self.constraints.get('max', 1800)
        mean = self.constraints.get('mean', 240)
        return _lognormal_duration(mean, min_val, max_val)


class WaitTimeGenerator(BaseGenerator):
    """Generate time (seconds) a caller waited in queue before being answered."""

    def generate(self) -> int:
        min_val = self.constraints.get('min', 0)
        max_val = self.constraints.get('max', 900)
        mean = self.constraints.get('mean', 45)
        return _lognormal_duration(mean, min_val, max_val)


class HoldTimeGenerator(BaseGenerator):
    """Generate time (seconds) a caller spent on hold during the call."""

    def generate(self) -> int:
        min_val = self.constraints.get('min', 0)
        max_val = self.constraints.get('max', 600)
        mean = self.constraints.get('mean', 30)
        return _lognormal_duration(mean, min_val, max_val)


class CallTypeGenerator(BaseGenerator):
    """Generate the direction of the call."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['Inbound', 'Outbound'],
            default_weights=[0.75, 0.25],
        )


class CallChannelGenerator(BaseGenerator):
    """Generate the channel a contact came in on."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['Phone', 'Chat', 'Email', 'Social Media'],
            default_weights=[0.6, 0.25, 0.1, 0.05],
        )


class CallDepartmentGenerator(BaseGenerator):
    """Generate the queue/department that handled the call."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=[
                'Customer Service', 'Technical Support', 'Billing',
                'Sales', 'Retention', 'Returns & Exchanges',
            ],
            default_weights=[0.3, 0.25, 0.2, 0.1, 0.1, 0.05],
        )


class AgentIdGenerator(BaseGenerator):
    """Generate an agent identifier from a bounded pool, mimicking a real roster."""

    def generate(self) -> str:
        prefix = self.constraints.get('prefix', 'AGT')
        num_agents = self.constraints.get('num_agents', 50)
        agent_num = random.randint(1, num_agents)
        return f"{prefix}-{agent_num:04d}"


class CallPriorityGenerator(BaseGenerator):
    """Generate the priority/severity assigned to a call or ticket."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['Low', 'Medium', 'High', 'Critical'],
            default_weights=[0.4, 0.4, 0.15, 0.05],
        )


class CallOutcomeGenerator(BaseGenerator):
    """Generate how the call ended."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=[
                'Resolved', 'Escalated', 'Follow-up Required',
                'Abandoned', 'Voicemail', 'Transferred',
            ],
            default_weights=[0.55, 0.12, 0.13, 0.08, 0.05, 0.07],
        )


class ResolutionStatusGenerator(BaseGenerator):
    """Generate the resolution state of the underlying issue/ticket."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['Resolved', 'Unresolved', 'Escalated', 'Pending'],
            default_weights=[0.65, 0.1, 0.1, 0.15],
        )


class SentimentGenerator(BaseGenerator):
    """Generate a sentiment label, e.g. from call transcript analysis."""

    def generate(self) -> str:
        return weighted_choice(
            self.constraints,
            default_choices=['Positive', 'Neutral', 'Negative'],
            default_weights=[0.45, 0.35, 0.2],
        )


class CSATScoreGenerator(BaseGenerator):
    """Generate a customer satisfaction score (1-5), skewed toward satisfied."""

    def generate(self) -> int:
        scale_max = self.constraints.get('scale', 5)
        default_weights = [0.05, 0.08, 0.12, 0.35, 0.4][:scale_max]
        return int(weighted_choice(
            self.constraints,
            default_choices=list(range(1, scale_max + 1)),
            default_weights=default_weights,
        ))


class NPSScoreGenerator(BaseGenerator):
    """Generate a Net Promoter Score response (0-10), skewed toward promoters."""

    def generate(self) -> int:
        choices = list(range(0, 11))
        weights = [0.02, 0.02, 0.02, 0.03, 0.04, 0.06, 0.08, 0.12, 0.18, 0.2, 0.23]
        return int(weighted_choice(self.constraints, choices, weights))
