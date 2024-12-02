import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import (
    load_and_prepare_data,
    get_services_to_analyze,
    setup_plotting_style,
    safe_groupby,
    safe_to_period,
    get_service_mapping
)

def analyze_monthly_overview(start_date, end_date, selected_services):
    """
    Generate monthly overview analysis showing incident counts by day of week
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=[f'{status}_timestamp' for status in 
                             ['investigating', 'identified', 'monitoring', 
                              'resolved', 'postmortem']]
        )
        
        # Get services to analyze
        services_to_analyze = get_services_to_analyze(selected_services)
        
        # Setup plotting style
        setup_plotting_style()

        # Create provider groupings
        provider_services = {
            'OpenAI': [],
            'Anthropic': [],
            'Character.AI': []
        }

        service_mapping = get_service_mapping()
        for service_id in selected_services:
            provider, _ = service_id.split(':')
            if service_id in service_mapping:
                provider_services[provider].append(service_mapping[service_id])

        fig, axs = plt.subplots(1, len(provider_services), figsize=(16, 8))
        if len(provider_services) == 1:
            axs = [axs]

        provider_colors = {
            'OpenAI': 'Blues',
            'Anthropic': 'Oranges',
            'Character.AI': 'Greens'
        }

        for idx, (provider, services) in enumerate(provider_services.items()):
            if not services:
                continue

            provider_df = df[df[services].any(axis=1)].copy()
            provider_df['Day'] = provider_df['investigating_timestamp'].dt.day_name()
            provider_df['Day'] = pd.Categorical(
                provider_df['Day'],
                categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                ordered=True
            )

            # Count incidents by day and service
            day_counts = pd.DataFrame()
            for service in services:
                # Use safe_groupby for counting incidents
                service_counts = safe_groupby(
                    provider_df[provider_df[service] == 1], 
                    'Day'
                ).size()
                day_counts[service] = service_counts

            day_counts = day_counts.fillna(0)

            # Plot stacked bar chart
            colors = sns.color_palette(provider_colors[provider], len(services))
            day_counts.plot(kind='bar', stacked=True, ax=axs[idx], color=colors)
            
            axs[idx].set_title(provider, fontsize=14, pad=20)
            axs[idx].set_xlabel('')
            axs[idx].set_ylabel('Incident Count' if idx == 0 else '')
            axs[idx].tick_params(axis='x', rotation=45)
            axs[idx].grid(axis='y', linestyle='--', alpha=0.7)
            axs[idx].legend(title='Services', bbox_to_anchor=(1.05, 1))

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in monthly overview analysis: {str(e)}")
        raise 