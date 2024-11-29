import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import os
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Define impact level descriptions with updated severity levels
IMPACT_LEVELS = {
    0: "None - Post-resolved notification or documentation update",
    1: "Minor - Brief disruption or elevated error rates with limited impact",
    2: "Major - Significant service degradation affecting core functionality",
    3: "Critical - Complete service outage or severe widespread impact",
    4: "Maintenance - Planned maintenance or scheduled updates"
}

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_provider_display_name(provider):
    """Convert provider name to proper display format"""
    provider_names = {
        'anthropic': 'Anthropic',
        'openai': 'OpenAI',
        'google': 'Google',
        'microsoft': 'Microsoft',
        'meta': 'Meta',
        'character': 'Character.AI'
    }
    return provider_names.get(provider, provider.title())

def analyze_impact_levels(df, output_dir):
    """
    Analyze the distribution of incident impact levels for each service provider.
    Returns statistical measures and creates visualization.
    """
    # Convert incident_impact_level to numeric if not already
    df['incident_impact_level'] = pd.to_numeric(df['incident_impact_level'])
    
    # Convert timestamps for timeframe calculation
    df['start_timestamp'] = pd.to_datetime(df['start_timestamp'])
    timeframe_start = df['start_timestamp'].min()
    timeframe_end = df['start_timestamp'].max()
    
    # Set up the plot style with larger font sizes
    plt.style.use('default')
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "font.size": 14,
        "axes.labelsize": 16,
        "axes.titlesize": 18,
        "legend.fontsize": 14,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
    })
    
    # Create figure with adjusted size
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create box plot
    sns.boxplot(
        data=df,
        x='provider',
        y='incident_impact_level',
        width=0.3,
        color='lightgray',
        showfliers=False,
        zorder=2
    )
    
    # Create violin plot
    sns.violinplot(
        data=df,
        x='provider',
        y='incident_impact_level',
        bw_method=0.5,
        cut=0.8,
        density_norm='width',
        inner=None,
        alpha=0.3,
        zorder=1
    )
    
    # Plot points with density-based jitter
    providers = df['provider'].unique()
    for idx, provider in enumerate(providers):
        provider_data = df[df['provider'] == provider]
        
        # For each impact level, calculate appropriate jitter
        for impact_level in range(5):
            level_data = provider_data[provider_data['incident_impact_level'] == impact_level]
            
            if len(level_data) > 0:
                # Calculate jitter based on number of points
                n_points = len(level_data)
                
                if n_points == 1:
                    # Single point, center it
                    x_positions = [idx]
                else:
                    # Multiple points, distribute them based on normal distribution
                    std = min(0.2, 0.4 / np.sqrt(n_points))
                    x_positions = np.random.normal(idx, std, n_points)
                    
                    # Clip to ensure points stay within bounds
                    x_positions = np.clip(x_positions, idx - 0.4, idx + 0.4)
                
                # Create scatter plot with simple styling
                plt.scatter(
                    x_positions,
                    [impact_level] * n_points,
                    color='darkred',
                    alpha=0.5,
                    s=40,
                    zorder=3
                )
    
    # Define legend elements before using them
    legend_elements = [
        Patch(facecolor='lightgray', edgecolor='black', alpha=0.7,
              label='Quartile Range'),
        Line2D([0], [0], color='black', linestyle='-', linewidth=2,
               label='Median'),
        Patch(facecolor='gray', alpha=0.3,
              label='Distribution'),
        Line2D([0], [0], marker='o', color='darkred',
               markersize=8, alpha=0.5,
               label='Individual Incidents'),
    ]
    
    # Add statistical annotations for each provider
    for idx, provider in enumerate(providers):
        provider_data = df[df['provider'] == provider]
        stats = {
            'n': len(provider_data),
            'mean': provider_data['incident_impact_level'].mean(),
            'median': provider_data['incident_impact_level'].median(),
            'std': provider_data['incident_impact_level'].std()
        }
        
        # Add mean line
        plt.hlines(y=stats['mean'], xmin=idx-0.3, xmax=idx+0.3,
                  colors='blue', linestyles='--', alpha=0.5, linewidth=2,
                  label='Mean' if idx == 0 else "")
        
        # Make median line more visible
        plt.hlines(y=stats['median'], xmin=idx-0.3, xmax=idx+0.3,
                  colors='red', linestyles='-', alpha=0.7, linewidth=2.5,
                  label='Median' if idx == 0 else "")
    
    # Update legend to include statistical lines
    legend_elements.extend([
        Line2D([0], [0], color='red', linestyle='-', linewidth=2.5, alpha=0.7,
               label='Median'),
        Line2D([0], [0], color='blue', linestyle='--', linewidth=2, alpha=0.5,
               label='Mean')
    ])
    
    # Adjust y-axis limits (no need for extra space for text boxes)
    plt.ylim(-0.5, 4.5)
    
    # Update legend with new elements
    plt.legend(handles=legend_elements, 
              loc='upper right',
              title='Plot Elements',
              title_fontsize=16,
              framealpha=0.9,
              edgecolor='black',
              fontsize=14)
    
    # Update x-axis labels with proper provider names and larger font
    plt.xticks(range(len(providers)), 
               [get_provider_display_name(p) for p in providers],
               rotation=0,
               fontsize=16)
    
    # Add timeframe to title with larger fonts
    timeframe_str = f"{timeframe_start.strftime('%B %Y')} - {timeframe_end.strftime('%B %Y')}"
    plt.suptitle(r'$\mathrm{Distribution\;of\;Incident\;Impact\;Levels}$', 
                 y=0.95, fontsize=22)
    plt.title(f"Analysis Period: {timeframe_str}", 
             fontsize=16, pad=20)
    
    plt.xlabel(r'$\mathrm{Provider}$', fontsize=18, labelpad=10)
    plt.ylabel(r'$\mathrm{Impact\;Level}$', fontsize=18, labelpad=10)
    
    # Get colors for each impact level from the CSV
    impact_colors = {}
    for level in range(5):
        color = df[df['incident_impact_level'] == level]['Incident_color'].iloc[0] \
                if len(df[df['incident_impact_level'] == level]) > 0 else '#333333'
        impact_colors[level] = color
    
    # Update y-axis labels with larger font
    severity_labels = [IMPACT_LEVELS[i].split(' - ')[0] for i in range(5)]
    plt.yticks(range(5))
    
    # Add colored labels with larger font
    for i, label in enumerate(severity_labels):
        ax.text(-0.1, i, f"{i} ({label})", 
                transform=ax.get_yaxis_transform(),
                ha='right',
                va='center',
                color=impact_colors[i],
                fontweight='bold',
                fontsize=16)
    
    # Hide original y-tick labels
    ax.set_yticklabels([])
    
    # Set y-axis limits with padding
    plt.ylim(-0.5, 4.5)
    
    # Enhance grid
    plt.grid(True, axis='y', alpha=0.2, linestyle='--')
    
    # Save plot with improved spacing
    plt.savefig(
        os.path.join(output_dir, 'impact_level_distribution.png'), 
        dpi=300, 
        bbox_inches='tight', 
        facecolor='white'
    )
    plt.close()
    
    # Add statistics to stats_dict
    stats_dict = {}
    for provider in providers:
        provider_data = df[df['provider'] == provider]
        
        # Basic statistics
        stats_dict[provider] = {
            'count': provider_data.shape[0],
            'mean': provider_data['incident_impact_level'].mean(),
            'median': provider_data['incident_impact_level'].median(),
            'std': provider_data['incident_impact_level'].std(),
            'mode': provider_data['incident_impact_level'].mode()[0],
            'skewness': provider_data['incident_impact_level'].skew(),
            'kurtosis': provider_data['incident_impact_level'].kurt(),
            'distribution': provider_data['incident_impact_level'].value_counts().to_dict()
        }
    
    return stats_dict, timeframe_start, timeframe_end

