from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
import json

from app import db
from models import GenerationHistory

# Import core modules from parent directory
from core.engine import SyntheticDataEngine
from core.schema import FieldSchema
from core.kaggle_client import KaggleClient, KaggleError
from core.schema_learner import infer_schema
from formatters.csv_formatter import CSVFormatter
from formatters.json_formatter import JSONFormatter
from formatters.sql_formatter import SQLFormatter

generator_bp = Blueprint('generator', __name__)

FIELD_TYPES = [
    {'value': 'integer', 'label': 'Integer', 'category': 'Numeric'},
    {'value': 'float', 'label': 'Float', 'category': 'Numeric'},
    {'value': 'string', 'label': 'String', 'category': 'Text'},
    {'value': 'name', 'label': 'Full Name', 'category': 'Text'},
    {'value': 'company', 'label': 'Company Name', 'category': 'Text'},
    {'value': 'email', 'label': 'Email Address', 'category': 'Contact'},
    {'value': 'phone', 'label': 'Phone Number', 'category': 'Contact'},
    {'value': 'url', 'label': 'URL', 'category': 'Contact'},
    {'value': 'address', 'label': 'Street Address', 'category': 'Location'},
    {'value': 'city', 'label': 'City', 'category': 'Location'},
    {'value': 'country', 'label': 'Country', 'category': 'Location'},
    {'value': 'date', 'label': 'Date', 'category': 'Date/Time'},
    {'value': 'datetime', 'label': 'DateTime', 'category': 'Date/Time'},
    {'value': 'boolean', 'label': 'Boolean', 'category': 'Other'},
    {'value': 'uuid', 'label': 'UUID', 'category': 'Other'},
    {'value': 'category', 'label': 'Custom Category', 'category': 'Other'},

    # Call center metrics
    {'value': 'call_duration', 'label': 'Call Duration (sec)', 'category': 'Call Center'},
    {'value': 'wait_time', 'label': 'Queue Wait Time (sec)', 'category': 'Call Center'},
    {'value': 'hold_time', 'label': 'Hold Time (sec)', 'category': 'Call Center'},
    {'value': 'call_type', 'label': 'Call Type', 'category': 'Call Center'},
    {'value': 'call_channel', 'label': 'Call Channel', 'category': 'Call Center'},
    {'value': 'call_department', 'label': 'Department/Queue', 'category': 'Call Center'},
    {'value': 'agent_id', 'label': 'Agent ID', 'category': 'Call Center'},
    {'value': 'call_priority', 'label': 'Call Priority', 'category': 'Call Center'},
    {'value': 'call_outcome', 'label': 'Call Outcome', 'category': 'Call Center'},
    {'value': 'resolution_status', 'label': 'Resolution Status', 'category': 'Call Center'},
    {'value': 'sentiment', 'label': 'Sentiment', 'category': 'Call Center'},
    {'value': 'csat_score', 'label': 'CSAT Score', 'category': 'Call Center'},
    {'value': 'nps_score', 'label': 'NPS Score', 'category': 'Call Center'},

    # Demographics
    {'value': 'age', 'label': 'Age', 'category': 'Demographics'},
    {'value': 'gender', 'label': 'Gender', 'category': 'Demographics'},
    {'value': 'ethnicity', 'label': 'Ethnicity', 'category': 'Demographics'},
    {'value': 'marital_status', 'label': 'Marital Status', 'category': 'Demographics'},
    {'value': 'education_level', 'label': 'Education Level', 'category': 'Demographics'},
    {'value': 'employment_status', 'label': 'Employment Status', 'category': 'Demographics'},
    {'value': 'income_bracket', 'label': 'Income Bracket', 'category': 'Demographics'},
    {'value': 'household_size', 'label': 'Household Size', 'category': 'Demographics'},
    {'value': 'language_preference', 'label': 'Language Preference', 'category': 'Demographics'},
    {'value': 'generation', 'label': 'Generation', 'category': 'Demographics'},
]


@generator_bp.route('/')
@login_required
def index():
    return render_template(
        'generator/index.html',
        field_types=FIELD_TYPES,
        has_kaggle_creds=current_user.has_kaggle_credentials(),
        kaggle_username=current_user.kaggle_username,
    )


def _resolve_kaggle_creds(data):
    """Use credentials from the request if given, else fall back to the user's saved ones."""
    username = (data.get('kaggle_username') or '').strip() or current_user.kaggle_username or ''
    key = (data.get('kaggle_key') or '').strip() or (current_user.get_kaggle_key() or '')
    return username, key


