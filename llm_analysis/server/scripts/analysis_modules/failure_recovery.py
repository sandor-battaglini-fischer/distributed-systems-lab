import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def analyze_failure_recovery(start_date, end_date, selected_services):
    """
    Analyze failure recovery patterns and generate stacked bar plot
    """
    try:
        # Convert service IDs to service names
        service_mapping = {
            'OpenAI:API': 'API-OpenAI',
            'OpenAI:ChatGPT': 'ChatGPT',
            'OpenAI:DALL·E': 'DALL·E',
            'OpenAI:Playground': 'Playground',
            'Anthropic:API': 'API-Anthropic',
            'Anthropic:Claude': 'Claude',
            'Anthropic:Console': 'Console',
            'Character.AI:Character.AI': 'Character.AI'
        }

        services_to_analyze = [service_mapping[s] for s in selected_services if s in service_mapping]
        
        if not services_to_analyze:
            raise ValueError("No valid services selected for analysis")

        # Load data from the static directory
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'static', 'data', 'incident_stages.csv')
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found at {data_path}")

        df = pd.read_csv(data_path)

        # Convert timestamps
        status_columns = ['investigating', 'identified', 'monitoring', 'resolved', 'postmortem']
        for status in status_columns:
            df[f'{status}_timestamp'] = pd.to_datetime(df[f'{status}_timestamp'])

        # Filter by date range
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df['investigating_timestamp'] >= start_date) & 
                (df['postmortem_timestamp'] <= end_date)]

        # Filter invalid sequences
        valid_indices = (
            (df['investigating_timestamp'] <= df['identified_timestamp']) &
            (df['identified_timestamp'] <= df['monitoring_timestamp']) &
            (df['monitoring_timestamp'] <= df['resolved_timestamp']) &
            (df['resolved_timestamp'] <= df['postmortem_timestamp'])
        )
        df = df[valid_indices]

        # Calculate status combinations
        def get_status_combination(row):
            flags = []
            if row['investigating_flag']: flags.append('S1')
            if row['identified_flag']: flags.append('S2')
            if row['monitoring_flag']: flags.append('S3')
            if row['resolved_flag']: flags.append('S4')
            if row['postmortem_flag']: flags.append('S5')
            return '-'.join(flags)

        df['status_combination'] = df.apply(get_status_combination, axis=1)

        # Prepare data for visualization
        service_combinations = {}
        for service in services_to_analyze:
            service_data = df[df[service] == 1]
            combinations = service_data['status_combination'].value_counts()
            total = combinations.sum()
            service_combinations[service] = (combinations / total).to_dict()

        # Create visualization
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Prepare data for stacked bar chart
        services = list(service_combinations.keys())
        all_combinations = sorted(list(set().union(*[set(d.keys()) for d in service_combinations.values()])))
        
        data = []
        for service in services:
            service_data = service_combinations[service]
            data.append([service_data.get(comb, 0) for comb in all_combinations])

        # Create stacked bar chart
        bottom = np.zeros(len(services))
        colors = sns.color_palette('tab10', n_colors=len(all_combinations))
        
        for i, combination in enumerate(all_combinations):
            values = [row[i] for row in data]
            ax.bar(services, values, bottom=bottom, label=combination, color=colors[i])
            
            # Add percentage labels
            for j, v in enumerate(values):
                if v > 0:
                    ax.text(j, bottom[j] + v/2, f'{v:.1%}', 
                           ha='center', va='center', color='white')
            bottom += values

        # Customize plot
        ax.set_xlabel('Service', fontsize=20)
        ax.set_ylabel('Percentage', fontsize=20)
        ax.legend(title='Status Combinations', bbox_to_anchor=(1.01, 1.0), loc='upper left')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        return fig

    except Exception as e:
        print(f"Error in failure recovery analysis: {str(e)}")
        raise 