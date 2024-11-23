from flask import Flask, jsonify, request, send_file, send_from_directory
import os
import logging
from scripts.analysis import (
    generate_failure_recovery,
    generate_monthly_overview,
    generate_status_combinations,
    cleanup_old_plots,
)
from werkzeug.exceptions import HTTPException
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress matplotlib debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING) 

app = Flask(__name__, static_folder='../client/build', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

# Ensure plots directory exists
PLOTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'plots')
os.makedirs(PLOTS_DIR, exist_ok=True)

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

        # Generate plots
        plots = {}
        try:
            # Clean up old plots first
            cleanup_old_plots()

            # Generate failure recovery plot
            failure_recovery_path = generate_failure_recovery(start_date, end_date, selected_services)
            if failure_recovery_path:
                plots['figure2'] = failure_recovery_path
            
            # Generate other plots as needed
            monthly_overview_path = generate_monthly_overview(start_date, end_date, selected_services)
            if monthly_overview_path:
                plots['figure1'] = monthly_overview_path
            
            status_combinations_path = generate_status_combinations(start_date, end_date, selected_services)
            if status_combinations_path:
                plots['figure3'] = status_combinations_path

            # Verify that the files exist
            for plot_name, plot_path in plots.items():
                full_path = os.path.join(os.path.dirname(__file__), plot_path.lstrip('/'))
                if not os.path.exists(full_path):
                    logger.error(f"Plot file not found: {full_path}")
                    plots.pop(plot_name)  # Remove the missing plot from the response

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

# Add these routes for serving the React app
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)