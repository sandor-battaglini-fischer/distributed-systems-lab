from flask import Flask, jsonify, request, send_file, send_from_directory
import os
import logging
from scripts.analysis import (
    generate_failure_recovery,
    generate_monthly_overview,
    generate_status_combinations,
    cleanup_old_plots,
    generate_mttr_distribution,
    generate_mtbf_distribution,
    generate_resolution_activities,
    generate_temporal_distribution,
    generate_daily_availability,
    generate_cooccurrence_matrix,
    generate_mttr_boxplot,
    generate_mtbf_boxplot,
    generate_mttr_provider,
    generate_mtbf_provider
)
from werkzeug.exceptions import HTTPException
import traceback
from werkzeug.serving import WSGIRequestHandler
from werkzeug.middleware.proxy_fix import ProxyFix
from scripts.analysis_modules.failure_reasons import analyze_failure_reasons
import pandas as pd
from routes.incidents import incidents_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress matplotlib debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING) 

# Increase timeout for WSGI server
WSGIRequestHandler.protocol_version = "HTTP/1.1"

app = Flask(__name__, static_folder='../client/build', static_url_path='')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config.update(
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max-limit
    SEND_FILE_MAX_AGE_DEFAULT=0,  # Disable caching for development
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    HOST='0.0.0.0',
    TIMEOUT=300,  # 5 minutes timeout
    SERVER_NAME=None,  # Allow all host headers
    PREFERRED_URL_SCHEME='http',
    PROPAGATE_EXCEPTIONS=True,
)

# Ensure plots directory exists
PLOTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'plots')
os.makedirs(PLOTS_DIR, exist_ok=True)

# Add near the top of the file, after imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# For example, if you have something like:
# scripts_dir = "scripts"
# Update to:
scripts_dir = os.path.join(BASE_DIR, "scripts")

app.register_blueprint(incidents_bp)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        logger.debug('Received request: %s', request.data)
        data = request.get_json()
        if not data:
            logger.error('No data provided')
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        start_date = data.get('startDate')
        end_date = data.get('endDate')
        selected_services = data.get('selectedServices')

        if not all([start_date, end_date, selected_services]):
            logger.error('Missing required fields')
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400


        plots = {}
        try:
            cleanup_old_plots()

            # Days of Week Distribution (figure1)
            days_distribution_path = generate_monthly_overview(start_date, end_date, selected_services)
            if days_distribution_path:
                plots['figure1'] = days_distribution_path
            
            # MTTR Analysis (figure2)
            mttr_analysis_path = generate_mttr_distribution(start_date, end_date, selected_services)
            if mttr_analysis_path:
                plots['figure2'] = mttr_analysis_path
            
            # MTTR by Provider (figure3)
            mttr_provider_path = generate_mttr_provider(start_date, end_date, selected_services)
            if mttr_provider_path:
                plots['figure3'] = mttr_provider_path

            # MTTR Distribution (figure4)
            mttr_boxplot_path = generate_mttr_boxplot(start_date, end_date, selected_services)
            if mttr_boxplot_path:
                plots['figure4'] = mttr_boxplot_path

            # MTBF Analysis (figure5)
            mtbf_analysis_path = generate_mtbf_distribution(start_date, end_date, selected_services)
            if mtbf_analysis_path:
                plots['figure5'] = mtbf_analysis_path

            # MTBF by Provider (figure6)
            mtbf_provider_path = generate_mtbf_provider(start_date, end_date, selected_services)
            if mtbf_provider_path:
                plots['figure6'] = mtbf_provider_path

            # MTBF Distribution (figure7)
            mtbf_boxplot_path = generate_mtbf_boxplot(start_date, end_date, selected_services)
            if mtbf_boxplot_path:
                plots['figure7'] = mtbf_boxplot_path

            # Resolution Activities (figure8)
            resolution_activities_path = generate_resolution_activities(start_date, end_date, selected_services)
            if resolution_activities_path:
                plots['figure8'] = resolution_activities_path

            # Status Combinations (figure9)
            status_combinations_path = generate_status_combinations(start_date, end_date, selected_services)
            if status_combinations_path:
                plots['figure9'] = status_combinations_path

            # Service Availability (figure10)
            daily_availability_path = generate_daily_availability(start_date, end_date, selected_services)
            if daily_availability_path:
                plots['figure10'] = daily_availability_path

            # Temporal Patterns (figure11)
            temporal_patterns_path = generate_temporal_distribution(start_date, end_date, selected_services)
            if temporal_patterns_path:
                plots['figure11'] = temporal_patterns_path

            # Service Co-occurrence (figure12)
            cooccurrence_matrix_path = generate_cooccurrence_matrix(start_date, end_date, selected_services)
            if cooccurrence_matrix_path:
                plots['figure12'] = cooccurrence_matrix_path

            # Verify files exist
            for plot_name, plot_path in plots.items():
                full_path = os.path.join(os.path.dirname(__file__), plot_path.lstrip('/'))
                if not os.path.exists(full_path):
                    logger.error(f"Plot file not found: {full_path}")
                    plots.pop(plot_name)

            if not plots:
                raise ValueError("No plots were generated successfully")

        except Exception as plot_error:
            logger.exception('Error generating plots')
            return jsonify({
                'success': False,
                'error': str(plot_error),
                'details': traceback.format_exc()
            }), 500

        logger.info('Analysis complete')
        logger.debug('Generated plots: %s', plots)
        return jsonify({
            'success': True,
            'message': 'Analysis complete',
            'plots': plots
        })

    except Exception as e:
        logger.exception('Error during analysis')
        return jsonify({
            'success': False,
            'error': str(e),
            'details': traceback.format_exc()
        }), 500

# Add error handlers
@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return jsonify({
            'success': False,
            'error': e.description,
            'code': e.code
        }), e.code
        
    # Handle non-HTTP errors
    logger.exception('An error occurred')
    return jsonify({
        'success': False,
        'error': str(e),
        'details': traceback.format_exc()
    }), 500

# Serving React
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/js/<path:path>')
def serve_static_js(path):
    return send_from_directory(os.path.join(app.static_folder, 'static/js'), path)

@app.route('/static/css/<path:path>')
def serve_static_css(path):
    return send_from_directory(os.path.join(app.static_folder, 'static/css'), path)

@app.route('/static/media/<path:path>')
def serve_static_media(path):
    return send_from_directory(os.path.join(app.static_folder, 'static/media'), path)

# Catch-all route to return the React app for client-side routing
@app.route('/<path:path>')
def catch_all(path):
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Plot files
@app.route('/static/plots/<path:filename>')
def serve_plot(filename):
    try:
        return send_from_directory(PLOTS_DIR, filename, as_attachment=False)
    except Exception as e:
        logger.error(f"Error serving plot {filename}: {str(e)}")
        return jsonify({'error': 'Plot not found'}), 404

@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = app.make_default_options_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Connection'] = 'keep-alive'
    return response

@app.route('/api/analyze-failures', methods=['POST'])
def analyze_failures():
    try:
        data = request.get_json()
        query = data.get('query')
        history = data.get('history', [])
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400

        # Load the incident data
        df = pd.read_csv('static/data/incident_stages_all.csv')
        
        # Analyze failures based on the query and history
        analysis = analyze_failure_reasons(df, query=query, history=history)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.exception('Error analyzing failures')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True,
        use_reloader=True,
        use_debugger=True,
        use_evalex=True,
        passthrough_errors=False
    )