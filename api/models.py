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
    rows: int = Field(..., ge=1, le=100_000, description="Number of rows to generate")
    fields: List[FieldConfig] = Field(..., min_length=1, description="Field definitions")
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


class KaggleSearchRequest(BaseModel):
    """Request to search Kaggle datasets. Credentials are used for this call only."""
    kaggle_username: str = Field(..., description="Kaggle account username")
    kaggle_key: str = Field(..., description="Kaggle API key (from kaggle.com/settings)")
    query: str = Field(..., min_length=1, description="Search keywords")


class KaggleDatasetInfo(BaseModel):
    """Summary info about a Kaggle dataset."""
    ref: str = Field(..., description="Dataset reference as owner/dataset-slug")
    title: str
    subtitle: Optional[str] = None
    size: Optional[str] = None
    last_updated: Optional[str] = None


class KaggleSearchResponse(BaseModel):
    """Response listing matching Kaggle datasets."""
    success: bool = True
    datasets: List[KaggleDatasetInfo]


class KaggleCloneRequest(BaseModel):
    """Request to learn a Kaggle dataset's schema and generate a synthetic clone of it."""
    kaggle_username: str = Field(..., description="Kaggle account username")
    kaggle_key: str = Field(..., description="Kaggle API key (from kaggle.com/settings)")
    dataset_ref: str = Field(..., description="Dataset reference as owner/dataset-slug")
    rows: int = Field(default=100, ge=1, le=100_000, description="Number of synthetic rows to generate")
    format: Literal["json", "csv", "sql"] = Field(default="json", description="Output format")
    table_name: Optional[str] = Field(default="synthetic_data", description="Table name for SQL format")
    sample_rows: int = Field(default=2000, ge=10, le=20000, description="Rows to sample from the source dataset when learning its schema")


class KaggleSchemaResponse(BaseModel):
    """Response containing the schema learned from a Kaggle dataset, without any real data."""
    success: bool = True
    dataset_ref: str
    fields: List[FieldConfig]
    rows_sampled: int
