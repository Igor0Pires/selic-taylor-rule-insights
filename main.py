"""Main entry point for Taylor Rule project pipeline."""

import logging
from src.pipeline import Pipeline
from src.utils import setup_logging

# Setup logging
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Execute the complete pipeline."""
    try:
        pipeline = Pipeline(config_path='./config/config.yaml')
        df_final = pipeline.run()
        logger.info("Pipeline execution successful!")
        res = pipeline.run_estimation(df_final)
        logger.info("Estimation execution successful!")
        pipeline.run_analysis(res)
        logger.info("Analysis execution successful!")
        pipeline.run_visualization(df_final)
        logger.info("Visualization execution successful!")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()