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

def analyze_daily_overview(start_date, end_date, selected_services):
    """
    Generate daily overview analysis showing incident counts by hour of the day.

    Args:
        start_date (datetime): Start date for filtering data.
        end_date (datetime): End date for filtering data.
        selected_services (list): List of services to analyze.

    Returns:
        fig (matplotlib.figure.Figure): The figure object with the plots.
    """
    try:
        # Load and prepare data
        timestamp_columns = [f'{status}_timestamp' for status in 
                            ['investigating', 'identified', 'monitoring', 
                             'resolved', 'postmortem']] + ['start_timestamp', 'close_timestamp']
        
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=timestamp_columns
        )
        
        # Get services to analyze
        services_to_analyze = get_services_to_analyze(selected_services)
        
        # Setup plotting style
        setup_plotting_style()

        # Create provider groupings
        provider_services = {
            'OpenAI': [],
            'Anthropic': [],
            'Character.AI': [],
            'StabilityAI': []
        }

        service_mapping = get_service_mapping()
        for service_id in selected_services:
            try:
                provider, _ = service_id.split(':')
                if service_id in service_mapping:
                    provider_services[provider].append(service_mapping[service_id])
                else:
                    print(f"Warning: Service ID '{service_id}' not found in service mapping.")
            except ValueError:
                print(f"Warning: Service ID '{service_id}' is not in the expected 'Provider:Service' format.")

        # Initialize subplots
        num_providers = len(provider_services)
        fig, axs = plt.subplots(1, num_providers, figsize=(5 * num_providers, 8), sharey=True)
        if num_providers == 1:
            axs = [axs]

        # Define color palettes for each provider
        provider_colors = {
            'OpenAI': 'Blues',
            'Anthropic': 'Oranges',
            'Character.AI': 'Greens',
            'StabilityAI': 'Reds'
        }

        for idx, (provider, services) in enumerate(provider_services.items()):
            if not services:
                axs[idx].text(0.5, 0.5, 'No Services Selected', horizontalalignment='center',
                              verticalalignment='center', fontsize=12, color='gray')
                axs[idx].set_title(provider, fontsize=14, pad=20)
                axs[idx].set_xlabel('Hour of Day', fontsize=12)
                continue

            provider_df = df[df[services].any(axis=1)].copy()
            if provider_df.empty:
                axs[idx].text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                              verticalalignment='center', fontsize=12, color='gray')
                axs[idx].set_title(provider, fontsize=14, pad=20)
                axs[idx].set_xlabel('Hour of Day', fontsize=12)
                continue

            # Extract hour from 'investigating_timestamp'
            provider_df['Hour'] = provider_df['investigating_timestamp'].dt.hour
            provider_df['Hour'] = pd.Categorical(
                provider_df['Hour'],
                categories=range(0, 24),
                ordered=True
            )

            # Count incidents by hour and service
            hour_counts = pd.DataFrame()
            for service in services:
                # Use safe_groupby for counting incidents
                service_counts = safe_groupby(
                    provider_df[provider_df[service] == 1], 
                    'Hour'
                ).size()
                hour_counts[service] = service_counts

            hour_counts = hour_counts.fillna(0).astype(int)

            # Plot stacked bar chart
            colors = sns.color_palette(provider_colors[provider], len(services))
            hour_counts.plot(kind='bar', stacked=True, ax=axs[idx], color=colors, edgecolor='black')

            axs[idx].set_title(provider, fontsize=14, pad=20)
            axs[idx].set_xlabel('Hour of Day', fontsize=12)
            axs[idx].set_ylabel('Incident Count' if idx == 0 else '')
            axs[idx].set_xticklabels(hour_counts.index, rotation=0)
            axs[idx].grid(axis='y', linestyle='--', alpha=0.7)
            axs[idx].legend(title='Services', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in daily overview analysis: {str(e)}")
        raise