def format_stats_report(stats_dict, timeframe_start, timeframe_end):
    """Format the statistical results into a readable report."""
    report = "Incident Impact Level Distribution Analysis\n"
    report += "=" * 50 + "\n\n"
    
    # Add timeframe information
    report += f"Analysis Period: {timeframe_start.strftime('%B %Y')} - {timeframe_end.strftime('%B %Y')}\n"
    report += "=" * 50 + "\n\n"
    
    # Add impact level descriptions
    report += "Impact Level Definitions:\n"
    report += "-" * 30 + "\n"
    for level, description in IMPACT_LEVELS.items():
        severity = description.split(' - ')[0]
        details = description.split(' - ')[1]
        report += f"Level {level} ({severity}): {details}\n"
    report += "\n" + "=" * 50 + "\n\n"
    
    # Add cross-provider comparison note
    report += "Cross-Provider Impact Level Comparison:\n"
    report += "-" * 30 + "\n"
    report += ("Note: Impact levels are standardized across providers to enable comparison.\n"
              "However, each provider may have slightly different internal criteria for\n"
              "assigning impact levels. The standardization is based on:\n"
              "- Scope of impact (number of users/services affected)\n"
              "- Duration of incident\n"
              "- Severity of service degradation\n"
              "- Business impact\n\n"
              "Level 0 (None) typically indicates incidents that were resolved before\n"
              "being reported or were reported after resolution. Level 4 (Maintenance)\n"
              "is used for planned events rather than incidents.\n\n")
    report += "=" * 50 + "\n\n"
    
    # Provider-specific statistics
    for provider, stats in stats_dict.items():
        report += f"Provider: {get_provider_display_name(provider)}\n"
        report += "-" * 30 + "\n"
        report += f"Total Incidents: {stats['count']}\n"
        report += f"Mean Impact Level: {stats['mean']:.2f}\n"
        report += f"Median Impact Level: {stats['median']:.2f}\n"
        report += f"Standard Deviation: {stats['std']:.2f}\n"
        report += f"Mode: {stats['mode']}\n"
        report += f"Skewness: {stats['skewness']:.2f}\n"
        report += f"Kurtosis: {stats['kurtosis']:.2f}\n"
        
        report += "\nDistribution of Impact Levels:\n"
        for level, count in stats['distribution'].items():
            percentage = (count / stats['count']) * 100
            severity = IMPACT_LEVELS[level].split(' - ')[0]
            details = IMPACT_LEVELS[level].split(' - ')[1]
            report += f"Level {level} ({severity}): {details}\n"
            report += f"  {count} incidents ({percentage:.1f}%)\n"
        
        report += "\n" + "=" * 50 + "\n\n"
    
    return report

def main():
    # Set up output directory
    output_dir = 'server/static/additional_analysis/incident_impact_levels'
    ensure_dir(output_dir)
    
    # Read the CSV file
    df = pd.read_csv('server/static/data/incident_stages.csv')
    
    # Perform analysis
    stats_dict, timeframe_start, timeframe_end = analyze_impact_levels(df, output_dir)
    
    # Generate report
    report = format_stats_report(stats_dict, timeframe_start, timeframe_end)
    
    # Save report
    report_path = os.path.join(output_dir, 'impact_level_analysis_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    
    return stats_dict, report

if __name__ == "__main__":
    main()
