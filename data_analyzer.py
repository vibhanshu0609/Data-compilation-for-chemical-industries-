from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

def generate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return summary statistics and add counts for nulls and uniques."""
    if df.empty:
        return pd.DataFrame()
    try:
        # newer pandas supports datetime_is_numeric
        desc = df.describe(include='all', datetime_is_numeric=False).T
    except TypeError:
        # fall back for older pandas versions
        desc = df.describe(include='all').T
    desc['null_count'] = df.isna().sum()
    desc['unique'] = df.nunique(dropna=True)
    return desc


def scale_numeric_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with numeric columns scaled using StandardScaler."""
    df = df.copy()
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric:
        logger.info("No numeric columns to scale")
        return df
    scaler = StandardScaler()
    df[numeric] = scaler.fit_transform(df[numeric].astype(float))
    return df


def detect_anomalies_iqr(df: pd.DataFrame, column: str, k: float = 1.5) -> pd.DataFrame:
    """Return rows flagged as anomalies in `column` using IQR method."""
    series = df[column].dropna().astype(float)
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    low = q1 - k * iqr
    high = q3 + k * iqr
    mask = (df[column] < low) | (df[column] > high)
    return df[mask]