@generator_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    if not current_user.try_consume_request():
        return jsonify({
            'error': 'Daily limit reached. Your quota resets at midnight UTC.'
        }), 429

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request data'}), 400

    rows = data.get('rows', 10)
    output_format = data.get('format', 'json')
    table_name = data.get('table_name', 'synthetic_data')
    fields = data.get('fields', [])

    # Validate
    max_rows = current_user.get_max_rows()
    if rows > max_rows:
        return jsonify({
            'error': f'Maximum {max_rows:,} rows allowed per request.'
        }), 400

    if not fields:
        return jsonify({'error': 'At least one field is required'}), 400

    if len(fields) > 20:
        return jsonify({'error': 'Maximum 20 fields allowed'}), 400

    try:
        # Build schema
        schema = []
        for field in fields:
            field_schema = FieldSchema(
                name=field['name'],
                field_type=field['type'],
                constraints=field.get('constraints', {})
            )
            schema.append(field_schema)

        # Generate data - use SyntheticDataEngine
        engine = SyntheticDataEngine(schema)
        # Generate in batches if needed (original engine limits to 1000 per call)
        generated_data = []
        remaining = rows
        while remaining > 0:
            batch_size = min(remaining, 1000)
            generated_data.extend(engine.generate(batch_size))
            remaining -= batch_size

        # Format output using static methods
        if output_format == 'csv':
            output = CSVFormatter.format(generated_data)
            content_type = 'text/csv'
        elif output_format == 'sql':
            output = SQLFormatter.format(generated_data, table_name)
            content_type = 'text/plain'
        else:
            output = JSONFormatter.format(generated_data)
            content_type = 'application/json'

        # Track usage (already consumed atomically at request start)

        # Save to history
        history = GenerationHistory(
            user_id=current_user.id,
            rows_generated=rows,
            output_format=output_format,
            field_config=[{'name': f['name'], 'type': f['type']} for f in fields]
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': output,
            'content_type': content_type,
            'rows': rows,
            'format': output_format
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generator_bp.route('/download', methods=['POST'])
@login_required
def download():
    data = request.get_json()
    content = data.get('content', '')
    output_format = data.get('format', 'json')
    filename = data.get('filename', 'synthetic_data')

    extensions = {'csv': 'csv', 'json': 'json', 'sql': 'sql'}
    content_types = {
        'csv': 'text/csv',
        'json': 'application/json',
        'sql': 'text/plain'
    }

    ext = extensions.get(output_format, 'txt')
    content_type = content_types.get(output_format, 'text/plain')

    return Response(
        content,
        mimetype=content_type,
        headers={
            'Content-Disposition': f'attachment; filename={filename}.{ext}'
        }
    )


@generator_bp.route('/kaggle/search', methods=['POST'])
@login_required
def kaggle_search():
    data = request.get_json() or {}
    username, key = _resolve_kaggle_creds(data)
    query = (data.get('query') or '').strip()

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    try:
        client = KaggleClient(username, key)
        results = client.search_datasets(query)
        datasets = [
            {
                'ref': item.get('ref', ''),
                'title': item.get('title', item.get('ref', '')),
                'subtitle': item.get('subtitle'),
                'size': str(item.get('size')) if item.get('size') is not None else None,
            }
            for item in results
        ]
        return jsonify({'success': True, 'datasets': datasets})
    except KaggleError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Kaggle request failed: {str(e)}'}), 502


@generator_bp.route('/kaggle/learn', methods=['POST'])
@login_required
def kaggle_learn():
    """Learn a field schema from a Kaggle dataset so it can populate the field editor.

    Only the inferred schema (types + distributions) is returned - the real
    dataset rows and the submitted credentials are never persisted.
    """
    data = request.get_json() or {}
    username, key = _resolve_kaggle_creds(data)
    dataset_ref = (data.get('dataset_ref') or '').strip()

    if '/' not in dataset_ref:
        return jsonify({'error': "dataset_ref must be in 'owner/dataset-slug' format"}), 400

    owner, _, dataset = dataset_ref.partition('/')

    try:
        client = KaggleClient(username, key)
        rows = client.fetch_dataset_rows(owner, dataset, max_rows=2000)
        fields = infer_schema(rows)
        if not fields:
            return jsonify({'error': 'Could not infer any fields from this dataset'}), 400

        return jsonify({
            'success': True,
            'dataset_ref': dataset_ref,
            'rows_sampled': len(rows),
            'fields': [f.to_dict() for f in fields],
        })
    except KaggleError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Kaggle request failed: {str(e)}'}), 502


@generator_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    history = current_user.generation_history.order_by(
        GenerationHistory.created_at.desc()
    ).paginate(page=page, per_page=20)
    return render_template('generator/history.html', history=history)
