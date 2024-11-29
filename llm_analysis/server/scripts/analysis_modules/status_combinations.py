import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def analyze_status_combinations(start_date, end_date, selected_services):
    """
    Analyze and visualize status combinations patterns
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

        # Calculate status combinations for each service
        service_combinations = {}
        for service in services_to_analyze:
            service_data = df[df[service] == 1]
            combinations = service_data[['investigating_flag', 'identified_flag', 
                                      'monitoring_flag', 'resolved_flag', 
                                      'postmortem_flag']].value_counts()
            total = combinations.sum()
            if total > 0:
                service_combinations[service] = (combinations / total).to_dict()

        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data for stacked bar chart
        all_combinations = sorted(list(set().union(*[set(d.keys()) for d in service_combinations.values()])))
        data = []
        for service in services_to_analyze:
            service_data = service_combinations[service]
            data.append([service_data.get(comb, 0) for comb in all_combinations])

        # Create stacked bar chart
        bottom = np.zeros(len(services_to_analyze))
        colors = sns.color_palette("husl", n_colors=len(all_combinations))
        
        for i, combination in enumerate(all_combinations):
            values = [row[i] for row in data]
            ax.bar(services_to_analyze, values, bottom=bottom, 
                  label=f"Status {i+1}", color=colors[i])
            bottom += values

        ax.set_xlabel('Service', fontsize=12)
        ax.set_ylabel('Percentage of Incidents', fontsize=12)
        ax.set_title('Status Combination Patterns by Service', fontsize=14, pad=20)
        ax.legend(title='Status Combinations', bbox_to_anchor=(1.05, 1.0))
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        return fig

    except Exception as e:
        print(f"Error in status combinations analysis: {str(e)}")
        raise 