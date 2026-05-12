"""
Logging module for NYC Taxi Data Pipeline.

Provides centralized, consistent logging across all pipeline stages.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "pipeline",
    log_level: str = "INFO",
    log_file: str = "pipeline.log"
) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create log directory if needed
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # File gets all levels
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Module-level logger
logger = setup_logger()


def log_section(section_name: str) -> None:
    """Log a major section header."""
    logger.info("=" * 70)
    logger.info(f"  {section_name.upper()}")
    logger.info("=" * 70)


def log_success(message: str) -> None:
    """Log a success message."""
    logger.info(f"✓ {message}")


def log_error(message: str) -> None:
    """Log an error message."""
    logger.error(f"✗ {message}")


def log_warning(message: str) -> None:
    """Log a warning message."""
    logger.warning(f"⚠ {message}")
