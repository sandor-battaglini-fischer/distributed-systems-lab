from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
from scripts.analysis import (
    generate_monthly_overview,
    generate_failure_recovery,
    generate_status_combinations,
    generate_resolution_activities,
    generate_mttr_distribution,
    generate_mtbf_distribution,
    generate_mttr_provider,
    generate_mtbf_provider,
    generate_temporal_distribution,
    generate_autocorrelations,
    generate_daily_availability,
    generate_cooccurrence_matrix,
    generate_conditional_probability
)

app = Flask(__name__)
CORS(app)

# Ensure plots directory exists
PLOTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'plots')
os.makedirs(PLOTS_DIR, exist_ok=True)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    selected_services = data.get('selectedServices')

    try:
        plots = {
            'figure1': generate_monthly_overview(start_date, end_date, selected_services),
            'figure2': generate_failure_recovery(start_date, end_date, selected_services),
            'figure3': generate_status_combinations(start_date, end_date, selected_services),
            'figure4': generate_resolution_activities(start_date, end_date, selected_services),
            'figure5': generate_mttr_distribution(start_date, end_date, selected_services),
            'figure6': generate_mtbf_distribution(start_date, end_date, selected_services),
            'figure7': generate_mttr_provider(start_date, end_date, selected_services),
            'figure8': generate_mtbf_provider(start_date, end_date, selected_services),
            'figure9': generate_temporal_distribution(start_date, end_date, selected_services),
            'figure10': generate_autocorrelations(start_date, end_date, selected_services),
            'figure11': generate_daily_availability(start_date, end_date, selected_services),
            'figure12': generate_cooccurrence_matrix(start_date, end_date, selected_services),
            'figure13': generate_conditional_probability(start_date, end_date, selected_services)
        }
        
        return jsonify({
            'success': True,
            'message': 'Analysis complete',
            'plots': plots
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/static/plots/<path:filename>')
def serve_plot(filename):
    return send_file(os.path.join(PLOTS_DIR, filename))

if __name__ == '__main__':
    app.run(debug=True)