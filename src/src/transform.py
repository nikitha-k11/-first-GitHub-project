"""
Transform stage: Clean and prepare NYC Yellow Taxi data.

This module handles:
- Datetime conversions
- Feature engineering (trip_duration)
- Column standardization
- Data type validation
"""

import pandas as pd
import numpy as np
from logger import logger, log_success, log_error, log_section


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all transformation steps to raw data.
    
    Args:
        df: Raw DataFrame from extraction
    
    Returns:
        Cleaned and transformed DataFrame
    """
    log_section("TRANSFORM: Clean and Prepare Data")
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Step 1: Convert datetime columns
    df = _convert_datetime_columns(df)
    
    # Step 2: Create derived features
    df = _create_features(df)
    
    # Step 3: Standardize column names
    df = _standardize_columns(df)
    
    # Step 4: Validate and clean
    df = _validate_and_clean(df)
    
    log_success(f"Transformed {len(df):,} rows successfully")
    return df


def _convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert datetime columns from object to datetime64."""
    logger.info("\n1. Converting datetime columns...")
    
    datetime_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
    
    for col in datetime_cols:
        if col in df.columns:
            logger.info(f"   Converting {col}...")
            df[col] = pd.to_datetime(df[col])
            logger.info(f"   ✓ {col} converted to datetime64[ns]")
    
    return df


def _create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived features from raw columns."""
    logger.info("\n2. Creating derived features...")
    
    # Trip duration (minutes)
    logger.info("   Calculating trip_duration (minutes)...")
    df['trip_duration'] = (
        df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    ).dt.total_seconds() / 60
    logger.info(f"   ✓ trip_duration created (mean: {df['trip_duration'].mean():.2f} min)")
    
    # Trip distance (miles)
    if 'trip_distance' in df.columns:
        logger.info("   trip_distance already present (keeping as-is)")
    
    return df


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to snake_case."""
    logger.info("\n3. Standardizing column names (PascalCase → snake_case)...")
    
    rename_map = {
        'VendorID': 'vendor_id',
        'RatecodeID': 'rate_code_id',
        'PULocationID': 'pu_location_id',
        'DOLocationID': 'do_location_id',
        'store_and_fwd_flag': 'store_and_fwd_flag',
    }
    
    # Only rename columns that exist
    rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    
    df = df.rename(columns=rename_map)
    logger.info(f"   ✓ Renamed {len(rename_map)} columns")
    
    return df


def _validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate data types and clean invalid records."""
    logger.info("\n4. Validating and cleaning data...")
    
    initial_rows = len(df)
    
    # Remove rows with trip_duration < 0 or > 24 hours (1440 min)
    logger.info("   Checking trip_duration validity...")
    invalid_duration = (df['trip_duration'] < 0) | (df['trip_duration'] > 1440)
    invalid_count = invalid_duration.sum()
    
    if invalid_count > 0:
        logger.warning(f"   Found {invalid_count} rows with invalid duration")
        df = df[~invalid_duration]
    
    # Remove rows with negative fare
    logger.info("   Checking fare_amount validity...")
    if 'fare_amount' in df.columns:
        invalid_fare = df['fare_amount'] < 0
        if invalid_fare.sum() > 0:
            logger.warning(f"   Found {invalid_fare.sum()} rows with negative fare")
            df = df[df['fare_amount'] >= 0]
    
    # Remove rows with passenger_count < 1
    logger.info("   Checking passenger_count validity...")
    if 'passenger_count' in df.columns:
        invalid_passengers = df['passenger_count'] < 1
        if invalid_passengers.sum() > 0:
            logger.warning(f"   Found {invalid_passengers.sum()} rows with 0 passengers")
            df = df[df['passenger_count'] >= 1]
    
    rows_removed = initial_rows - len(df)
    if rows_removed > 0:
        logger.warning(f"   Removed {rows_removed} invalid rows")
    else:
        logger.info(f"   ✓ All {len(df):,} rows are valid")
    
    return df


def get_data_summary(df: pd.DataFrame) -> None:
    """Log summary statistics of transformed data."""
    logger.info("\nData Summary:")
    logger.info(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    logger.info(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    logger.info(f"\n  Numeric columns summary:")
    logger.info(df.describe().to_string())
