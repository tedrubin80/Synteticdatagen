"""FastAPI application for synthetic data generation."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Union
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SyntheticDataEngine, FieldSchema
from core.kaggle_client import KaggleClient, KaggleError
from core.schema_learner import infer_schema
from formatters import CSVFormatter, JSONFormatter, SQLFormatter
from api.models import (
    GenerateRequest, GenerateResponse, FieldTypesResponse,
    FieldTypeInfo, ErrorResponse, FieldConfig,
    KaggleSearchRequest, KaggleSearchResponse, KaggleDatasetInfo,
    KaggleCloneRequest, KaggleSchemaResponse,
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
        FieldTypeInfo(
            type="category",
            description="Random value sampled from a custom list, optionally weighted",
            supported_constraints=["choices", "weights"]
        ),
        # Call center metrics
        FieldTypeInfo(
            type="call_duration",
            description="Call handle time in seconds (right-skewed distribution)",
            supported_constraints=["min", "max", "mean"]
        ),
        FieldTypeInfo(
            type="wait_time",
            description="Time in queue before being answered, in seconds",
            supported_constraints=["min", "max", "mean"]
        ),
        FieldTypeInfo(
            type="hold_time",
            description="Time on hold during the call, in seconds",
            supported_constraints=["min", "max", "mean"]
        ),
        FieldTypeInfo(
            type="call_type",
            description="Call direction (Inbound/Outbound)",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="call_channel",
            description="Contact channel (Phone/Chat/Email/Social Media)",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="call_department",
            description="Queue/department that handled the call",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="agent_id",
            description="Agent identifier drawn from a bounded roster",
            supported_constraints=["prefix", "num_agents"]
        ),
        FieldTypeInfo(
            type="call_priority",
            description="Priority/severity of the call or ticket",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="call_outcome",
            description="How the call ended (Resolved, Escalated, Abandoned, ...)",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="resolution_status",
            description="Resolution state of the underlying issue",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="sentiment",
            description="Sentiment label (Positive/Neutral/Negative)",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="csat_score",
            description="Customer satisfaction score, skewed toward satisfied",
            supported_constraints=["scale", "choices", "weights"]
        ),
        FieldTypeInfo(
            type="nps_score",
            description="Net Promoter Score response (0-10), skewed toward promoters",
            supported_constraints=["choices", "weights"]
        ),
        # Demographics
        FieldTypeInfo(
            type="age",
            description="Age in years, skewed toward working-age adults",
            supported_constraints=["min", "max", "mode"]
        ),
        FieldTypeInfo(
            type="gender",
            description="Gender identity",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="ethnicity",
            description="Race/ethnicity category (US Census-style buckets)",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="marital_status",
            description="Marital status",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="education_level",
            description="Highest level of education attained",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="employment_status",
            description="Employment status",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="income_bracket",
            description="Household income bracket label",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="household_size",
            description="Number of people in the household",
            supported_constraints=["min", "max", "choices", "weights"]
        ),
        FieldTypeInfo(
            type="language_preference",
            description="Preferred language",
            supported_constraints=["choices", "weights"]
        ),
        FieldTypeInfo(
            type="generation",
            description="Generational cohort label (Gen Z, Millennial, ...)",
            supported_constraints=["choices", "weights"]
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


@app.post("/kaggle/search", response_model=KaggleSearchResponse, tags=["Kaggle"])
async def kaggle_search(request: KaggleSearchRequest):
    """
    Search public Kaggle datasets by keyword.

    Credentials (your Kaggle username + API key from kaggle.com/settings)
    are used only for this request and are never stored server-side.
    """
    try:
        client = KaggleClient(request.kaggle_username, request.kaggle_key)
        results = client.search_datasets(request.query)
        datasets = [
            KaggleDatasetInfo(
                ref=item.get("ref", ""),
                title=item.get("title", item.get("ref", "")),
                subtitle=item.get("subtitle"),
                size=str(item.get("size")) if item.get("size") is not None else None,
                last_updated=item.get("lastUpdated"),
            )
            for item in results
        ]
        return KaggleSearchResponse(datasets=datasets)
    except KaggleError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Kaggle request failed: {str(e)}")


@app.post("/kaggle/schema", response_model=KaggleSchemaResponse, tags=["Kaggle"])
async def kaggle_schema(request: KaggleCloneRequest):
    """
    Learn a synthetic-data field schema from a Kaggle dataset.

    Downloads a sample of the dataset's first CSV file, infers a field type
    and realistic constraints per column, and returns that schema only -
    no real rows are ever returned. Reuse the schema with `/generate` or
    `/kaggle/clone` to produce synthetic data shaped like the source.
    """
    try:
        owner, _, dataset = request.dataset_ref.partition("/")
        if not owner or not dataset:
            raise HTTPException(status_code=400, detail="dataset_ref must be in 'owner/dataset-slug' format")

        client = KaggleClient(request.kaggle_username, request.kaggle_key)
        rows = client.fetch_dataset_rows(owner, dataset, max_rows=request.sample_rows)
        fields = infer_schema(rows)

        return KaggleSchemaResponse(
            dataset_ref=request.dataset_ref,
            fields=[FieldConfig(name=f.name, type=f.field_type, constraints=f.constraints) for f in fields],
            rows_sampled=len(rows),
        )
    except KaggleError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Kaggle request failed: {str(e)}")


@app.post("/kaggle/clone", response_model=None, tags=["Kaggle"])
async def kaggle_clone(request: KaggleCloneRequest):
    """
    Learn a Kaggle dataset's schema and generate a fresh synthetic clone of it.

    This is `/kaggle/schema` followed by `/generate` in one call: the source
    data is used only to infer column types and distributions, then discarded.
    """
    try:
        owner, _, dataset = request.dataset_ref.partition("/")
        if not owner or not dataset:
            raise HTTPException(status_code=400, detail="dataset_ref must be in 'owner/dataset-slug' format")

        client = KaggleClient(request.kaggle_username, request.kaggle_key)
        source_rows = client.fetch_dataset_rows(owner, dataset, max_rows=request.sample_rows)
        fields = infer_schema(source_rows)
        if not fields:
            raise HTTPException(status_code=400, detail="Could not infer any fields from this dataset")

        engine = SyntheticDataEngine(fields)
        data = engine.generate(request.rows)

        if request.format == "csv":
            return PlainTextResponse(
                content=CSVFormatter.format(data),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=synthetic_clone.csv"},
            )
        elif request.format == "sql":
            return PlainTextResponse(
                content=SQLFormatter.format(data, request.table_name),
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={request.table_name}.sql"},
            )
        return JSONResponse(content={
            "success": True,
            "dataset_ref": request.dataset_ref,
            "rows_generated": len(data),
            "format": "json",
            "fields": [f.to_dict() for f in fields],
            "data": data,
        })
    except KaggleError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Kaggle request failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
