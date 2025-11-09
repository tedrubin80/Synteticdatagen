"""Schema definitions for synthetic data fields."""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class FieldSchema:
    """Defines a single field in the synthetic data schema."""

    name: str
    field_type: str
    constraints: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate the field schema."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Field name must be a non-empty string")

        valid_types = [
            'integer', 'float', 'string', 'email', 'phone',
            'date', 'datetime', 'boolean', 'uuid', 'name',
            'address', 'city', 'country', 'company', 'url'
        ]

        if self.field_type not in valid_types:
            raise ValueError(f"Invalid field type: {self.field_type}. Must be one of {valid_types}")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'name': self.name,
            'type': self.field_type,
            'constraints': self.constraints
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldSchema':
        """Create FieldSchema from dictionary."""
        return cls(
            name=data['name'],
            field_type=data.get('type', data.get('field_type', 'string')),
            constraints=data.get('constraints', {})
        )
