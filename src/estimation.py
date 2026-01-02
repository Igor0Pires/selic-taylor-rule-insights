# Class Estimation
import pandas as pd
import statsmodels.formula.api as smf
import datetime as dt

class TaylorRuleEstimator:
    """Class to estimate taylor rule parameters.
    data: pd.DataFrame with columns 'focus_inflation_deviation', 'output_gap', 'selic_target', 'exchange_rate_var', 'Date'
    """
    def __init__(self, data: pd.DataFrame, source: str = 'market', lag: int = 1):
        """
        source: 'market' (Focus) or 'bc'
        """
        self.data = data.copy()
        self.source = source
        self.lag = lag

    def _source_column(self):
        if self.source == 'market':
            self.data['inf_dev'] = self.data['focus_inflation_deviation']
        elif self.source == 'bc':
            self.data['inf_dev'] = self.data['bcb_inflation_deviation']
        else:
            raise ValueError("Source must be either 'market' or 'bc'.")

    def _apply_lag(self):
        self.data['output_gap_lag'] = self.data['output_gap'].shift(self.lag)
        # inf_dev is not lagged, the selic is chosen based on current inflation deviation 
        self.data['exchange_rate_var_lag'] = self.data['exchange_rate_var'].shift(self.lag)
        self.data['selic_target_lag'] = self.data['selic_target'].shift(self.lag)
        self.data.dropna(subset=['output_gap_lag', 'exchange_rate_var_lag', 'selic_target_lag', 'inf_dev'], inplace=True)

    def estimate_naive(self):
        """Estimate the Taylor rule parameters using OLS regression."""
        self._source_column()
        self._apply_lag()

        # model I: only inflation
        model_i = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev', data=self.data)
        
        # model II: inflation + output
        model_ii = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev + output_gap_lag', data=self.data)    

        # model III: inflattion + output + exchange
        model_iii = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev + output_gap_lag + exchange_rate_var_lag', data=self.data)
        return model_i, model_ii, model_iii
    
    def estimate_range(self, year_range: tuple):
        """Estimate the Taylor rule parameters over a specified year range.
        
        year_range: (start_year, end_year) e.g. (5, 10)
        """

        self._source_column()
        self._apply_lag()

        df_range = self.data[(self.data['ano'] >= year_range[0]) & (self.data['ano'] <= year_range[1])].copy()
        if df_range.empty:
            raise ValueError(f"No data available for the specified year range: {year_range}.")
        

        # model I: only inflation
        model_i = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev', data=df_range)
        
        # model II: inflation + output
        model_ii = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev + output_gap_lag', data=df_range)    

        # model III: inflattion + output + exchange
        model_iii = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev + output_gap_lag + exchange_rate_var_lag', data=df_range)
        return model_i, model_ii, model_iii

    def estimate_finer(self, year_range: tuple, dummy_range: tuple):
        """Estimate the Taylor rule parameters over a specified year range.
        
        year_range: (start_year, end_year) e.g. (5, 10)
        dummy_range: (start: MM-YYYY, end) e.g. (10-2002, 03-2003)
        """
        self._source_column()
        self._apply_lag()

        df_range = self.data[(self.data['ano'] >= year_range[0]) & (self.data['ano'] <= year_range[1])].copy()
        if df_range.empty:
            raise ValueError(f"No data available for the specified year range: {year_range}.")
        
        # Create dummy variable for the specified date range (1 if within range, 0 otherwise)
        try:
            start_period = pd.Period(dummy_range[0], freq='M')
            end_period = pd.Period(dummy_range[1], freq='M')

            if not 'Period' not in df_range['Date'].dtype.name:
                df_range.loc[:, 'Date'] = df_range['Date'].dt.to_period('M')
            
            # Add dummy variable
            df_range.loc[:, f'dummy_var'] = ((df_range['Date'] >= start_period) & (df_range['Date'] <= end_period)).astype(int)
            
        except Exception as e:
            raise ValueError(f"Error creating dummy variable: {e}") from e
            
        # model I: only inflation
        model_i = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev + dummy_var:inf_dev', data=df_range)
        
        # model II: inflation + output
        model_ii = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev + output_gap_lag + dummy_var:inf_dev', data=df_range)    

        # model III: inflattion + output + exchange
        model_iii = smf.ols(formula=f'selic_target ~ selic_target_lag + inf_dev + output_gap_lag + exchange_rate_var_lag + dummy_var:inf_dev', data=df_range)
        return model_i, model_ii, model_iii

    def fit_models(self, function=None):
        """Fit all three model specifications and return the results."""
        if function is None:
            function = self.estimate_naive()
        model_i, model_ii, model_iii = function
        
        results_i = model_i.fit(cov_type='HAC', cov_kwds={'maxlags':4})
        results_ii = model_ii.fit(cov_type='HAC', cov_kwds={'maxlags':4})
        results_iii = model_iii.fit(cov_type='HAC', cov_kwds={'maxlags':4})
        
        return results_i, results_ii, results_iii