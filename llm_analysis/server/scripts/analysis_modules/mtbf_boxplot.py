import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from .utils import safe_convert_timezone
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

def analyze_mtbf_boxplot(start_date, end_date, selected_services):
    """
    Create horizontal box plot showing MTBF distribution by service
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

        # Calculate MTBF for each service
        mtbf_data = {}
        for service in services_to_analyze:
            service_df = df[df[service] == 1].copy()
            service_df = service_df.sort_values('investigating_timestamp')
            service_df.loc[:, 'MTBF'] = (service_df['investigating_timestamp'].diff()
                                        .dt.total_seconds() / (24 * 3600))  # Convert to days
            mtbf_data[service] = service_df['MTBF'].dropna()

        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Convert data to DataFrame for boxplot
        df_mtbf = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in mtbf_data.items()]))
        
        # Create boxplot
        flierprops = dict(marker='D', markersize=3)
        sns.boxplot(data=df_mtbf, orient='h', ax=ax, color='white', 
                   linewidth=2, flierprops=flierprops)
        
        # Customize boxplot appearance
        for patch in ax.artists:
            patch.set_edgecolor('black')
            patch.set_linewidth(2)
        
        # Add median values
        for i, service in enumerate(services_to_analyze):
            x = mtbf_data[service].median()
            ax.text(x, i, f'{x:.2f}', color='black', va='center', ha='center', fontsize=12)

        # Add reference lines
        thresholds = [1, 7, 30]  # in days
        labels = ['1d', '7d', '30d']
        for threshold, label in zip(thresholds, labels):
            ax.axvline(x=threshold, color='black', linestyle='--', linewidth=1)
            ax.text(threshold, -0.5, label, color='black', fontsize=12, ha='center', va='top')

        # Customize plot
        ax.set_yticks(range(len(services_to_analyze)))
        ax.set_yticklabels([s.replace('_', ' ') for s in services_to_analyze], fontsize=12)
        ax.set_xlabel('MTBF [days]', fontsize=14)
        ax.grid(axis='both', linestyle='--', alpha=0.6, which='both')
        ax.set_xscale('log')
        plt.title('MTBF Distribution by Service', pad=20)

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in MTBF boxplot analysis: {str(e)}")
        raise 