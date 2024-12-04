import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

def analyze_websites(start_date, end_date, selected_services):
    """
    Analyze and visualize website visits, outages, and incidents for different services.

    Parameters:
    start_date (datetime): Start date for filtering the data.
    end_date (datetime): End date for filtering the data.
    selected_services (list of str): List of services to analyze (e.g., ['ChatGPT', 'Claude']).

    Returns:
    fig (matplotlib.figure.Figure): The figure object with the plot.
    """
    try:
        # Ensure the start and end dates are datetime objects
        start_date = pd.to_datetime(start_date).replace(tzinfo=None)
        end_date = pd.to_datetime(end_date).replace(tzinfo=None)

        # Paths to data sources
        base_path = 'data'
        outage_path = os.path.join(base_path, 'clean', 'outage', '2024-08-31', 'outage_unexploded.csv')
        incident_path = os.path.join(base_path, 'clean', 'incident', '2024-08-31', 'incident_stages.csv')

        # Initialize the figure
        fig, ax1 = plt.subplots(figsize=(12, 6))

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
                services_to_analyze.append(mapped_service)
        
        print(f"Services to analyze: {services_to_analyze}")

        # Loop through each service to plot their respective data
        for service in services_to_analyze:
            # Read and preprocess website visits data
            visits_path = os.path.join(base_path, f'data/website_visits_{service.lower()}.csv')
            if not os.path.exists(visits_path):
                print(f"Warning: Visits data for {service} not found at {visits_path}")
                continue

            df_visits = pd.read_csv(visits_path)
            df_visits = df_visits[::-1]  # Reverse the order for chronological plotting

            # Plot the number of visits on the left y-axis
            ax1.plot(df_visits['Month'], df_visits['Monthly Website Visits (billions)'],
                     marker='o', linewidth=2, label=f'{service} Visits')

        ax1.set_xlabel(r'\textbf{Month}')
        ax1.set_ylabel(r'\textbf{Number of Visits [billions]}')
        ax1.tick_params(axis='y', labelsize=12)
        ax1.set_xticks(range(len(df_visits['Month'])))
        ax1.set_xticklabels(df_visits['Month'], rotation=45, ha='right', fontsize=12)
        ax1.grid(True, linestyle='--', color='gray', alpha=0.7)

        # Read and preprocess outage data
        df_outage = pd.read_csv(outage_path, parse_dates=['Date'])
        df_outage = df_outage[(df_outage['Service'].str.lower().isin([s.lower() for s in selected_services])) &
                              (df_outage['Date'] >= start_date) & (df_outage['Date'] <= end_date)]
        df_outage['Month'] = df_outage['Date'].dt.strftime('%Y-%m')
        df_outage = df_outage[df_outage['outage_flag'] >= 1]
        df_outage = df_outage.groupby('Month').size().reset_index(name='Outage Count')

        # Read and preprocess incident data
        df_incident = pd.read_csv(incident_path, parse_dates=['start_timestamp'])
        df_incident = df_incident[(df_incident[selected_services[0]] == 1) &
                                  (df_incident['start_timestamp'] >= start_date) &
                                  (df_incident['start_timestamp'] <= end_date)]
        df_incident['Month'] = df_incident['start_timestamp'].dt.strftime('%Y-%m')
        df_incident = df_incident.groupby('Month').size().reset_index(name='Incident Count')

        # Create the second y-axis on the right
        ax2 = ax1.twinx()
        ax2.plot(df_outage['Month'], df_outage['Outage Count'], marker='^', linewidth=2, color='r', label='Outages')
        ax2.plot(df_incident['Month'], df_incident['Incident Count'], marker='s', linewidth=2, color='g', label='Incidents')
        ax2.set_ylabel(r'\textbf{Monthly Failures}')
        ax2.tick_params(axis='y', labelsize=12)

        # Add annotations for each line
        if len(df_visits) > 13:
            ax1.text(len(df_visits) - 14, df_visits['Monthly Website Visits (billions)'].iloc[-13] + 0.4,
                     r'\textbf{Website Visits}', color='b', fontsize=12, verticalalignment='center')
        if len(df_outage) > 4:
            ax2.text(len(df_outage) - 5, df_outage['Outage Count'].iloc[-4] - 2,
                     r'\textbf{Outages}', color='r', fontsize=12, verticalalignment='center')
        if len(df_incident) > 6:
            ax2.text(len(df_incident) - 6, df_incident['Incident Count'].iloc[-1] - 2,
                     r'\textbf{Incidents}', color='g', fontsize=12, verticalalignment='center')

        plt.title(r'\textbf{Service Activity Analysis}', fontsize=16)
        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"Error in service activity analysis: {str(e)}")
        raise