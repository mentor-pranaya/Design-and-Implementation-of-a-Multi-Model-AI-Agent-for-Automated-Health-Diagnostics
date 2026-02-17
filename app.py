"""
Flask Web Application - Health Diagnostics AI
Run this file to start the web interface
"""
import os, sys, json, importlib.util
from pathlib import Path
from flask import (Flask, render_template, request,
                   jsonify, send_file, redirect, url_for)
from werkzeug.utils import secure_filename

# Path setup
BASE_DIR = Path(__file__).parent
SRC_DIR  = BASE_DIR / 'src'

def load_mod(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

app = Flask(__name__)
app.config['SECRET_KEY']         = 'health_ai_secret_2026'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER']      = str(BASE_DIR / 'data' / 'uploads')
app.config['OUTPUT_FOLDER']      = str(BASE_DIR / 'outputs')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'],  exist_ok=True)

ALLOWED = {'json', 'pdf', 'txt'}

def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED

_orchestrator     = None
_report_generator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        mod = load_mod('orchestrator',
                       SRC_DIR / 'orchestrator' / 'orchestrator.py')
        _orchestrator = mod.HealthDiagnosticsOrchestrator(str(SRC_DIR))
    return _orchestrator

def get_report_generator():
    global _report_generator
    if _report_generator is None:
        mod = load_mod('report_generator',
                       SRC_DIR / 'report' / 'report_generator.py')
        _report_generator = mod.ReportGenerator()
    return _report_generator

# ══════════════════════════════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')


# ── Upload & analyse ──────────────────────────────────────────────────
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # ── Validate upload ──────────────────────────────────────────
        if 'file' not in request.files:
            return jsonify({'success': False,
                            'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False,
                            'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False,
                            'error': 'Invalid file type. Use JSON, PDF, or TXT'}), 400

        # ── Save file ────────────────────────────────────────────────
        filename    = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        # ── Optional metadata from form ──────────────────────────────
        gender = request.form.get('gender') or None
        age    = request.form.get('age')
        age    = int(age) if age and age.isdigit() else None

        # ── Run pipeline ─────────────────────────────────────────────
        orchestrator = get_orchestrator()
        report       = orchestrator.process_report(upload_path, gender, age)

        # ── Generate HTML report ─────────────────────────────────────
        report_gen  = get_report_generator()
        report_id   = report['metadata'].get('report_id', 'report')
        html_path   = os.path.join(app.config['OUTPUT_FOLDER'],
                                   f'{report_id}_report.html')
        json_path   = os.path.join(app.config['OUTPUT_FOLDER'],
                                   f'{report_id}_data.json')

        report_gen.generate_html_report(report, html_path)
        orchestrator.save_report(report, json_path)

        # ── Build summary for frontend ────────────────────────────────
        param_summary = report.get('parameter_summary', {})
        pattern_count = len(report.get('pattern_analysis', {}).get('patterns', []))
        rec_count     = sum(
            len(v) for v in report.get('recommendations', {}).values()
            if isinstance(v, list)
        )

        return jsonify({
            'success':        True,
            'report_id':      report_id,
            'overall_status': report.get('overall_status', 'unknown'),
            'summary': {
                'total_parameters': param_summary.get('total_parameters', 0),
                'normal':           param_summary.get('normal', 0),
                'abnormal':         param_summary.get('abnormal', 0),
                'borderline':       param_summary.get('borderline', 0),
                'critical':         param_summary.get('critical', 0),
                'patterns_found':   pattern_count,
                'recommendations':  rec_count,
                'processing_time':  report['metadata'].get('processing_time', 0)
            },
            'html_report':    f'/view_report/{report_id}',
            'download_json':  f'/download/{report_id}'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── View HTML report ──────────────────────────────────────────────────
@app.route('/view_report/<report_id>')
def view_report(report_id):
    html_path = os.path.join(app.config['OUTPUT_FOLDER'],
                             f'{report_id}_report.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    return 'Report not found', 404


# ── Download JSON ─────────────────────────────────────────────────────
@app.route('/download/<report_id>')
def download_report(report_id):
    json_path = os.path.join(app.config['OUTPUT_FOLDER'],
                             f'{report_id}_data.json')
    if os.path.exists(json_path):
        return send_file(json_path, as_attachment=True,
                         download_name=f'{report_id}_analysis.json')
    return 'File not found', 404


# ── Sample report ─────────────────────────────────────────────────────
@app.route('/sample')
def sample_report():
    sample_path = BASE_DIR / 'data' / 'raw' / 'report_015.json'
    if not sample_path.exists():
        return jsonify({'success': False,
                        'error': 'Sample data not found. Run create_dataset.py first.'})
    try:
        orchestrator = get_orchestrator()
        report       = orchestrator.process_report(str(sample_path))
        report_gen   = get_report_generator()
        html_path    = os.path.join(app.config['OUTPUT_FOLDER'],
                                    'sample_report.html')
        report_gen.generate_html_report(report, html_path)
        return redirect('/view_report/sample')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ── Health check ──────────────────────────────────────────────────────
@app.route('/health')
def health_check():
    return jsonify({
        'status':  'running',
        'version': '1.0.0',
        'message': 'Health Diagnostics AI is operational'
    })


# ── Stats ─────────────────────────────────────────────────────────────
@app.route('/stats')
def get_stats():
    try:
        stats = get_orchestrator().get_workflow_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("="*60)
    print("  Health Diagnostics AI - Web Interface")
    print("="*60)
    print("  Open your browser and go to: http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)