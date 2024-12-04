import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import (
    load_and_prepare_data,
    get_services_to_analyze,
    setup_plotting_style
)

def analyze_daily_availability(start_date, end_date, selected_services):
    """
    Analyze and visualize daily service availability patterns
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=[
                'investigating_timestamp', 'resolved_timestamp'
            ]
        )
        
        # Get services to analyze
        services_to_analyze = get_services_to_analyze(selected_services)
        
        # Setup plotting style
        setup_plotting_style()

        # Create figure
        fig, ax = plt.subplots(figsize=(15, 8))

        # Calculate daily availability for each service
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        availability_data = {}

        for service in services_to_analyze:
            service_df = df[df[service] == 1].copy()
            daily_incidents = service_df.groupby(
                service_df['investigating_timestamp'].dt.date
            ).agg({
                'investigating_timestamp': 'count',
                'resolved_timestamp': lambda x: (x - service_df.loc[x.index, 'investigating_timestamp']).dt.total_seconds().sum() / 3600
            })

            # Calculate availability percentage
            availability = []
            for date in date_range:
                date_str = date.date()
                if date_str in daily_incidents.index:
                    # Calculate downtime based on incident count and duration
                    incident_count = daily_incidents.loc[date_str, 'investigating_timestamp']
                    incident_hours = daily_incidents.loc[date_str, 'resolved_timestamp']
                    downtime_percentage = min(incident_hours / 24 * 100, 100)  # Cap at 100%
                    availability.append(100 - downtime_percentage)
                else:
                    availability.append(100)
            
            availability_data[service] = availability

        # Plot availability lines
        colors = sns.color_palette('Set2', n_colors=len(services_to_analyze))
        for idx, (service, avail) in enumerate(availability_data.items()):
            plt.plot(date_range, avail, 
                    label=service.replace('_', ' '), 
                    color=colors[idx],
                    marker='o', 
                    markersize=4,
                    alpha=0.8)

        # Add reference lines for common SLA levels
        sla_levels = [99.9, 99.99, 99.999]
        sla_colors = ['red', 'orange', 'green']
        sla_labels = ['99.9%', '99.99%', '99.999%']
        
        for level, color, label in zip(sla_levels, sla_colors, sla_labels):
            plt.axhline(y=level, color=color, linestyle='--', alpha=0.5)
            plt.text(plt.xlim()[1], level, f' {label}', 
                    va='center', ha='left', color=color)

        # Customize plot
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlabel('Date')
        plt.ylabel('Availability (%)')
        plt.title('Daily Service Availability')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)

        # Set y-axis limits to focus on high availability range
        plt.ylim(99, 100.1)

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in daily availability analysis: {str(e)}")
        raise 