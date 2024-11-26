import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
from datetime import datetime
import pandas as pd
from .analysis_modules.monthly_overview import analyze_monthly_overview
from .analysis_modules.failure_recovery import analyze_failure_recovery
from .analysis_modules.status_combinations import analyze_status_combinations
from .analysis_modules.mttr_distribution import analyze_mttr_distribution
from .analysis_modules.mtbf_distribution import analyze_mtbf_distribution
from .analysis_modules.resolution_activities import analyze_resolution_activities
from .analysis_modules.temporal_distribution import analyze_temporal_distribution
from .analysis_modules.daily_availability import analyze_daily_availability
from .analysis_modules.cooccurrence_matrix import analyze_cooccurrence_matrix
from .analysis_modules.mttr_boxplot import analyze_mttr_boxplot
from .analysis_modules.mtbf_boxplot import analyze_mtbf_boxplot
from .analysis_modules.mttr_provider import analyze_mttr_provider
from .analysis_modules.mtbf_provider import analyze_mtbf_provider

PLOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'plots')

def save_plot(fig, plot_type, start_date, end_date, services):
    """Helper function to save plots with consistent formatting and unique names"""
    # Format dates for filename
    start_str = pd.to_datetime(start_date).strftime('%Y%m%d')
    end_str = pd.to_datetime(end_date).strftime('%Y%m%d')
    
    # Create more descriptive service string for filename
    service_names = []
    for service in services:
        provider, name = service.split(':')
        if provider == 'OpenAI':
            service_names.append(f'OpenAI_{name}')
        elif provider == 'Anthropic':
            if name == 'API':
                service_names.append('Anthropic_API')
            elif name == 'Claude':
                service_names.append('Anthropic_Claude')
            elif name == 'Console':
                service_names.append('Anthropic_Console')
        elif provider == 'Character.AI':
            service_names.append('CharacterAI')
        elif provider == 'Stability AI':
            service_names.append('StabilityAI')
        elif provider == 'Google':
            service_names.append(f'Google_{name}')
    
    service_str = '-'.join(service_names)
    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime('%H%M%S')
    filename = f'{plot_type}_{start_str}_{end_str}__{service_str}__{timestamp}.png'
    
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
    """Generate monthly overview of incidents"""
    try:
        cleanup_old_plots()
        fig = analyze_monthly_overview(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'monthly_overview', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating monthly overview: {e}")
        return None

def generate_failure_recovery(start_date, end_date, services):
    """Generate failure recovery model analysis"""
    try:
        cleanup_old_plots()
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
        fig = analyze_status_combinations(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'status_combinations', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating status combinations: {e}")
        return None

def generate_resolution_activities(start_date, end_date, services):
    """Generate resolution activities analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_resolution_activities(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'resolution_activities', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating resolution activities: {e}")
        return None

def generate_mttr_distribution(start_date, end_date, services):
    """Generate MTTR distribution analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_mttr_distribution(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'mttr_distribution', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating MTTR distribution: {e}")
        return None

def generate_mtbf_distribution(start_date, end_date, services):
    """Generate MTBF distribution analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_mtbf_distribution(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'mtbf_distribution', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating MTBF distribution: {e}")
        return None

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
    try:
        cleanup_old_plots()
        fig = analyze_temporal_distribution(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'temporal_distribution', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating temporal distribution: {e}")
        return None

def generate_autocorrelations(start_date, end_date, services):
    """Generate autocorrelations analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure10.png', start_date, end_date, services)

def generate_daily_availability(start_date, end_date, services):
    """Generate daily availability analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_daily_availability(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'daily_availability', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating daily availability: {e}")
        return None

def generate_cooccurrence_matrix(start_date, end_date, services):
    """Generate co-occurrence matrix analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_cooccurrence_matrix(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'cooccurrence_matrix', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating co-occurrence matrix: {e}")
        return None

def generate_all_plots(start_date, end_date, services):
    """Generate all analysis plots"""
    plots = {}
    
    try:
        # Monthly Overview
        monthly_overview_path = generate_monthly_overview(start_date, end_date, services)
        if monthly_overview_path:
            plots['figure1'] = monthly_overview_path

        # MTTR Analysis
        mttr_distribution_path = generate_mttr_distribution(start_date, end_date, services)
        if mttr_distribution_path:
            plots['figure2'] = mttr_distribution_path

        # MTTR by Provider
        mttr_provider_path = generate_mttr_provider(start_date, end_date, services)
        if mttr_provider_path:
            plots['figure3'] = mttr_provider_path

        # MTTR Distribution (Boxplot)
        mttr_boxplot_path = generate_mttr_boxplot(start_date, end_date, services)
        if mttr_boxplot_path:
            plots['figure4'] = mttr_boxplot_path

        # MTBF Analysis
        mtbf_distribution_path = generate_mtbf_distribution(start_date, end_date, services)
        if mtbf_distribution_path:
            plots['figure5'] = mtbf_distribution_path

        # MTBF by Provider
        mtbf_provider_path = generate_mtbf_provider(start_date, end_date, services)
        if mtbf_provider_path:
            plots['figure6'] = mtbf_provider_path

        # MTBF Distribution (Boxplot)
        mtbf_boxplot_path = generate_mtbf_boxplot(start_date, end_date, services)
        if mtbf_boxplot_path:
            plots['figure7'] = mtbf_boxplot_path

        # Resolution Activities
        resolution_activities_path = generate_resolution_activities(start_date, end_date, services)
        if resolution_activities_path:
            plots['figure8'] = resolution_activities_path

        # Status Combinations
        status_combinations_path = generate_status_combinations(start_date, end_date, services)
        if status_combinations_path:
            plots['figure9'] = status_combinations_path

        # Service Availability
        daily_availability_path = generate_daily_availability(start_date, end_date, services)
        if daily_availability_path:
            plots['figure10'] = daily_availability_path

        # Temporal Patterns
        temporal_distribution_path = generate_temporal_distribution(start_date, end_date, services)
        if temporal_distribution_path:
            plots['figure11'] = temporal_distribution_path

        # Service Co-occurrence
        cooccurrence_matrix_path = generate_cooccurrence_matrix(start_date, end_date, services)
        if cooccurrence_matrix_path:
            plots['figure12'] = cooccurrence_matrix_path

        return plots

    except Exception as e:
        print(f"Error generating plots: {e}")
        return plots

# Add individual generate functions for each plot type
def generate_mttr_boxplot(start_date, end_date, services):
    """Generate MTTR boxplot analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_mttr_boxplot(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'mttr_boxplot', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating MTTR boxplot: {e}")
        return None

def generate_mtbf_boxplot(start_date, end_date, services):
    """Generate MTBF boxplot analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_mtbf_boxplot(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'mtbf_boxplot', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating MTBF boxplot: {e}")
        return None

def generate_mttr_provider(start_date, end_date, services):
    """Generate MTTR provider analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_mttr_provider(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'mttr_provider', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating MTTR provider analysis: {e}")
        return None

def generate_mtbf_provider(start_date, end_date, services):
    """Generate MTBF provider analysis"""
    try:
        cleanup_old_plots()
        fig = analyze_mtbf_provider(start_date, end_date, services)
        if fig:
            return save_plot(fig, 'mtbf_provider', start_date, end_date, services)
        return None
    except Exception as e:
        print(f"Error generating MTBF provider analysis: {e}")
        return None

# Ensure plots directory exists when module is imported
os.makedirs(PLOTS_DIR, exist_ok=True) 