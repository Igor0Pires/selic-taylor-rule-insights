# Processing module
import pandas as pd
from typing import Literal


def filter_expected_inflation_dates(atas_data, df_expected, load_data: bool) -> pd.Series:
    """Filter expected inflation dates.
    
    when use: process focus expected inflation data

    Reason: use the inflation expectations collected on the eve of Copom meetings, avoiding possible endogeneity
    problems.
    """

    df = pd.DataFrame(atas_data)
    dates = pd.to_datetime(df['dataReferencia'])
    eve_dates = dates - pd.Timedelta(days=1) 
    df_expected['Date'] = pd.to_datetime(df_expected['Date'], dayfirst=True)
    df_expected.columns.values[1] = 'focus_expected_inflation'

    filtered_df = df_expected[df_expected['Date'].isin(eve_dates)]
    # Recursively search for eve dates, falling back to previous days if not found
    for offset in range(1, 8):  # Search up to 7 days back
        if len(filtered_df) > 0:
            break
        fallback_dates = dates - pd.Timedelta(days=offset)
        filtered_df = df_expected[df_expected['Date'].isin(fallback_dates)]

    if load_data:
        filtered_df.to_csv('./data/processed/focus_expected_inflation_filtered.csv', index=False)

    return filtered_df



def interpolate_quartely_data(df: pd.DataFrame, column: str, load_data: bool) -> pd.DataFrame:
    """Interpolate quarterly data to monthly frequency using linear interpolation.
    
    when use: process bcb expectations data
    """
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%Y')
    df[column] = pd.to_numeric(df[column], errors='coerce')
    df.set_index('Date', inplace=True)
    df = df.resample('MS').asfreq() # Resample to monthly frequency (NaN for missing months)
    df[column] = df[column].interpolate(method='linear') # Linear interpolation
    df.reset_index(inplace=True)
    df.columns.values[1] = 'bcb_expected_inflation'
    if load_data:
        df.to_csv('./data/processed/bcb_expectations_interpolated.csv', index=False)
    return df

def resample_daily_to_monthly(df: pd.DataFrame, column: str, load_data: bool) -> pd.DataFrame:
    """Resample daily data to monthly frequency using month-end values.
    
    when use: process selic rate data
    """
    
    df.columns.values[1] = 'selic_target'
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    df.set_index('Date', inplace=True)
    df['selic_target'] = df['selic_target'].str.replace(',', '.')
    df['selic_target'] = pd.to_numeric(df['selic_target'], errors='coerce')
    df = df.resample('ME').last() # Resample to last day
    df.reset_index(inplace=True)
    if load_data:
        df.to_csv('./data/processed/selic_target_monthly.csv', index=False)
    return df

def process_exchange_rate_data(df: pd.DataFrame, load_data: bool) -> pd.DataFrame:
    """Process variation exchange rate data.
    
    when use: process exchange rate data
    """

    df.columns.values[1] = 'exchange_rate'
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    df.set_index('Date', inplace=True)

    df['exchange_rate'] = df['exchange_rate'].str.replace(',', '.')
    df['exchange_rate'] = pd.to_numeric(df['exchange_rate'], errors='coerce')

    df.sort_index(inplace=True)
    df = df.resample('ME').mean()
    df['exchange_rate_var'] = df['exchange_rate'].pct_change(fill_method=None) * 100

    df.reset_index(inplace=True)
    if load_data:
        df.to_csv('./data/processed/exchange_rate_var.csv', index=False)
    return df

def hp_filter_output(df: pd.DataFrame, column: str, lamb, load_data: bool) -> pd.DataFrame:
    """Apply Hodrick-Prescott filter.
    
    when use: process output gap data
    """
    from statsmodels.tsa.filters.hp_filter import hpfilter

    df['Date'] = pd.to_datetime(df['Date'], format='%b-%y', errors='coerce')
    
    # Remove rows with NaN values in Data or the target column
    df = df.dropna(subset=['Date', column]).copy()
    
    df.set_index('Date', inplace=True)
    
    _, df['output_potential'] = hpfilter(df[column], lamb=lamb)

    df['output_gap'] = df[column] - df['output_potential']
    df.reset_index(inplace=True)

    if load_data:
        df.to_csv('./data/processed/output_gap_hp_filter.csv', index=False)
    return df

