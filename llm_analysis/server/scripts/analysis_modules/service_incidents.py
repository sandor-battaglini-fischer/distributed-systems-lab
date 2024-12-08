import pandas as pd
import matplotlib.pyplot as plt
from .utils import load_and_prepare_data

def analyze_service_incidents(start_date, end_date, services):
    """
    Analyze and visualize service incident combinations, showing how services
    are impacted together during incidents.

    Args:
        start_date (datetime): Start date for filtering incident data
        end_date (datetime): End date for filtering incident data
        services (list): List of service identifiers to analyze

    Returns:
        dict: Dictionary containing Matplotlib Figure objects for each provider
    """
    try:
        # Load and prepare data
        df = load_and_prepare_data(start_date, end_date, timestamp_columns=['investigating_timestamp', 'start_timestamp', 'close_timestamp'])
        
        # Convert timestamps
        status_lst = ['investigating', 'identified', 'monitoring', 'resolved', 'postmortem', 'start']
        for status in status_lst:
            df[f'{status}_timestamp'] = pd.to_datetime(df[f'{status}_timestamp'])

        # Rename columns for clarity
        df.rename(columns={
            'API': 'API-OpenAI',
            'ChatGPT': 'ChatGPT',
            'Labs': 'DALL-E',
            'Playground': 'Playground',
            'api.anthropic.com': 'API-Anthropic',
            'claude.ai': 'Claude',
            'console.anthropic.com': 'Console',
            'Character.AI': 'Character.AI'
        }, inplace=True)

        # Define service lists
        service_lst = ['API-OpenAI', 'ChatGPT', 'DALL-E', 'Playground', 
                      'API-Anthropic', 'Claude', 'Console', 'Character.AI']
        
        # Create separate DataFrames for each service
        dfs = {}
        for service in service_lst:
            dfs[service] = df[df[service] == 1].reset_index(drop=True)

        # Group by provider
        provider_lst = ['openai', 'anthropic', 'character']
        dfs_provider = {}
        for provider in provider_lst:
            dfs_provider[provider] = pd.DataFrame()
            for service in service_lst:
                if provider in dfs[service]['provider'].unique():
                    provider_data = dfs[service][dfs[service]['provider'] == provider]
                    dfs_provider[provider] = pd.concat([dfs_provider[provider], provider_data])

        # Define provider-specific service lists
        openai_lst = ['API-OpenAI', 'ChatGPT', 'DALL-E', 'Playground']
        anthropic_lst = ['API-Anthropic', 'Claude', 'Console']

        # Analyze OpenAI services
        openai_df = dfs_provider['openai'][openai_lst]
        openai_df['impact_range'] = openai_df.sum(axis=1)
        openai_impact_counts = openai_df['impact_range'].value_counts().sort_index()
        openai_df['impacted_services'] = openai_df.apply(
            lambda row: [service for service in openai_df.columns[:-1] if row[service] == 1],
            axis=1
        )

        # Analyze Anthropic services
        anthropic_df = dfs_provider['anthropic'][anthropic_lst]
        anthropic_df['impact_range'] = anthropic_df.sum(axis=1)
        anthropic_impact_counts = anthropic_df['impact_range'].value_counts().sort_index()
        anthropic_df['impacted_services'] = anthropic_df.apply(
            lambda row: [service for service in anthropic_df.columns[:-1] if row[service] == 1],
            axis=1
        )

        # Create impact range DataFrame
        impact_range_df = pd.DataFrame({
            'OpenAI': openai_impact_counts,
            'Anthropic': anthropic_impact_counts
        })

        # Calculate percentages
        impact_range_percent = impact_range_df.T.div(impact_range_df.T.sum(axis=1), axis=0) * 100
        impact_range_percent = impact_range_percent.round(2)

        figures = {}

        # Plot OpenAI service combinations
        service_labels = {
            'API-OpenAI': 'O1',
            'ChatGPT': 'O2',
            'DALL-E': 'O3',
            'Playground': 'O4'
        }

        openai_df['impacted_services_short'] = openai_df['impacted_services'].apply(
            lambda services: [service_labels[service] for service in services]
        )
        openai_df['impacted_services_short_str'] = openai_df['impacted_services_short'].apply(
            lambda x: ', '.join(x)
        )
        impacted_combinations_counts = openai_df['impacted_services_short_str'].value_counts()

        plt.figure(figsize=(10, 8))
        ax = impacted_combinations_counts[::-1].plot(
            kind='barh',
            color='grey',
            edgecolor='black'
        )

        for i, count in enumerate(impacted_combinations_counts[::-1]):
            plt.text(count + 0.5, i, str(count), ha='left', va='center', fontsize=12)

        plt.title("OpenAI", fontsize=16, pad=20)
        plt.ylabel("Impacted Services", fontsize=14)
        plt.xlabel("Number of Incidents", fontsize=14)

        label_text = "O1: API-OpenAI\nO2: ChatGPT\nO3: DALL-E\nO4: Playground"
        plt.text(
            0.99, 0.01, label_text,
            ha='right', va='bottom',
            transform=plt.gca().transAxes,
            fontsize=10,
            bbox=dict(facecolor='white', alpha=0.5)
        )

        plt.tight_layout()
        figures['openai'] = plt.gcf()

        # Plot Anthropic service combinations
        service_labels = {
            'API-Anthropic': 'A1',
            'Claude': 'A2',
            'Console': 'A3'
        }

        anthropic_df['impacted_services_short'] = anthropic_df['impacted_services'].apply(
            lambda services: [service_labels[service] for service in services]
        )
        anthropic_df['impacted_services_short_str'] = anthropic_df['impacted_services_short'].apply(
            lambda x: ', '.join(x)
        )
        impacted_combinations_counts = anthropic_df['impacted_services_short_str'].value_counts()

        plt.figure(figsize=(10, 8))
        ax = impacted_combinations_counts[::-1].plot(
            kind='barh',
            color='grey',
            edgecolor='black'
        )

        for i, count in enumerate(impacted_combinations_counts[::-1]):
            plt.text(count + 0.5, i, str(count), ha='left', va='center', fontsize=12)

        plt.title("Anthropic", fontsize=16, pad=20)
        plt.ylabel("Impacted Services", fontsize=14)
        plt.xlabel("Number of Incidents", fontsize=14)

        label_text = "A1: API-Anthropic\nA2: Claude\nA3: Console"
        plt.text(
            0.99, 0.01, label_text,
            ha='right', va='bottom',
            transform=plt.gca().transAxes,
            fontsize=10,
            bbox=dict(facecolor='white', alpha=0.5)
        )

        plt.tight_layout()
        figures['anthropic'] = plt.gcf()

        return figures

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise 