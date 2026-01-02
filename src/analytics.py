# Calculate taylor rule and sensitivity analysis

from statsmodels.stats.diagnostic import acorr_breusch_godfrey
import pandas as pd

class analyze:
    """Class to calculate the Taylor rule and perform sensitivity analysis."""
    
    def __init__(self, results):
        self.results = results
    
    def estructural_params(self):
        """Extract coefficients from the regression results."""
        alpha1 = self.results.params['selic_target_lag']
        alpha2 = self.results.params['inf_dev']/(1-alpha1)
        alpha3 = self.results.params.get('output_gap_lag', 0)/(1-alpha1)
        alpha4 = self.results.params.get('exchange_rate_var_lag', 0)/(1-alpha1)
        return alpha1, alpha2, alpha3, alpha4

    def lm_value(self):
        """Calculate the LM test for autocorrelation."""
        lm_test = acorr_breusch_godfrey(self.results, nlags=4)
        return lm_test[3]  # LM statistic

    def summarize_results(self):
        """Summarize the regression results."""
        summary = self.results.summary()
        alpha1, alpha2, alpha3, alpha4 = self.estructural_params()
        test = self.results.t_test("inf_dev + selic_target_lag = 1")
        lm_stat = self.lm_value()
        
        summary_text = f"""
        Taylor Rule Estimation Results:
        -------------------------------
        Coefficient on Lagged Selic Rate (alpha1): {alpha1:.4f}
        Coefficient on Inflation Deviation (alpha2): {alpha2:.4f}
        Coefficient on Output Gap (alpha3): {alpha3:.4f}
        Coefficient on Exchange Rate Variation (alpha4): {alpha4:.4f}
        
        LM Test Statistic for Autocorrelation: {lm_stat:.4f}
        
        T-Test Statistic for alpha2 > 1: {test}

        Full Regression Summary:
        {summary}


        """
        return summary_text
