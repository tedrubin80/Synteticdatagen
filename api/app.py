"""FastAPI application for synthetic data generation."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Union
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SyntheticDataEngine, FieldSchema
from formatters import CSVFormatter, JSONFormatter, SQLFormatter
from api.models import (
    GenerateRequest, GenerateResponse, FieldTypesResponse,
    FieldTypeInfo, ErrorResponse
)

app = FastAPI(
    title="Syngen API",
    description="REST API for generating synthetic data with customizable fields and output formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/", tags=["General"])
async def root():
    """Health check endpoint."""
    return {
        "service": "Syngen API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health", tags=["General"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/field-types", response_model=FieldTypesResponse, tags=["Info"])
async def get_field_types():
    """Get list of supported field types and their constraints."""
    field_types = [
        FieldTypeInfo(
            type="integer",
            description="Random integer within range",
            supported_constraints=["min", "max"]
        ),
        FieldTypeInfo(
            type="float",
            description="Random floating-point number",
            supported_constraints=["min", "max", "precision"]
        ),
        FieldTypeInfo(
            type="string",
            description="Random alphanumeric string",
            supported_constraints=["length", "min_length", "max_length", "charset"]
        ),
        FieldTypeInfo(
            type="email",
            description="Random email address",
            supported_constraints=["domain"]
        ),
        FieldTypeInfo(
            type="phone",
            description="Random phone number",
            supported_constraints=["format"]
        ),
        FieldTypeInfo(
            type="date",
            description="Random date within range",
            supported_constraints=["start", "end", "format"]
        ),
        FieldTypeInfo(
            type="datetime",
            description="Random datetime within range",
            supported_constraints=["start", "end", "format"]
        ),
        FieldTypeInfo(
            type="boolean",
            description="Random boolean value",
            supported_constraints=["true_probability"]
        ),
        FieldTypeInfo(
            type="uuid",
            description="Universally unique identifier",
            supported_constraints=["version"]
        ),
        FieldTypeInfo(
            type="name",
            description="Random person name",
            supported_constraints=["type"]
        ),
        FieldTypeInfo(
            type="address",
            description="Random street address",
            supported_constraints=[]
        ),
        FieldTypeInfo(
            type="city",
            description="Random city name",
            supported_constraints=[]
        ),
        FieldTypeInfo(
            type="country",
            description="Random country name",
            supported_constraints=[]
        ),
        FieldTypeInfo(
            type="company",
            description="Random company name",
            supported_constraints=[]
        ),
        FieldTypeInfo(
            type="url",
            description="Random URL",
            supported_constraints=[]
        ),
    ]

    return FieldTypesResponse(field_types=field_types)


@app.post("/generate", response_model=None, tags=["Generation"])
async def generate_data(request: GenerateRequest):
    """
    Generate synthetic data based on field configuration.

    Returns data in the requested format:
    - json: Returns JSON array of objects
    - csv: Returns CSV string with headers
    - sql: Returns SQL INSERT statements
    """
    try:
        # Convert API model to FieldSchema objects
        fields = []
        for field_config in request.fields:
            field_schema = FieldSchema(
                name=field_config.name,
                field_type=field_config.type,
                constraints=field_config.constraints or {}
            )
            field_schema.validate()
            fields.append(field_schema)

        # Generate data
        engine = SyntheticDataEngine(fields)
        data = engine.generate(request.rows)

        # Format output
        if request.format == "json":
            return JSONResponse(
                content={
                    "success": True,
                    "rows_generated": len(data),
                    "format": "json",
                    "data": data
                }
            )
        elif request.format == "csv":
            csv_output = CSVFormatter.format(data)
            return PlainTextResponse(
                content=csv_output,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=synthetic_data.csv"}
            )
        elif request.format == "sql":
            sql_output = SQLFormatter.format(data, request.table_name)
            return PlainTextResponse(
                content=sql_output,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={request.table_name}.sql"}
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/generate/preview", response_model=GenerateResponse, tags=["Generation"])
async def generate_preview(request: GenerateRequest):
    """
    Generate a preview of synthetic data (always returns JSON, max 10 rows).
    Useful for testing field configurations before generating large datasets.
    """
    try:
        # Limit to 10 rows for preview
        preview_rows = min(request.rows, 10)

        # Convert API model to FieldSchema objects
        fields = []
        for field_config in request.fields:
            field_schema = FieldSchema(
                name=field_config.name,
                field_type=field_config.type,
                constraints=field_config.constraints or {}
            )
            field_schema.validate()
            fields.append(field_schema)

        # Generate data
        engine = SyntheticDataEngine(fields)
        data = engine.generate(preview_rows)

        return GenerateResponse(
            success=True,
            rows_generated=len(data),
            format="json",
            data=data
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
