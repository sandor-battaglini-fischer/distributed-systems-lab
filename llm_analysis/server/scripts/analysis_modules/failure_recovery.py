import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import (
    load_and_prepare_data,
    get_services_to_analyze,
    setup_plotting_style
)

def analyze_failure_recovery(start_date, end_date, selected_services):
    """
    Analyze failure recovery patterns and generate stacked bar plot
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=[f'{status}_timestamp' for status in 
                             ['investigating', 'identified', 'monitoring', 
                              'resolved', 'postmortem']]
        )
        
        # Get services to analyze
        services_to_analyze = get_services_to_analyze(selected_services)
        
        # Setup plotting style
        setup_plotting_style()

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
            
            # Add percentage labels
            for j, v in enumerate(values):
                if v > 0:
                    ax.text(j, bottom[j] + v/2, f'{v:.1%}', 
                           ha='center', va='center', color='white',
                           fontweight='bold')
            bottom += values

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