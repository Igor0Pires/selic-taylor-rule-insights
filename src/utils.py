"""Utility functions for logging, error handling, and common operations."""

import logging
import sys
from functools import wraps
from typing import Callable, Any

# Configure logging
def setup_logging(level=logging.INFO):
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('./logs/pipeline.log', encoding='utf-8')
        ]
    )

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass


class DataLoadError(PipelineError):
    """Exception raised when data loading fails."""
    pass


class DataProcessingError(PipelineError):
    """Exception raised when data processing fails."""
    pass


def log_execution(func: Callable) -> Callable:
    """Decorator to log function execution with timing."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import time
        func_name = func.__name__
        logger.info(f"Starting {func_name}...")
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"Completed {func_name} in {elapsed:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Error in {func_name}: {str(e)}", exc_info=True)
            raise
    return wrapper


def safe_load(func: Callable) -> Callable:
    """Decorator to safely handle data loading with error catching."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise DataLoadError(f"Data file not found: {str(e)}") from e
        except Exception as e:
            raise DataLoadError(f"Failed to load data: {str(e)}") from e
    return wrapper


def print_summary(df):
    """Print a summary of a DataFrame."""
    logger.info(f"Shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    logger.info(f"\nFirst few rows:\n{df.head()}")
