import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def analyze_failure_recovery(start_date, end_date, selected_services):
    """
    Analyze failure recovery patterns and generate stacked bar plot
    """
    try:
        start_date = pd.to_datetime(start_date).tz_localize('UTC')
        end_date = pd.to_datetime(end_date).tz_localize('UTC')
        
        service_mapping = {
            # OpenAI Services
            'OpenAI:Playground': 'Playground',
            'OpenAI:API': 'API',
            'OpenAI:Labs': 'Labs',
            'OpenAI:ChatGPT': 'ChatGPT',
            
            # Anthropic Services
            'Anthropic:API': 'api.anthropic.com',
            'Anthropic:Claude': 'claude.ai',
            'Anthropic:Console': 'console.anthropic.com',
            
            # Character.AI Services
            'Character.AI:Character.AI': 'Character.AI',
        }

        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'static', 'data', 'incident_stages.csv')
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found at {data_path}")

        df = pd.read_csv(data_path)
        
        status_columns = ['investigating', 'identified', 'monitoring', 'resolved', 'postmortem']
        for status in status_columns:
            df[f'{status}_timestamp'] = pd.to_datetime(df[f'{status}_timestamp'])
            if df[f'{status}_timestamp'].dt.tz is None:
                df[f'{status}_timestamp'] = df[f'{status}_timestamp'].dt.tz_localize('UTC')
            else:
                df[f'{status}_timestamp'] = df[f'{status}_timestamp'].dt.tz_convert('UTC')

        # Filter by date range
        df = df[
            (df['investigating_timestamp'] >= start_date) & 
            (df['investigating_timestamp'] <= end_date)  
        ]

        services_to_analyze = []
        for service in selected_services:
            if service in service_mapping:
                mapped_service = service_mapping[service]
                if mapped_service in df.columns:
                    services_to_analyze.append(mapped_service)
                else:
                    print(f"Warning: Mapped service {mapped_service} not found in CSV columns")
            else:
                print(f"Warning: No mapping found for service {service}")

        if not services_to_analyze:
            raise ValueError("No valid services selected for analysis")

        print("Selected services:", selected_services)
        print("Mapped services:", services_to_analyze)

        def get_status_combination(row):
            flags = []
            if row['investigating_flag']: flags.append('S1')
            if row['identified_flag']: flags.append('S2')
            if row['monitoring_flag']: flags.append('S3')
            if row['resolved_flag']: flags.append('S4')
            if row['postmortem_flag']: flags.append('S5')
            return '-'.join(flags)

        df['status_combination'] = df.apply(get_status_combination, axis=1)

        # Set the style for the plot
        plt.style.use('default')
        sns.set_theme(style="whitegrid")


        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Prepare data for stacked bar chart
        service_combinations = {}
        for service in services_to_analyze:
            # Filter incidents where this service was affected
            service_data = df[df[service] == 1]
            if len(service_data) > 0:  # Only process if there's data
                combinations = service_data['status_combination'].value_counts()
                total = combinations.sum()
                if total > 0:
                    service_combinations[service] = (combinations / total).to_dict()
                    print(f"Found {total} incidents for {service}")
            else:
                print(f"No incidents found for {service}")

        if not service_combinations:
            raise ValueError("No data found for any of the selected services in the given date range")

        # Create stacked bar chart
        services = list(service_combinations.keys())
        all_combinations = sorted(list(set().union(*[set(d.keys()) for d in service_combinations.values()])))
        
        data = []
        for service in services:
            service_data = service_combinations[service]
            data.append([service_data.get(comb, 0) for comb in all_combinations])

        # Create stacked bar chart
        bottom = np.zeros(len(services))
        colors = sns.color_palette("husl", n_colors=len(all_combinations))
        
        for i, combination in enumerate(all_combinations):
            values = [row[i] for row in data]
            ax.bar(services, values, bottom=bottom, label=combination, color=colors[i])
            
            # Add percentage labels
            for j, v in enumerate(values):
                if v > 0:
                    ax.text(j, bottom[j] + v/2, f'{v:.1%}', 
                           ha='center', va='center', color='white',
                           fontweight='bold')
            bottom += values

        # Customize plot
        ax.set_xlabel('Service', fontsize=12, fontweight='bold')
        ax.set_ylabel('Percentage', fontsize=12, fontweight='bold')
        ax.set_title('Status Combinations by Service', fontsize=14, pad=20, fontweight='bold')
        ax.legend(title='Status Combinations', bbox_to_anchor=(1.05, 1.0), loc='upper left')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        return fig

    except Exception as e:
        print(f"Error in failure recovery analysis: {str(e)}")
        raise