"""Pipeline orchestration module for the Taylor Rule project.

Coordinates data ingestion, processing, and merging workflows.
"""

import pandas as pd
import yaml
from typing import Dict, List
import logging

from src.utils import log_execution, safe_load, DataLoadError, PipelineError, print_summary

logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates the complete data pipeline."""
    
    def __init__(self, config_path: str = './config/config.yaml'):
        """Initialize pipeline with configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.data = {}
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError as e:
            raise DataLoadError(f"Config file not found: {self.config_path}") from e
        except yaml.YAMLError as e:
            raise DataLoadError(f"Invalid YAML format in config: {str(e)}") from e
    
    @log_execution
    def fetch_focus_expectations(self):
        """Fetch and process Focus expected inflation data."""
        import src.ingestion as ingestion
        import src.processing as processing
        
        try:
            bcb_endpoint = self.config['ingestion']['bcb_endpoint_atas']
            raw_data_path = self.config['paths']['raw_data']
            save_files = self.config['processing']['save_files']
            
            # Fetch atas metadata
            atas_data = ingestion.fetch_atas(bcb_endpoint)
            logger.info(f"Fetched {len(atas_data)} Copom meetings")
            
            # Load Focus expectations
            focus_df = ingestion.FocusLoader(raw_data_path).load()
            logger.info(f"Loaded Focus data with shape {focus_df.shape}")
            
            # Filter by meeting dates
            filtered_df = processing.filter_expected_inflation_dates(
                atas_data, focus_df, save_files
            )
            self.data['focus_expectations'] = filtered_df
            logger.info(f"Filtered to {len(filtered_df)} records on Copom eve dates")
            return filtered_df
            
        except Exception as e:
            raise PipelineError(f"Failed to fetch Focus expectations: {str(e)}") from e
    
    @log_execution
    def fetch_bcb_expectations(self):
        """Fetch and process BC expectations data."""
        import src.ingestion as ingestion
        import src.processing as processing
        
        try:
            raw_data_path = self.config['paths']['raw_data']
            save_files = self.config['processing']['save_files']
            
            bcb_df = ingestion.BCBExpectationsLoader(raw_data_path).load()
            logger.info(f"Loaded BCB data with shape {bcb_df.shape}")
            
            interpolated_df = processing.interpolate_quartely_data(
                bcb_df, 'Infl. 12 m.', save_files
            )
            self.data['bcb_expectations'] = interpolated_df
            return interpolated_df
            
        except Exception as e:
            raise PipelineError(f"Failed to fetch BCB expectations: {str(e)}") from e
    
    @log_execution
    def fetch_selic_rate(self):
        """Fetch and process Selic rate data."""
        import src.ingestion as ingestion
        import src.processing as processing
        
        try:
            raw_data_path = self.config['paths']['raw_data']
            save_files = self.config['processing']['save_files']
            
            selic_df = ingestion.SelicRateLoader(raw_data_path).load()
            logger.info(f"Loaded Selic data with shape {selic_df.shape}")
            
            monthly_df = processing.resample_daily_to_monthly(
                selic_df, 'selic_rate', save_files
            )
            self.data['selic_rate'] = monthly_df
            return monthly_df
            
        except Exception as e:
            raise PipelineError(f"Failed to fetch Selic rate: {str(e)}") from e
    
    @log_execution
    def fetch_exchange_rate(self):
        """Fetch and process exchange rate data."""
        import src.ingestion as ingestion
        import src.processing as processing
        
        try:
            raw_data_path = self.config['paths']['raw_data']
            save_files = self.config['processing']['save_files']
            
            exchange_df = ingestion.ExchangeLoader(raw_data_path).load()
            logger.info(f"Loaded exchange rate data with shape {exchange_df.shape}")
            
            processed_df = processing.process_exchange_rate_data(exchange_df, save_files)
            self.data['exchange_rate'] = processed_df
            return processed_df
            
        except Exception as e:
            raise PipelineError(f"Failed to fetch exchange rate: {str(e)}") from e
    
    @log_execution
    def fetch_output_gap(self):
        """Fetch and process output gap data."""
        import src.ingestion as ingestion
        import src.processing as processing
        
        try:
            raw_data_path = self.config['paths']['raw_data']
            save_files = self.config['processing']['save_files']
            hp_lambda = self.config['processing']['hp_filter_lambda']
            
            output_df = ingestion.OutputLoader(raw_data_path).load()
            logger.info(f"Loaded output data with shape {output_df.shape}")
            
            filtered_df = processing.hp_filter_output(output_df, 'output', hp_lambda, save_files)
            self.data['output_gap'] = filtered_df
            return filtered_df
            
        except Exception as e:
            raise PipelineError(f"Failed to fetch output gap: {str(e)}") from e
    
    @log_execution
    def fetch_inflation_target(self):
        """Fetch and process inflation target data."""
        import src.ingestion as ingestion
        import src.processing as processing
        
        try:
            raw_data_path = self.config['paths']['raw_data']
            save_files = self.config['processing']['save_files']
            
            target_df = ingestion.InflationTargetLoader(raw_data_path).load()
            logger.info(f"Loaded inflation target data with shape {target_df.shape}")
            
            monthly_df = processing.resample_annualy_to_monthly(target_df, save_files)
            self.data['inflation_target'] = monthly_df
            return monthly_df
            
        except Exception as e:
            raise PipelineError(f"Failed to fetch inflation target: {str(e)}") from e
        
    def fetch_inflation(self):
        """Fetch and process inflation data."""
        import src.ingestion as ingestion
        import src.processing as processing
        
        try:
            raw_data_path = self.config['paths']['raw_data']
            save_files = self.config['processing']['save_files']
            
            inflation_df = ingestion.InflationLoader(raw_data_path).load()
            logger.info(f"Loaded inflation data with shape {inflation_df.shape}")
            
            processed_df = processing.process_inflation(inflation_df, save_files)
            self.data['inflation'] = processed_df
            return processed_df
            
        except Exception as e:
            raise PipelineError(f"Failed to fetch inflation data: {str(e)}") from e
    
    @log_execution
    def estimate_taylor_rule(self, data: pd.DataFrame, source = "market", year_range: tuple = None, dummy_range = None) -> pd.DataFrame:
        """Estimate Taylor Rule interest rates.
        
        Args:
            df: Merged dataset containing necessary variables
            source: Source of inflation expectations ('market' or 'bcb')
        
        Returns:
            DataFrame with estimated Taylor Rule rates
        """
        import src.estimation as estimation
        try:
            estimator = estimation.TaylorRuleEstimator(data=data, source=source, lag=int(self.config['estimation']['lag']))
            if not year_range:
                results_i, results_ii, results_iii = estimator.fit_models()
            else:
                if dummy_range:
                    results_i, results_ii, results_iii = estimator.fit_models(function=estimator.estimate_finer(year_range, dummy_range))
                else:
                    results_i, results_ii, results_iii = estimator.fit_models(function=estimator.estimate_range(year_range))
            logger.info("Taylor Rule estimation completed.")
            return estimator, results_i, results_ii, results_iii
        except Exception as e:
            raise PipelineError(f"Failed to estimate Taylor Rule: {str(e)}") from e

    @log_execution
    def run(self) -> pd.DataFrame:
        """Execute the complete pipeline.
        
        Returns:
            Merged and processed dataset
        """
        import src.processing as processing
        
        logger.info("=" * 50)
        logger.info("Starting Taylor Project Pipeline")
        logger.info("=" * 50)
        
        try:
            # Fetch all data sources in sequence
            dfs = [
                self.fetch_focus_expectations(),
                self.fetch_bcb_expectations(),
                self.fetch_selic_rate(),
                self.fetch_exchange_rate(),
                self.fetch_output_gap(),
                self.fetch_inflation_target(),
                self.fetch_inflation()
            ]
            
            # Merge datasets
            logger.info("Merging datasets...")
            save_files = self.config['processing']['save_files']
            df_merged = processing.merge_datasets(dfs, save_files)
            logger.info(f"Merged dataset shape: {df_merged.shape}")
            
            # Calculate deviation from target
            logger.info("Calculating deviation from inflation target...")
            df_final = processing.calculate_deviation_from_target(df_merged, save_files)
            
            logger.info("=" * 50)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 50)
            
            # Print summary
            print_summary(df_final)
            return df_final
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            raise
        
    def run_estimation(self, df_final: pd.DataFrame = None):
        """Run Taylor Rule estimation on the final dataset."""
        try:
            if df_final is None:
                df_final = self.run()
            estimator = dict()
            results = dict()
            ranges = self.config['estimation']['year_ranges']
            for year_range in ranges or [None]:
                normalized_range = tuple((year_range['start'], year_range['end'])) if year_range else None
                for i in range(2):
                    source = "market" if i == 0 else "bc"
                    est, *res = self.estimate_taylor_rule(
                        data=df_final,
                        source=source,
                        year_range=normalized_range,
                        dummy_range=year_range.get('dummy_range') if year_range else None
                    )
                    estimator[(source, normalized_range)] = est
                    results[(source, normalized_range)] = res
                    logger.info(
                        f"Taylor Rule estimation results for source '{source}' and year range '{normalized_range}':"
                    )
            logger.info("Taylor Rule estimation results obtained.")
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            raise

    def run_analysis(self, results: Dict) -> Dict:
        """Run analysis on the estimation results.
        
        Args:
            results: Dictionary of estimation results
        
        Returns:
            Dictionary of analysis summaries
        """
        import src.analytics as analytics
        
        try:
            analysis_summaries = dict()
            for key, res_list in results.items():
                analysis = analytics.analyze(res_list[-1])  # Analyze the most complex model
                summary_text = analysis.summarize_results()
                analysis_summaries[key] = summary_text
                logger.info(f"Analysis summary for {key}:\n{summary_text}")
            return analysis_summaries
        except Exception as e:
            logger.error(f"Analysis execution failed: {str(e)}", exc_info=True)
            raise

    def run_visualization(self, df_final: pd.DataFrame = None):
        """Run visualization on the final dataset and estimation results.
        
        Args:
            df_final: Final merged dataset
            results: Dictionary of estimation results
        """
        import src.vizualization as vizualization
        
        try:
            if df_final is None:
                df_final = self.run()
            plotter = vizualization.Plotter(df_final)
            plotter.plot_inflation(load_data=self.config['visualization']['save_plots'])
            plotter.plot_selic(load_data=self.config['visualization']['save_plots'])
            plotter.plot_output_and_exchange(load_data=self.config['visualization']['save_plots'])
            logger.info("Inflation plot generated.")
        except Exception as e:
            logger.error(f"Visualization execution failed: {str(e)}", exc_info=True)
            raise