import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import (
    load_and_prepare_data,
    get_services_to_analyze,
    setup_plotting_style,
    safe_to_period
)

def analyze_temporal_distribution(start_date, end_date, selected_services):
    """
    Analyze and visualize temporal distribution of incidents
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=['investigating_timestamp']
        )
        
        # Get services to analyze
        services_to_analyze = get_services_to_analyze(selected_services)
        
        # Setup plotting style
        setup_plotting_style()

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))

        # Plot 1: Monthly trend
        for service in services_to_analyze:
            service_df = df[df[service] == 1].copy()
            service_df['Month'] = safe_to_period(service_df['investigating_timestamp'])
            monthly_counts = service_df.groupby('Month').size()
            
            # Calculate moving average
            ma = monthly_counts.rolling(window=3, min_periods=1).mean()
            
            # Plot both actual counts and moving average
            ax1.plot(range(len(monthly_counts)), monthly_counts, 
                    'o-', alpha=0.5, label=f'{service.replace("_", " ")} (Actual)')
            ax1.plot(range(len(ma)), ma, 
                    '--', linewidth=2, label=f'{service.replace("_", " ")} (3-month MA)')

        ax1.set_title('Monthly Incident Trends')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Number of Incidents')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Plot 2: Hourly distribution
        for service in services_to_analyze:
            service_df = df[df[service] == 1].copy()
            service_df['Hour'] = service_df['investigating_timestamp'].dt.hour
            hourly_counts = service_df.groupby('Hour').size()
            
            # Calculate percentage of total incidents
            hourly_pct = (hourly_counts / hourly_counts.sum()) * 100
            
            # Plot hourly distribution
            ax2.plot(hourly_pct.index, hourly_pct, 
                    'o-', label=service.replace('_', ' '),
                    markersize=6)

        # Add reference lines for business hours
        business_hours = [9, 17]  # 9 AM to 5 PM
        for hour in business_hours:
            ax2.axvline(x=hour, color='gray', linestyle='--', alpha=0.5)
            ax2.text(hour, ax2.get_ylim()[1], f'{hour:02d}:00',
                    rotation=0, ha='center', va='bottom')

        ax2.set_title('Hourly Incident Distribution')
        ax2.set_xlabel('Hour (UTC)')
        ax2.set_ylabel('Percentage of Incidents')
        ax2.set_xticks(range(0, 24, 2))
        ax2.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in temporal distribution analysis: {str(e)}")
        raise 