import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from .utils import (
    load_and_prepare_data,
    get_services_to_analyze,
    setup_plotting_style
)
import traceback

IMPACT_LEVELS = {
    0: "None - Post-resolved notification or documentation update",
    1: "Minor - Brief disruption or elevated error rates with limited impact",
    2: "Major - Significant service degradation affecting core functionality",
    3: "Critical - Complete service outage or severe widespread impact",
    4: "Maintenance - Planned maintenance or scheduled updates"
}

def analyze_incident_distribution(start_date, end_date, services):
    """
    Analyze and visualize the distribution of incident impact levels across providers
    """
    try:
        print(f"Starting incident distribution analysis with dates: {start_date} to {end_date}")
        
        # Load data with timestamp columns specified
        df = load_and_prepare_data(
            start_date, 
            end_date,
            timestamp_columns=['investigating_timestamp', 'start_timestamp', 'close_timestamp']
        )
        print(f"Loaded data shape: {df.shape}")
        
        # Convert impact levels to numeric if they aren't already
        df['incident_impact_level'] = pd.to_numeric(df['incident_impact_level'], errors='coerce')
        
        # Setup plotting
        setup_plotting_style()
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Create violin plot
        sns.violinplot(
            data=df,
            x='provider',
            y='incident_impact_level',
            color='gray',
            inner=None,
            alpha=0.3,
            zorder=1,
            ax=ax
        )
        
        # Add individual points
        providers = df['provider'].unique()
        for idx, provider in enumerate(providers):
            provider_data = df[df['provider'] == provider]
            
            for impact_level in range(5):
                level_data = provider_data[provider_data['incident_impact_level'] == impact_level]
                
                if len(level_data) > 0:
                    n_points = len(level_data)
                    
                    if n_points == 1:
                        x_positions = [idx]
                    else:
                        std = min(0.2, 0.4 / np.sqrt(n_points))
                        x_positions = np.random.normal(idx, std, n_points)
                        x_positions = np.clip(x_positions, idx - 0.4, idx + 0.4)
                    
                    ax.scatter(
                        x_positions,
                        [impact_level] * n_points,
                        color='darkred',
                        alpha=0.5,
                        s=40,
                        zorder=3
                    )
        
        # Add legend
        legend_elements = [
            Patch(facecolor='lightgray', edgecolor='black', alpha=0.7,
                  label='Quartile Range'),
            Line2D([0], [0], color='black', linestyle='-', linewidth=2,
                   label='Median'),
            Patch(facecolor='gray', alpha=0.3,
                  label='Distribution'),
            Line2D([0], [0], marker='o', color='darkred',
                   markersize=8, alpha=0.5,
                   label='Individual Incidents')
        ]
        
        ax.legend(handles=legend_elements,
                 loc='center left',
                 bbox_to_anchor=(1.02, 0.5),
                 title='Plot Elements',
                 framealpha=0.9,
                 edgecolor='black')
        
        # Customize plot
        ax.set_xlabel('Provider')
        ax.set_ylabel('Impact Level')
        ax.set_title('Distribution of Incident Impact Levels')
        
        # Set y-axis ticks and labels
        ax.set_yticks(range(5))
        severity_labels = [IMPACT_LEVELS[i].split(' - ')[0] for i in range(5)]
        ax.set_yticklabels(severity_labels)
        
        ax.set_ylim(-0.5, 4.5)
        ax.grid(True, axis='y', alpha=0.2, linestyle='--')
        
        # Add box around plot
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1)
            spine.set_edgecolor('black')
        
        # Add timeframe to title
        timeframe_start = pd.to_datetime(start_date).strftime('%d %B %Y').replace(' ', '\\;')
        timeframe_end = pd.to_datetime(end_date).strftime('%d %B %Y').replace(' ', '\\;')
        title = f"$\\mathrm{{Distribution\\;of\\;Incident\\;Impact\\;Levels\\;({timeframe_start}\\;-\\;{timeframe_end})}}$"
        if df.empty:
            title += "\n$\\mathrm{(No\\;incidents\\;recorded\\;in\\;this\\;period)}$"
        fig.suptitle(title, y=0.95, fontsize=22)  # Use suptitle instead of ax.set_title
        
        # Adjust layout
        plt.tight_layout()
        if not df.empty:
            plt.subplots_adjust(right=0.85, top=0.9)  # Add space for legend
        
        # Save the figure before returning
        return fig

    except Exception as e:
        print(f"Error in incident distribution analysis: {str(e)}")
        traceback.print_exc()  # Add traceback for better error debugging
        return None
