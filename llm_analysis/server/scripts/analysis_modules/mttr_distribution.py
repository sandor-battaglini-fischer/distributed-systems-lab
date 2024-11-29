import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from matplotlib.ticker import PercentFormatter
from .utils import safe_convert_timezone
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

def analyze_mttr_distribution(start_date, end_date, selected_services):
    """
    Analyze and visualize MTTR distribution across services
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
        df = safe_convert_timezone(df, ['investigating_timestamp', 'resolved_timestamp'])

        # Filter by date range
        df = df[(df['investigating_timestamp'] >= start_date) & 
                (df['investigating_timestamp'] <= end_date)]

        # Map selected services to CSV column names
        service_mapping = {
            'OpenAI:API': 'API',
            'OpenAI:ChatGPT': 'ChatGPT',
            'OpenAI:DALL-E': 'Labs',
            'OpenAI:Playground': 'Playground',
            'Anthropic:API': 'api.anthropic.com',
            'Anthropic:Claude': 'claude.ai',
            'Anthropic:Console': 'console.anthropic.com',
            'Character.AI:Character.AI': 'Character.AI'
        }

        services_to_analyze = []
        for service in selected_services:
            if service in service_mapping:
                mapped_service = service_mapping[service]
                if mapped_service in df.columns:
                    services_to_analyze.append(mapped_service)

        if not services_to_analyze:
            raise ValueError("No valid services selected for analysis")

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

        # Calculate MTTR for each service
        mttr_data = {}
        for service in services_to_analyze:
            service_df = df[df[service] == 1].copy()
            service_df.loc[:, 'MTTR'] = (service_df['resolved_timestamp'] - 
                                       service_df['investigating_timestamp']).dt.total_seconds() / 3600
            mttr_data[service] = service_df['MTTR'].dropna()

        # Plot 1: ECDF Plot
        colors = sns.color_palette('Set2', n_colors=len(services_to_analyze))
        for idx, service in enumerate(services_to_analyze):
            sns.ecdfplot(
                data=mttr_data[service],
                label=service.replace('_', ' '),
                color=colors[idx],
                linestyle='-',
                linewidth=2,
                ax=ax1
            )

        # Add vertical lines at key thresholds
        thresholds = [0.5, 1, 3, 10, 24]  # in hours
        labels = ['30m', '1h', '3h', '10h', '24h']
        for threshold, label in zip(thresholds, labels):
            ax1.axvline(x=threshold, color='gray', linestyle='--', alpha=0.5)
            ax1.text(threshold, 1.01, label, rotation=0, ha='center', va='bottom')

        ax1.set_xlabel('MTTR [hours]')
        ax1.set_ylabel('ECDF')
        ax1.set_xscale('log')
        ax1.grid(True, which='both', linestyle='--', alpha=0.7)
        ax1.legend(title='Service', bbox_to_anchor=(1.05, 1))

        # Plot 2: Percentage Distribution
        # Calculate percentages for each threshold
        percent_data = []
        for service in services_to_analyze:
            service_data = {'Service': service}
            mttr_series = mttr_data[service]
            for threshold in thresholds:
                percent = (mttr_series <= threshold).mean() * 100
                service_data[f'≤{threshold}h'] = percent
            service_data['>24h'] = (mttr_series > 24).mean() * 100
            percent_data.append(service_data)

        df_percent = pd.DataFrame(percent_data)
        
        # Create stacked bar plot
        df_percent.plot(
            x='Service',
            y=[f'≤{t}h' for t in thresholds] + ['>24h'],
            kind='bar',
            stacked=True,
            ax=ax2,
            colormap='Set3'
        )

        ax2.set_xlabel('Service')
        ax2.set_ylabel('Percentage of Incidents')
        ax2.legend(title='MTTR Duration', bbox_to_anchor=(1.05, 1))
        ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in MTTR distribution analysis: {str(e)}")
        raise