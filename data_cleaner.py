from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

DEFAULT_ALIAS_MAP = {
    'temp': 'temperature',
    'temp_c': 'temperature',
    'temperature_c': 'temperature',
    'ph_value': 'ph',
    'product_id': 'product_code',
    'prod_id': 'product_code',
    'date_time': 'timestamp',
    'time': 'timestamp',
    'qty_kg': 'quantity_kg',
    'quantity_(kg)': 'quantity_kg',
    'cost_($)': 'cost_usd',
    'purity_(%)': 'purity_pct'
}


def standardize_columns(df: pd.DataFrame, alias_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Normalize column names: strip, lowercase, replace spaces and apply alias map."""
    if alias_map is None:
        alias_map = DEFAULT_ALIAS_MAP
    df = df.copy()
    cols = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    cols = [alias_map.get(c, c) for c in cols]
    df.columns = cols
    return df


def parse_datetimes(df: pd.DataFrame, candidates=('timestamp', 'date')) -> pd.DataFrame:
    """Try to parse datetime-like columns in place."""
    df = df.copy()
    for c in candidates:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    return df


def fill_missing_values(df: pd.DataFrame, numeric_strategy='mean', fill_str='Unknown') -> pd.DataFrame:
    """
    Fill missing values:
     - numeric columns: strategy can be 'mean' (default) or a numeric constant
     - object/category columns: fill with fill_str
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if numeric_strategy == 'mean':
            val = df[col].mean()
        else:
            try:
                val = float(numeric_strategy)
            except Exception:
                val = 0.0
        df[col] = df[col].fillna(val)

    # Fill non-numeric with a sentinel
    obj_cols = df.select_dtypes(include=['object', 'category']).columns
    df[obj_cols] = df[obj_cols].fillna(fill_str)
    return df


def clean_and_standardize(df: pd.DataFrame, alias_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Complete cleaning pipeline for a single DataFrame."""
    df = standardize_columns(df, alias_map=alias_map)
    df = parse_datetimes(df)
    df = fill_missing_values(df)
    return df


def merge_dataframes(dfs: List[pd.DataFrame], how='outer') -> pd.DataFrame:
    """
    Merge/concatenate multiple DataFrames into one. Uses concat to preserve union of columns.
    """
    if not dfs:
        return pd.DataFrame()
    merged = pd.concat(dfs, ignore_index=True, sort=False)
    # drop rows that are entirely NaN
    merged = merged.dropna(how='all').reset_index(drop=True)
    logger.info("Merged DataFrame shape: %s", merged.shape)
    return merged