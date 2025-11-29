from pathlib import Path
from typing import List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def read_file(path: Path) -> pd.DataFrame:
    """Read a csv/xlsx/xls file into a DataFrame. Raises on unreadable files."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path}")


def load_data_from_dir(data_dir: Path, patterns: List[str] = ("*.csv", "*.xlsx", "*.xls")) -> List[pd.DataFrame]:
    """
    Load all files from a directory matching common patterns and return a list of DataFrames.
    Prints summary logging for each file.
    """
    dataframes = []
    data_dir = Path(data_dir)
    if not data_dir.exists():
        logger.warning("Data directory does not exist: %s", data_dir)
        return dataframes

    files = []
    for pat in patterns:
        files.extend(sorted(data_dir.glob(pat)))

    for path in files:
        try:
            df = read_file(path)
            dataframes.append(df)
            logger.info("Loaded %s — rows: %d cols: %d", path.name, df.shape[0], df.shape[1])
        except Exception as e:
            logger.exception("Failed to load %s: %s", path, e)
    return dataframes