import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from .utils import safe_convert_timezone
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

def analyze_mtbf_provider(start_date, end_date, selected_services):
    """
    Analyze and visualize MTBF distribution across providers
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
        df = safe_convert_timezone(df, ['investigating_timestamp', 'start_timestamp'])

        # Filter by date range
        df = df[(df['investigating_timestamp'] >= start_date) & 
                (df['investigating_timestamp'] <= end_date)]

        # Group by provider
        provider_list = ['openai', 'anthropic', 'character']
        dfs_provider = {}
        dfs_provider_mtbf = {}

        for provider in provider_list:
            provider_df = df[df['provider'] == provider].copy()
            provider_df = provider_df.sort_values('investigating_timestamp')
            provider_df.loc[:, 'MTBF'] = (provider_df['investigating_timestamp'].diff()
                                         .dt.total_seconds() / (24 * 3600))  # Convert to days
            dfs_provider_mtbf[provider] = provider_df['MTBF'].dropna()
            dfs_provider[provider] = provider_df

        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot ECDF for each provider
        colors = sns.color_palette('bright', n_colors=len(provider_list))
        markers = ['^', 'o', 's']
        
        for idx, provider in enumerate(provider_list):
            if not dfs_provider_mtbf[provider].empty:
                sns.ecdfplot(
                    data=dfs_provider_mtbf[provider],
                    label=provider.capitalize(),
                    color=colors[idx],
                    linestyle='-',
                    linewidth=2
                )

        # Add reference lines
        thresholds = [1, 7, 30]  # in days
        labels = ['1d', '7d', '30d']
        for threshold, label in zip(thresholds, labels):
            ax.axvline(x=threshold, color='gray', linestyle='--', alpha=0.5)
            ax.text(threshold, 1.08, label, color='black', fontsize=12, ha='center', va='top')

        ax.set_xlabel('MTBF [days]')
        ax.set_ylabel('ECDF')
        ax.set_xscale('log')
        ax.grid(True, which='both', linestyle='--', alpha=0.7)
        ax.legend(title='Provider', bbox_to_anchor=(1.05, 1))

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in MTBF provider analysis: {str(e)}")
        raise 