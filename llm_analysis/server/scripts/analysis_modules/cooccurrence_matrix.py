import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import (
    load_and_prepare_data,
    get_services_to_analyze,
    setup_plotting_style
)

def analyze_cooccurrence_matrix(start_date, end_date, selected_services):
    """
    Analyze and visualize service incident co-occurrence patterns
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=['investigating_timestamp']
        )
        
        # Get services to analyze
        services_to_analyze = get_services_to_analyze(selected_services)
        
        # Setup plotting style
        setup_plotting_style()
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Calculate co-occurrence matrix
        cooccurrence = np.zeros((len(services_to_analyze), len(services_to_analyze)))
        
        for i, service1 in enumerate(services_to_analyze):
            for j, service2 in enumerate(services_to_analyze):
                if i <= j:  # Only calculate upper triangle
                    cooccurrence[i, j] = ((df[service1] == 1) & (df[service2] == 1)).sum()
                    if i != j:  # Mirror for lower triangle
                        cooccurrence[j, i] = cooccurrence[i, j]

        # Create heatmap
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

        # Add percentage annotations
        total_incidents = {
            service: (df[service] == 1).sum() 
            for service in services_to_analyze
        }

        for i in range(len(services_to_analyze)):
            for j in range(len(services_to_analyze)):
                if i != j and cooccurrence[i, j] > 0:
                    pct_i = (cooccurrence[i, j] / total_incidents[services_to_analyze[i]]) * 100
                    pct_j = (cooccurrence[i, j] / total_incidents[services_to_analyze[j]]) * 100
                    text = f'{cooccurrence[i, j]:.0f}\n({pct_i:.1f}%/{pct_j:.1f}%)'
                    ax.text(j + 0.5, i + 0.5, text,
                           ha='center', va='center',
                           color='black' if cooccurrence[i, j] < cooccurrence.max()/2 else 'white')

        plt.title('Service Incident Co-occurrence Matrix', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        return fig

    except Exception as e:
        print(f"Error in co-occurrence matrix analysis: {str(e)}")
        raise 