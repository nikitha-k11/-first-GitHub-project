"""
Extract stage: Load NYC Yellow Taxi data from Parquet file.

This module handles reading the Parquet data source with
optional sampling for large datasets.
"""

import pandas as pd
from pathlib import Path
from logger import logger, log_success, log_error, log_section


def extract_data(
    parquet_path: str,
    sample_size: int | None = None
) -> pd.DataFrame:
    """
    Extract data from Parquet file.
    
    Args:
        parquet_path: Path to Parquet file
        sample_size: Number of rows to sample (None = all rows)
    
    Returns:
        DataFrame with extracted data
    
    Raises:
        FileNotFoundError: If Parquet file doesn't exist
        Exception: If reading Parquet fails
    """
    log_section("EXTRACT: Load Parquet Data")
    
    parquet_file = Path(parquet_path)
    
    # Validate file exists
    if not parquet_file.exists():
        error_msg = f"Parquet file not found: {parquet_path}"
        log_error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info(f"Reading Parquet file: {parquet_file.name}")
    
    try:
        # Read Parquet with metadata
        df = pd.read_parquet(parquet_path)
        logger.info(f"  Total rows in file: {len(df):,}")
        logger.info(f"  Columns: {len(df.columns)}")
        
        # Apply sampling if specified
        if sample_size and sample_size < len(df):
            logger.info(f"  Sampling {sample_size:,} rows...")
            df = df.head(sample_size)
            logger.info(f"  Sample size: {len(df):,} rows")
        
        # Display column info
        logger.info(f"  Data types:\n{df.dtypes}")
        
        log_success(f"Extracted {len(df):,} rows from Parquet")
        return df
    
    except Exception as e:
        error_msg = f"Failed to read Parquet file: {str(e)}"
        log_error(error_msg)
        raise


def validate_raw_data(df: pd.DataFrame) -> bool:
    """
    Validate raw data quality before transformation.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        True if data is valid, logs warnings otherwise
    """
    logger.info("\nValidating raw data...")
    
    # Check for completely empty data
    if df.empty:
        log_error("DataFrame is empty!")
        return False
    
    # Check for duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        logger.warning(f"Found {duplicates:,} duplicate rows")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        logger.warning("Missing values detected:")
        for col, count in missing[missing > 0].items():
            pct = (count / len(df)) * 100
            logger.warning(f"  {col}: {count:,} ({pct:.2f}%)")
    
    log_success("Raw data validation complete")
    return True
