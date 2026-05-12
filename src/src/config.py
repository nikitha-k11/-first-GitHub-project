"""
Configuration module for NYC Taxi Data Pipeline.

Loads environment variables from .env file and provides
centralized access to all pipeline configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)


class Config:
    """Configuration class with environment-based settings."""
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/dbname"
    )
    TABLE_NAME = os.getenv("TABLE_NAME", "yellow_taxi_2023")
    
    # Data Input
    PARQUET_PATH = os.getenv(
        "PARQUET_PATH",
        "/kaggle/input/datasets/kurapatinikitha/nyc-taxi/yellow_tripdata_2023-01.parquet"
    )
    SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", "500000"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "pipeline.log")
    
    # Output
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        if not cls.DATABASE_URL or cls.DATABASE_URL == "postgresql://user:password@localhost/dbname":
            raise ValueError(
                "DATABASE_URL not configured. "
                "Please set DATABASE_URL in .env file."
            )
        
        if not Path(cls.PARQUET_PATH).exists():
            print(f"  Warning: Parquet file not found at {cls.PARQUET_PATH}")
            print("   This is expected when running outside Kaggle environment.")
    
    @classmethod
    def display(cls) -> None:
        """Display current configuration (hide sensitive data)."""
        print("\n" + "="*60)
        print("PIPELINE CONFIGURATION")
        print("="*60)
        print(f"Database Table:     {cls.TABLE_NAME}")
        print(f"Data Source:        {Path(cls.PARQUET_PATH).name}")
        print(f"Sample Size:        {cls.SAMPLE_SIZE:,} rows")
        print(f"Log Level:          {cls.LOG_LEVEL}")
        print(f"Output Directory:   {cls.OUTPUT_DIR}")
        print(f"Database (masked):  {cls.DATABASE_URL.split('@')[0]}...@...")
        print("="*60 + "\n")


# Module-level access
DATABASE_URL = Config.DATABASE_URL
TABLE_NAME = Config.TABLE_NAME
PARQUET_PATH = Config.PARQUET_PATH
SAMPLE_SIZE = Config.SAMPLE_SIZE
LOG_LEVEL = Config.LOG_LEVEL
OUTPUT_DIR = Config.OUTPUT_DIR
