# Data ingestion module
import requests
import yaml
import pandas as pd

def fetch_atas(endpoint, key: str = 'conteudo') -> dict:
    """Fetch data from the given API endpoint."""

    response = requests.get(endpoint)
    response.raise_for_status() # Raise an error for bad responses

    return response.json()[key]

class Loader:
    """Class for loading different types of data."""
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        with open('./config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
    
    def load(self):  
        raise NotImplementedError("Load method must be implemented in subclasses.")

class FocusLoader(Loader):
    def load(self) -> pd.DataFrame:
        """Load Focus expected inflation data from CSV files in the specified folder."""
        pattern = self.config['files_patterns']['focus_expected_inflation']
        from glob import glob
        files_list = glob(self.folder_path + pattern)
        if not files_list:
            raise FileNotFoundError(f"No expected inflation CSV files found in the specified folder. (searched in: {self.folder_path} by pattern '{pattern}')")
        
        df_concatenated = pd.DataFrame()
        for file in files_list:
            df = pd.read_csv(file)
            df_concatenated = pd.concat([df_concatenated, df], ignore_index=True)
        return df_concatenated

class BCBExpectationsLoader(Loader):
    def load(self) -> pd.DataFrame:
        """Load BC expectations time series data from a CSV file.
        
        only one file is expected to be found.
        """
        pattern = self.config['files_patterns']['bcb_expected_inflation']
        file_path = self.folder_path + pattern
        if not file_path:
            raise FileNotFoundError(f"No BC expectations CSV file found in the specified folder. (searched in: {self.folder_path} by pattern '{pattern}')")
        df = pd.read_csv(file_path)       
        return df
    
class SelicRateLoader(Loader):
    def load(self) -> pd.DataFrame:
        """Load Selic rate time series data from a CSV file.
        
        only one file is expected to be found.
        """
        pattern = self.config['files_patterns']['selic_target_rate']
        file_path = self.folder_path + pattern
        if not file_path:
            raise FileNotFoundError(f"No Selic rate CSV file found in the specified folder. (searched in: {self.folder_path} by pattern '{pattern}')")
        df = pd.read_csv(file_path, sep=";")       
        return df
    
class ExchangeLoader(Loader):
    def load(self) -> pd.DataFrame:
        """Load exchange rate VAR data from a CSV file.
        
        only one file is expected to be found.
        """
        pattern = self.config['files_patterns']['exchange_rate']
        file_path = self.folder_path + pattern
        if not file_path:
            raise FileNotFoundError(f"No exchange rate CSV file found in the specified folder. (searched in: {self.folder_path} by pattern '{pattern}')")
        df = pd.read_csv(file_path, sep=";")
        return df
    
class OutputLoader(Loader):
    def load(self) -> pd.DataFrame:
        """Load output gap data from a CSV file.
        
        only one file is expected to be found.
        """
        pattern = self.config['files_patterns']['output_proxy']
        file_path = self.folder_path + pattern
        if not file_path:
            raise FileNotFoundError(f"No output gap CSV file found in the specified folder. (searched in: {self.folder_path} by pattern '{pattern}')")
        df = pd.read_csv(file_path, names=['Date', 'output'], header=0)       
        return df

class InflationTargetLoader(Loader):
    def load(self) -> pd.DataFrame:
        """Load inflation target data from a CSV file.
        
        only one file is expected to be found.
        """
        pattern = self.config['files_patterns']['inflation_target']
        file_path = self.folder_path + pattern
        if not file_path:
            raise FileNotFoundError(f"No inflation target CSV file found in the specified folder. (searched in: {self.folder_path} by pattern '{pattern}')")
        df = pd.read_csv(file_path, sep=",")       
        return df
    
class InflationLoader(Loader):
    def load(self) -> pd.DataFrame:
        """Load inflation data from a CSV file.
        
        only one file is expected to be found.
        """
        pattern = self.config['files_patterns']['inflation_data']
        file_path = self.folder_path + pattern
        if not file_path:
            raise FileNotFoundError(f"No inflation CSV file found in the specified folder. (searched in: {self.folder_path} by pattern '{pattern}')")
        df = pd.read_csv(file_path, sep=";")       
        return df