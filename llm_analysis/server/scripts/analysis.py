import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
from datetime import datetime
import pandas as pd

PLOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'plots')

def save_plot(fig, plot_type, start_date, end_date, services):
    """Helper function to save plots with consistent formatting and unique names"""
    # Format dates for filename
    start_str = pd.to_datetime(start_date).strftime('%Y%m%d')
    end_str = pd.to_datetime(end_date).strftime('%Y%m%d')
    
    # Create service string for filename
    service_str = '_'.join(s.split(':')[1] for s in services)[:50]  # Limit length
    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime('%H%M%S')
    filename = f'{plot_type}_{start_str}_{end_str}_{service_str}_{timestamp}.png'
    
    # Save the plot
    plt.savefig(os.path.join(PLOTS_DIR, filename), bbox_inches='tight', dpi=300)
    plt.close(fig)
    return f'/static/plots/{filename}'

def cleanup_old_plots():
    """Remove plots older than 1 hour"""
    current_time = datetime.now()
    for filename in os.listdir(PLOTS_DIR):
        if filename.endswith('.png'):
            file_path = os.path.join(PLOTS_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if (current_time - file_time).total_seconds() > 3600:  
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to remove old plot {filename}: {e}")

def generate_monthly_overview(start_date, end_date, services):
    """Generate monthly overview of visits, incidents and outages"""
    try:
        cleanup_old_plots()
        fig, ax = plt.subplots(figsize=(12, 6))
        # Your monthly overview plot logic here
        return save_plot(fig, 'monthly_overview', start_date, end_date, services)
    except Exception as e:
        print(f"Error generating monthly overview: {e}")
        return None

def generate_failure_recovery(start_date, end_date, services):
    """Generate failure recovery model analysis"""
    try:
        cleanup_old_plots()
        from .analysis_modules.failure_recovery import analyze_failure_recovery
        fig = analyze_failure_recovery(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'failure_recovery', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating failure recovery: {e}")
        return None

def generate_status_combinations(start_date, end_date, services):
    """Generate status combinations analysis"""
    try:
        cleanup_old_plots()
        fig, ax = plt.subplots(figsize=(8, 6))
        # Your status combinations plot logic here
        return save_plot(fig, 'status_combinations', start_date, end_date, services)
    except Exception as e:
        print(f"Error generating status combinations: {e}")
        return None

def generate_resolution_activities(start_date, end_date, services):
    """Generate resolution activities analysis"""
    try:
        cleanup_old_plots()
        fig, ax = plt.subplots(figsize=(8, 6))
        # Your resolution activities plot logic here
        return save_plot(fig, 'resolution_activities', start_date, end_date, services)
    except Exception as e:
        print(f"Error generating resolution activities: {e}")
        return None

def generate_mttr_distribution(start_date, end_date, services):
    """Generate MTTR distribution analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure5.png', start_date, end_date, services)

def generate_mtbf_distribution(start_date, end_date, services):
    """Generate MTBF distribution analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure6.png', start_date, end_date, services)

def generate_mttr_provider(start_date, end_date, services):
    """Generate MTTR per provider analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure7.png', start_date, end_date, services)

def generate_mtbf_provider(start_date, end_date, services):
    """Generate MTBF per provider analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure8.png', start_date, end_date, services)

def generate_temporal_distribution(start_date, end_date, services):
    """Generate temporal distribution analysis"""
    fig, ax = plt.subplots(figsize=(12, 6))

    return save_plot(fig, 'figure9.png', start_date, end_date, services)

def generate_autocorrelations(start_date, end_date, services):
    """Generate autocorrelations analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure10.png', start_date, end_date, services)

def generate_daily_availability(start_date, end_date, services):
    """Generate daily availability analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure11.png', start_date, end_date, services)

def generate_cooccurrence_matrix(start_date, end_date, services):
    """Generate co-occurrence matrix"""
    fig, ax = plt.subplots(figsize=(12, 8))

    return save_plot(fig, 'figure12.png', start_date, end_date, services)

def generate_conditional_probability(start_date, end_date, services):
    """Generate conditional probability matrix"""
    fig, ax = plt.subplots(figsize=(12, 8))

    return save_plot(fig, 'figure13.png', start_date, end_date, services)

# Ensure plots directory exists when module is imported
os.makedirs(PLOTS_DIR, exist_ok=True) 