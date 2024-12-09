import os
import pandas as pd
import warnings
import seaborn as sns
import ast
import matplotlib.pyplot as plt
from datetime import datetime

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

def get_data_path_incident():
    """Get the path to the incident data CSV file"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                       'static', 'data', 'incident_stages_all.csv')

def get_data_path_outage():
    """Get the path to the outage data CSV file"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                       'static', 'data', 'outage_unexploded.csv')

def get_service_mapping():
    """Get the mapping of service IDs to CSV column names"""
    return {
        'OpenAI:API': 'API',
        'OpenAI:ChatGPT': 'ChatGPT',
        'OpenAI:DALL-E': 'DALL-E',
        'OpenAI:Playground': 'Playground',
        'Anthropic:API': 'api.anthropic.com',
        'Anthropic:Claude': 'claude.ai',
        'Anthropic:Console': 'console.anthropic.com',
        'Character.AI:Character.AI': 'Character.AI',
        'StabilityAI:REST': 'REST API',
        'StabilityAI:gRPC': 'gRPC API',
        'StabilityAI:Assistant': 'Stable Assistant'
    }

def get_service_mapping_outage():
    """Get the mapping of service IDs to CSV column names"""
    return {
        'OpenAI:API': 'api',
        'OpenAI:ChatGPT': 'chatgpt',
        'OpenAI:DALL-E': 'labs',
        'OpenAI:Playground': 'playground',
        'Anthropic:API': 'api.anthropic.com',
        'Anthropic:Claude': 'claude.ai',
        'Anthropic:Console': 'console.anthropic.com',
        'Character.AI:Character.AI': 'character.ai'
    }


def load_and_prepare_data(start_date, end_date, timestamp_columns=None):
    """
    Load and prepare incident data with common preprocessing steps
    
    Args:
        start_date: Start date for filtering
        end_date: End date for filtering
        timestamp_columns: List of timestamp columns to convert
    
    Returns:
        Preprocessed DataFrame
    """
    # Convert dates to UTC timezone
    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')
    
    # Read data
    data_path = get_data_path_incident()
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}")
        
    df = pd.read_csv(data_path)
    
    # Convert timestamp columns
    if timestamp_columns:
        df = safe_convert_timezone(df, timestamp_columns)
    
    # Filter by date range using investigating_timestamp
    if 'start_timestamp' in df.columns:
        df = df[(df['start_timestamp'] >= start_date) & 
                (df['close_timestamp'] <= end_date)]
        
                
    return df


def load_and_prepare_data_outage(start_date, end_date):
    """
    Load and prepare outage data with common preprocessing steps

    Args:
        start_date (pd.Timestamp): Start date for filtering (UTC timezone)
        end_date (pd.Timestamp): End date for filtering (UTC timezone)

    Returns:
        pd.DataFrame: Preprocessed outage DataFrame
    """
    # Convert dates to UTC timezone
    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')
    
    # Read data
    data_path = get_data_path_outage()
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}")
        
    df = pd.read_csv(data_path)
    
    # Convert 'Date' column to datetime and localize to UTC
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.tz_localize('UTC')
    else:
        raise KeyError("'Date' column is missing in the outage data.")
    
    # Parse 'Incidents' column from string to list
    if 'Incidents' in df.columns:
        df['Incidents'] = df['Incidents'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
    else:
        raise KeyError("'Incidents' column is missing in the outage data.")
    
    # Compute 'Incident Count' column
    df['Incident Count'] = df['Incidents'].apply(len)
    
    # Filter by date range using 'Date' column
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    return df


def get_services_to_analyze(selected_services):
    """
    Map selected service IDs to CSV column names
    
    Args:
        selected_services: List of service IDs
        
    Returns:
        List of mapped service names
    """
    service_mapping = get_service_mapping()
    services_to_analyze = []
    
    for service in selected_services:
        if service in service_mapping:
            mapped_service = service_mapping[service]
            services_to_analyze.append(mapped_service)
            
    if not services_to_analyze:
        raise ValueError("No valid services selected for analysis")
        
    return services_to_analyze

def get_services_to_analyze_outage(selected_services):
    """
    Map selected service IDs to CSV column names
    
    Args:
        selected_services: List of service IDs
        
    Returns:
        List of mapped service names
    """
    service_mapping = get_service_mapping_outage()
    services_to_analyze = []
    
    for service in selected_services:
        if service in service_mapping:
            mapped_service = service_mapping[service]
            services_to_analyze.append(mapped_service)
            
    if not services_to_analyze:
        raise ValueError("No valid services selected for analysis")
        
    return services_to_analyze

def setup_plotting_style():
    """Set up common plotting style settings"""
    plt.style.use('default')
    sns.set_theme(style="whitegrid")
    
def safe_convert_timezone(df, timestamp_columns):
    """Safely convert timestamp columns to UTC timezone"""
    df = df.copy()
    for col in timestamp_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
            if df[col].dt.tz is None:
                df[col] = df[col].dt.tz_localize('UTC')
            else:
                df[col] = df[col].dt.tz_convert('UTC')
    return df

def safe_groupby(df, column, **kwargs):
    """Safely perform groupby operation with proper observed parameter"""
    return df.groupby(column, observed=True, **kwargs)

def safe_to_period(series, freq='M'):
    """Safely convert timestamp series to period, handling timezone"""
    return series.dt.tz_localize(None).dt.to_period(freq) 