"""
Main pipeline orchestration: Extract → Transform → Load

This module coordinates all stages of the ETL pipeline
with error handling and logging.
"""

import sys
from pathlib import Path
from config import Config
from logger import logger, log_section, log_success, log_error
from extract import extract_data, validate_raw_data
from transform import transform_data, get_data_summary
from load import load_to_database, get_table_info


def run_pipeline():
    """
    Execute the complete ETL pipeline.
    
    Flow:
    1. Validate configuration
    2. Extract data from Parquet
    3. Transform and clean data
    4. Load to PostgreSQL
    5. Verify and log results
    """
    try:
        # Display configuration
        Config.display()
        
        # ===== EXTRACT =====
        df = extract_data(Config.PARQUET_PATH, Config.SAMPLE_SIZE)
        
        # Validate raw data
        if not validate_raw_data(df):
            raise ValueError("Raw data validation failed")
        
        # ===== TRANSFORM =====
        df = transform_data(df)
        get_data_summary(df)
        
        # ===== LOAD =====
        load_to_database(
            df,
            Config.DATABASE_URL,
            Config.TABLE_NAME,
            if_exists="replace"  # Use 'append' for incremental loads
        )
        
        # Display table info
        get_table_info(Config.DATABASE_URL, Config.TABLE_NAME)
        
        # ===== SUMMARY =====
        log_section("PIPELINE COMPLETE")
        log_success(f"✓ ETL Pipeline executed successfully!")
        logger.info(f"  Extracted: {len(df):,} rows")
        logger.info(f"  Transformed: {len(df):,} rows")
        logger.info(f"  Loaded to: {Config.TABLE_NAME}")
        logger.info(f"  Database: {Config.DATABASE_URL.split('@')[0]}...@...")
        
        return True
    
    except FileNotFoundError as e:
        log_error(f"Data file not found: {str(e)}")
        logger.info("\nTip: Ensure Parquet file path is correct.")
        logger.info(f"     PARQUET_PATH in .env: {Config.PARQUET_PATH}")
        return False
    
    except Exception as e:
        log_error(f"Pipeline failed: {str(e)}")
        logger.exception("Full traceback:")
        return False


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
