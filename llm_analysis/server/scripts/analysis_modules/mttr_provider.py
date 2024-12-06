import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import (
    load_and_prepare_data,
    get_services_to_analyze,
    setup_plotting_style
)

def analyze_mttr_provider(start_date, end_date, selected_services):
    """
    Analyze and visualize MTTR distribution across providers
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=['investigating_timestamp', 'resolved_timestamp', 'start_timestamp', 'close_timestamp']
        )
        
        # Setup plotting style
        setup_plotting_style()

        # Group by provider
        provider_list = ['openai', 'anthropic', 'character']
        dfs_provider = {}
        dfs_provider_mttr = {}

        for provider in provider_list:
            provider_df = df[df['provider'] == provider].copy()
            provider_df = provider_df.sort_values('investigating_timestamp')
            provider_df.loc[:, 'MTTR'] = (provider_df['resolved_timestamp'] - 
                                        provider_df['investigating_timestamp']).dt.total_seconds() / 3600
            dfs_provider_mttr[provider] = provider_df['MTTR'].dropna()
            dfs_provider[provider] = provider_df

        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot ECDF for each provider
        colors = sns.color_palette('bright', n_colors=len(provider_list))
        
        for idx, provider in enumerate(provider_list):
            if not dfs_provider_mttr[provider].empty:
                sns.ecdfplot(
                    data=dfs_provider_mttr[provider],
                    label=provider.capitalize(),
                    color=colors[idx],
                    linestyle='-',
                    linewidth=2
                )

        # Add reference lines
        thresholds = [10/60, 0.5, 3, 10, 24]  # in hours
        labels = ['10m', '30m', '3h', '10h', '24h']
        for threshold, label in zip(thresholds, labels):
            ax.axvline(x=threshold, color='gray', linestyle='--', alpha=0.5)
            ax.text(threshold, 1.08, label, color='black', fontsize=12, ha='center', va='top')

        ax.set_xlabel('MTTR [hours]')
        ax.set_ylabel('ECDF')
        ax.set_xscale('log')
        ax.grid(True, which='both', linestyle='--', alpha=0.7)
        ax.legend(title='Provider', bbox_to_anchor=(1.05, 1))

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in MTTR provider analysis: {str(e)}")
        raise 