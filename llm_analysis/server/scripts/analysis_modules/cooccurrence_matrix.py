import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from .utils import safe_convert_timezone
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

def analyze_cooccurrence_matrix(start_date, end_date, selected_services):
    """
    Analyze and visualize service incident co-occurrence patterns
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
        df = safe_convert_timezone(df, ['investigating_timestamp'])

        # Filter by date range
        df = df[(df['investigating_timestamp'] >= start_date) & 
                (df['investigating_timestamp'] <= end_date)]

        # Map selected services to CSV column names
        service_mapping = {
            'OpenAI:API': 'API',
            'OpenAI:ChatGPT': 'ChatGPT',
            'OpenAI:DALL-E': 'DALL-E',
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

        # Calculate co-occurrence matrix
        cooccurrence = np.zeros((len(services_to_analyze), len(services_to_analyze)))
        
        for i, service1 in enumerate(services_to_analyze):
            for j, service2 in enumerate(services_to_analyze):
                if i <= j:  # Only calculate upper triangle
                    # Count incidents where both services were affected
                    cooccurrence[i, j] = ((df[service1] == 1) & (df[service2] == 1)).sum()
                    if i != j:  # Mirror for lower triangle
                        cooccurrence[j, i] = cooccurrence[i, j]

        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create heatmap with improved aesthetics
        sns.heatmap(
            cooccurrence,
            xticklabels=[s.replace('_', ' ') for s in services_to_analyze],
            yticklabels=[s.replace('_', ' ') for s in services_to_analyze],
            annot=True,
            fmt='g',
            cmap='YlOrRd',
            square=True,
            cbar_kws={'label': 'Number of Co-occurring Incidents'}
        )

        # Customize plot
        plt.title('Service Incident Co-occurrence Matrix', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        # Add text annotations for percentages
        total_incidents = {
            service: (df[service] == 1).sum() 
            for service in services_to_analyze
        }

        for i in range(len(services_to_analyze)):
            for j in range(len(services_to_analyze)):
                if i != j and cooccurrence[i, j] > 0:
                    # Calculate percentage of co-occurrence relative to individual service incidents
                    pct_i = (cooccurrence[i, j] / total_incidents[services_to_analyze[i]]) * 100
                    pct_j = (cooccurrence[i, j] / total_incidents[services_to_analyze[j]]) * 100
                    text = f'{cooccurrence[i, j]:.0f}\n({pct_i:.1f}%/{pct_j:.1f}%)'
                    ax.text(j + 0.5, i + 0.5, text,
                           ha='center', va='center',
                           color='black' if cooccurrence[i, j] < cooccurrence.max()/2 else 'white')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in co-occurrence matrix analysis: {str(e)}")
        raise 