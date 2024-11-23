import matplotlib.pyplot as plt
import seaborn as sns
import os
from .analysis_modules.failure_recovery import analyze_failure_recovery

PLOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'plots')

def save_plot(fig, filename):
    """Helper function to save plots with consistent formatting"""
    plt.savefig(os.path.join(PLOTS_DIR, filename), bbox_inches='tight', dpi=300)
    plt.close(fig)
    return f'/static/plots/{filename}'

def generate_monthly_overview(start_date, end_date, services):
    """Generate monthly overview of visits, incidents and outages"""
    fig, ax = plt.subplots(figsize=(12, 6))
    # Dummy plot

    return save_plot(fig, 'figure1.png')

def generate_failure_recovery(start_date, end_date, services):
    """Generate failure recovery model analysis"""
    fig = analyze_failure_recovery(start_date, end_date, services)
    return save_plot(fig, 'figure2.png')

def generate_status_combinations(start_date, end_date, services):
    """Generate status combinations analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure3.png')

def generate_resolution_activities(start_date, end_date, services):
    """Generate resolution activities analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure4.png')

def generate_mttr_distribution(start_date, end_date, services):
    """Generate MTTR distribution analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure5.png')

def generate_mtbf_distribution(start_date, end_date, services):
    """Generate MTBF distribution analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure6.png')

def generate_mttr_provider(start_date, end_date, services):
    """Generate MTTR per provider analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure7.png')

def generate_mtbf_provider(start_date, end_date, services):
    """Generate MTBF per provider analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure8.png')

def generate_temporal_distribution(start_date, end_date, services):
    """Generate temporal distribution analysis"""
    fig, ax = plt.subplots(figsize=(12, 6))

    return save_plot(fig, 'figure9.png')

def generate_autocorrelations(start_date, end_date, services):
    """Generate autocorrelations analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure10.png')

def generate_daily_availability(start_date, end_date, services):
    """Generate daily availability analysis"""
    fig, ax = plt.subplots(figsize=(8, 6))

    return save_plot(fig, 'figure11.png')

def generate_cooccurrence_matrix(start_date, end_date, services):
    """Generate co-occurrence matrix"""
    fig, ax = plt.subplots(figsize=(12, 8))

    return save_plot(fig, 'figure12.png')

def generate_conditional_probability(start_date, end_date, services):
    """Generate conditional probability matrix"""
    fig, ax = plt.subplots(figsize=(12, 8))

    return save_plot(fig, 'figure13.png') 