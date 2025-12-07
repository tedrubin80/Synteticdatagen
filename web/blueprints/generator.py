from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
import json

from app import db
from models import GenerationHistory

# Import core modules from parent directory
from core.engine import SyntheticDataEngine
from core.schema import FieldSchema
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
]


@generator_bp.route('/')
@login_required
def index():
    return render_template('generator/index.html', field_types=FIELD_TYPES)


@generator_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    if not current_user.can_make_request():
        return jsonify({
            'error': 'Daily limit reached. Upgrade to Pro for more requests.'
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
            'error': f'Maximum {max_rows} rows allowed. Upgrade to Pro for more.'
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

        # Track usage
        current_user.increment_usage()

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


@generator_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    history = current_user.generation_history.order_by(
        GenerationHistory.created_at.desc()
    ).paginate(page=page, per_page=20)
    return render_template('generator/history.html', history=history)
