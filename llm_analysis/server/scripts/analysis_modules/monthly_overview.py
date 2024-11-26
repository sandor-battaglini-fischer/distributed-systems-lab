import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from matplotlib.ticker import PercentFormatter
import warnings
from .utils import safe_convert_timezone, safe_groupby

warnings.filterwarnings('ignore', category=FutureWarning)

def analyze_monthly_overview(start_date, end_date, selected_services):
    """
    Generate monthly overview analysis showing incident counts by day of week
    """
    try:
        # Convert string dates to pandas datetime with UTC timezone
        start_date = pd.to_datetime(start_date).tz_localize('UTC')
        end_date = pd.to_datetime(end_date).tz_localize('UTC')

        # Read the data
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'static', 'data', 'incident_stages.csv')
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found at {data_path}")

        df = pd.read_csv(data_path)
        
        # Convert timestamps and handle timezone
        status_columns = ['investigating', 'identified', 'monitoring', 'resolved', 'postmortem']
        for status in status_columns:
            df[f'{status}_timestamp'] = pd.to_datetime(df[f'{status}_timestamp'])
            if df[f'{status}_timestamp'].dt.tz is None:
                df[f'{status}_timestamp'] = df[f'{status}_timestamp'].dt.tz_localize('UTC')
            df[f'{status}_timestamp'] = df[f'{status}_timestamp'].dt.tz_convert('US/Pacific')

        # Convert timestamps using utility function
        df = safe_convert_timezone(df, [f'{status}_timestamp' for status in status_columns])

        # Filter by date range
        df = df[(df['investigating_timestamp'] >= start_date) & 
                (df['investigating_timestamp'] <= end_date)]

        # Map selected services to CSV column names
        service_mapping = {
            'OpenAI:API': 'API',
            'OpenAI:ChatGPT': 'ChatGPT',
            'OpenAI:Labs': 'Labs',
            'OpenAI:Playground': 'Playground',
            'Anthropic:API': 'api.anthropic.com',
            'Anthropic:Claude': 'claude.ai',
            'Anthropic:Console': 'console.anthropic.com',
            'Character.AI:Character.AI': 'Character.AI'
        }

        # Create provider groupings
        provider_services = {
            'OpenAI': [],
            'Anthropic': [],
            'Character.AI': []
        }

        for service_id in selected_services:
            provider, _ = service_id.split(':')
            if service_id in service_mapping:
                provider_services[provider].append(service_mapping[service_id])

        # Create the plot
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

            # Get incidents for this provider's services
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