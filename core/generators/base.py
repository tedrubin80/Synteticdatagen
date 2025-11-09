"""Base generator class for all field types."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseGenerator(ABC):
    """Abstract base class for data generators."""

    def __init__(self, constraints: Dict[str, Any] = None):
        """Initialize generator with optional constraints."""
        self.constraints = constraints or {}

    @abstractmethod
    def generate(self) -> Any:
        """Generate a single value."""
        pass

    def generate_batch(self, count: int) -> list:
        """Generate multiple values."""
        return [self.generate() for _ in range(count)]
