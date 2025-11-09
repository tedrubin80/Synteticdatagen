"""API request/response models."""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class FieldConfig(BaseModel):
    """Configuration for a single field."""
    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type (integer, string, email, etc.)")
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Field constraints")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "user_id",
                    "type": "integer",
                    "constraints": {"min": 1, "max": 1000}
                },
                {
                    "name": "email",
                    "type": "email",
                    "constraints": {}
                }
            ]
        }
    }


class GenerateRequest(BaseModel):
    """Request to generate synthetic data."""
    rows: int = Field(..., ge=1, le=1000, description="Number of rows to generate (1-1000)")
    fields: List[FieldConfig] = Field(..., min_length=1, max_length=10, description="Field definitions (1-10 fields)")
    format: Literal["json", "csv", "sql"] = Field(default="json", description="Output format")
    table_name: Optional[str] = Field(default="synthetic_data", description="Table name for SQL format")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "rows": 100,
                    "fields": [
                        {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 10000}},
                        {"name": "email", "type": "email"},
                        {"name": "created_at", "type": "date", "constraints": {"start": "2024-01-01", "end": "2024-12-31"}}
                    ],
                    "format": "json"
                }
            ]
        }
    }


class GenerateResponse(BaseModel):
    """Response containing generated data."""
    success: bool = Field(..., description="Whether generation was successful")
    rows_generated: int = Field(..., description="Number of rows generated")
    format: str = Field(..., description="Output format")
    data: Any = Field(..., description="Generated data (format depends on 'format' field)")


class FieldTypeInfo(BaseModel):
    """Information about a field type."""
    type: str = Field(..., description="Field type name")
    description: str = Field(..., description="Description of the field type")
    supported_constraints: List[str] = Field(..., description="Supported constraint parameters")


class FieldTypesResponse(BaseModel):
    """Response listing available field types."""
    field_types: List[FieldTypeInfo]


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