def resample_annualy_to_monthly(df: pd.DataFrame, load_data: bool) -> pd.DataFrame:
    """ Resample annual data to monthly frequency using forward fill.
        add columns: upper and lower limits of tolerance.
    
    when use: process inflation target data

    """
    df.rename(columns={df.columns[1]: 'inflation_target', df.columns[2]: 'interval_size'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y', errors='coerce')
    df.set_index('Date', inplace=True)
    df = df.resample('MS').asfreq() # Resample to monthly frequency (NaN for missing months)
    try:
        df['inflation_target'] = pd.to_numeric(df['inflation_target'], errors='coerce')
        df['interval_size'] = pd.to_numeric(df['interval_size'], errors='coerce')
    except Exception as e:
        pass
    df['inflation_target'] = df['inflation_target'].ffill() # Forward fill to propagate annual value to all months
    df['upper_limit'] = df['inflation_target'] + df['interval_size'] 
    df['lower_limit'] = df['inflation_target'] - df['interval_size']
    df.reset_index(inplace=True)
    if load_data:
        df.to_csv('./data/processed/inflation_target_monthly.csv', index=False)
    return df

def process_inflation(df: pd.DataFrame, load_data: bool) -> pd.DataFrame:
    """process inflation data to calculate 12-month inflation rate.
    
    when use: process inflation data
    """
    df.columns.values[1] = 'inflation_12m'
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%Y', errors='coerce')
    df.set_index('Date', inplace=True)
    df['inflation_12m'] = pd.to_numeric(df['inflation_12m'].str.replace(',', '.'), errors='coerce')
    df.reset_index(inplace=True)
    if load_data:
        df.to_csv('./data/processed/inflation_12m.csv', index=False)
    return df


def merge_datasets(dfs: list[pd.DataFrame], load_data: bool) -> pd.DataFrame:
    """Merge multiple datasets on the 'Date' column.
    
    when use: merge all processed datasets into a final dataframe
    """
    from functools import reduce

    for df in dfs:
        df['Date'] = df['Date'].dt.to_period('M')
    df_merged = reduce(lambda left, right: pd.merge(left, right, on='Date', how='left'), dfs)

    if load_data:
        df_merged.to_csv('./data/processed/final_merged_dataset.csv', index=False)
    
    return df_merged


def calculate_deviation_from_target(df_final: pd.DataFrame, load_data: bool) -> pd.DataFrame:
    """Calculate deviation from inflation target.

    formula: deviation = (12-month)/12 * (expected_inflation - inflation_target(t)) + month/12 * (expected_inflation - inflation_target(t+1))
    
    when use: calculate deviation for focus and bcb expected inflation data
    """

    df_final = df_final.copy()
    df_final['ano'] = df_final['Date'].dt.year
    df_final['mes'] = df_final['Date'].dt.month
    df_final['inflation_target_next'] = df_final.groupby('mes')['inflation_target'].shift(-1)
    df_final['bcb_inflation_deviation'] = ((12-df_final['mes']) / 12 ) * (df_final['bcb_expected_inflation'] - df_final['inflation_target']) + (df_final['mes'] / 12) * (df_final['bcb_expected_inflation'] - df_final['inflation_target_next'])
    df_final['focus_inflation_deviation'] = ((12-df_final['mes']) / 12 ) * (df_final['focus_expected_inflation'] - df_final['inflation_target']) + (df_final['mes'] / 12) * (df_final['focus_expected_inflation'] - df_final['inflation_target_next'])

    if load_data:
        df_final.to_csv('./data/processed/final_merged_dataset.csv', index=False)
        print("final file dataset was updated")
    else: 
        print("final file dataset was not saved")
    return df_final