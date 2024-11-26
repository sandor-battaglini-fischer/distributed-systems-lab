import pandas as pd
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

def safe_convert_timezone(df, timestamp_columns):
    """
    Safely convert timestamp columns to UTC timezone
    """
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
    """
    Safely perform groupby operation with proper observed parameter
    """
    return df.groupby(column, observed=True, **kwargs)

def safe_to_period(series, freq='M'):
    """
    Safely convert timestamp series to period, handling timezone
    """
    return series.dt.tz_localize(None).dt.to_period(freq) 