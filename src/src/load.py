"""
Load stage: Persist transformed data to PostgreSQL.

This module handles database connection, table creation,
and efficient data insertion.
"""

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from logger import logger, log_success, log_error, log_section


def load_to_database(
    df: pd.DataFrame,
    database_url: str,
    table_name: str,
    if_exists: str = "replace"
) -> bool:
    """
    Load transformed DataFrame to PostgreSQL.
    
    Args:
        df: Transformed DataFrame
        database_url: PostgreSQL connection string
        table_name: Target table name
        if_exists: What to do if table exists
                  ('fail', 'replace', 'append')
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        SQLAlchemyError: If database operation fails
    """
    log_section("LOAD: Insert Data to PostgreSQL")
    
    logger.info(f"Target table: {table_name}")
    logger.info(f"Rows to insert: {len(df):,}")
    logger.info(f"Strategy (if_exists): {if_exists}")
    
    try:
        # Create database engine
        logger.info("\nConnecting to database...")
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
        
        # Check if table exists
        inspector = inspect(engine)
        table_exists = table_name in inspector.get_table_names()
        logger.info(f"Table '{table_name}' exists: {table_exists}")
        
        # Load data to database
        logger.info(f"\nInserting {len(df):,} rows to '{table_name}'...")
        
        df.to_sql(
            table_name,
            engine,
            if_exists=if_exists,
            index=False,
            method='multi',  # Faster insertion
            chunksize=10000  # Insert in batches
        )
        
        logger.info(f"✓ Data insertion complete")
        
        # Verify insertion
        row_count = _get_row_count(engine, table_name)
        logger.info(f"✓ Verified {row_count:,} rows in table")
        
        log_success(f"Loaded {len(df):,} rows to {table_name}")
        
        engine.dispose()
        return True
    
    except SQLAlchemyError as e:
        error_msg = f"Database error: {str(e)}"
        log_error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error during load: {str(e)}"
        log_error(error_msg)
        raise


def _get_row_count(engine, table_name: str) -> int:
    """Get row count from table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            )
            return result.scalar()
    except Exception as e:
        logger.warning(f"Could not verify row count: {str(e)}")
        return 0


def get_table_info(database_url: str, table_name: str) -> None:
    """Display information about loaded table."""
    try:
        engine = create_engine(database_url)
        
        # Get schema info
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        
        logger.info(f"\nTable Schema ({table_name}):")
        logger.info("  Column Name          | Data Type      | Nullable")
        logger.info("  " + "-" * 55)
        
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            nullable = "Yes" if col['nullable'] else "No"
            logger.info(f"  {col_name:20} | {col_type:14} | {nullable}")
        
        engine.dispose()
    
    except Exception as e:
        logger.warning(f"Could not retrieve table info: {str(e)}")
