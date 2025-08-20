"""
Dictionary for futures contract prices.

This module provides dictionary classes for storing and manipulating
futures contract price data with DataFrame values.
"""

import pandas as pd
from typing import List, Optional, Union, Dict, Any


class DictFutureContractPrices(dict):
    """
    Dictionary of futures contract prices with DataFrame values.
    
    Structure: {contract_date_string: DataFrame with BID/ASK/FINAL_PRICE columns}
    
    Example:
        {
            '20240300': DataFrame with columns [BID, ASK, FINAL_PRICE] and date index,
            '20240600': DataFrame with columns [BID, ASK, FINAL_PRICE] and date index
        }
    
    Inherits from dict and adds contract-specific price manipulation methods.
    """
    
    def __repr__(self):
        """String representation showing number of contracts."""
        object_repr = f"Dict of futures contract prices with {len(self.keys())} contracts"
        return object_repr
    
    def sorted_contract_date_str(self) -> List[str]:
        """
        Get contract date strings sorted chronologically.
        
        Returns:
            List of contract date strings sorted by date
        """
        try:
            all_contract_date_str_sorted = getattr(self, "_all_contract_date_str_sorted")
        except AttributeError:
            all_contract_date_str_sorted = self._get_and_set_sorted_contract_date_str()
        
        return all_contract_date_str_sorted
    
    def _get_and_set_sorted_contract_date_str(self) -> List[str]:
        """Calculate and cache sorted contract date strings."""
        contract_date_strs = list(self.keys())
        contract_date_strs_sorted = sorted(contract_date_strs)
        self._all_contract_date_str_sorted = contract_date_strs_sorted
        
        return contract_date_strs_sorted
    
    def last_contract_date_str(self) -> Optional[str]:
        """
        Get the latest contract date string.
        
        Returns:
            Latest contract date string, or None if empty
        """
        sorted_dates = self.sorted_contract_date_str()
        if sorted_dates:
            return sorted_dates[-1]
        return None
    
    def first_contract_date_str(self) -> Optional[str]:
        """
        Get the earliest contract date string.
        
        Returns:
            Earliest contract date string, or None if empty
        """
        sorted_dates = self.sorted_contract_date_str()
        if sorted_dates:
            return sorted_dates[0]
        return None
    
    def joint_data(self, price_type: str = 'FINAL_PRICE') -> pd.DataFrame:
        """
        Create DataFrame with specified price type for all contracts.
        
        Args:
            price_type: Column to extract ('FINAL_PRICE', 'BID', 'ASK')
            
        Returns:
            DataFrame with dates as index and contract date strings as columns
        """
        series_list = []
        
        for contract_date_str in self.sorted_contract_date_str():
            contract_df = self[contract_date_str]
            if price_type in contract_df.columns:
                price_series = contract_df[price_type].copy()
                price_series.name = contract_date_str
                series_list.append(price_series)
        
        if series_list:
            joint_data = pd.concat(series_list, axis=1)
            return joint_data.sort_index()
        else:
            return pd.DataFrame()
    
    def matched_prices(self, contracts_to_match: Optional[List[str]] = None, 
                      price_type: str = 'FINAL_PRICE') -> pd.DataFrame:
        """
        Return DataFrame where we only have prices for all specified contracts.
        
        Args:
            contracts_to_match: List of contract date strings to match, or None for all
            price_type: Column to extract ('FINAL_PRICE', 'BID', 'ASK')
            
        Returns:
            DataFrame with matched price data (no NaN values)
            
        Raises:
            ValueError: If no matched data is found
        """
        if contracts_to_match is None:
            contracts_to_match = list(self.keys())
        
        joint_data = self.joint_data(price_type)
        
        # Filter to only requested contracts
        available_contracts = [c for c in contracts_to_match if c in joint_data.columns]
        if not available_contracts:
            raise ValueError("No matching contracts found in price data")
        
        joint_data_to_match = joint_data[available_contracts]
        matched_data = joint_data_to_match.dropna()
        
        if len(matched_data) == 0:
            raise ValueError("No overlapping price data found for specified contracts")
        
        return matched_data
    
    def final_prices(self) -> pd.DataFrame:
        """
        Get final prices for all contracts.
        
        Returns:
            DataFrame with dates as index and contract date strings as columns
        """
        return self.joint_data('FINAL_PRICE')
    
    def bid_prices(self) -> pd.DataFrame:
        """
        Get bid prices for all contracts.
        
        Returns:
            DataFrame with dates as index and contract date strings as columns
        """
        return self.joint_data('BID')
    
    def ask_prices(self) -> pd.DataFrame:
        """
        Get ask prices for all contracts.
        
        Returns:
            DataFrame with dates as index and contract date strings as columns
        """
        return self.joint_data('ASK')
    
    def get_contract_prices(self, contract_date_str: str) -> pd.DataFrame:
        """
        Get full price DataFrame for a specific contract.
        
        Args:
            contract_date_str: Contract date string (e.g., '20240300')
            
        Returns:
            DataFrame with BID/ASK/FINAL_PRICE columns
        """
        if contract_date_str not in self:
            raise KeyError(f"Contract {contract_date_str} not found in price data")
        
        return self[contract_date_str].copy()
    
    def get_latest_prices(self, price_type: str = 'FINAL_PRICE') -> pd.Series:
        """
        Get the most recent price for each contract.
        
        Args:
            price_type: Column to extract ('FINAL_PRICE', 'BID', 'ASK')
            
        Returns:
            Series with contract date strings as index and latest prices as values
        """
        latest_prices = {}
        
        for contract_date_str, contract_df in self.items():
            if not contract_df.empty and price_type in contract_df.columns:
                # Get latest date for this contract
                latest_price = contract_df[price_type].iloc[-1]  # Assuming sorted by date
                latest_prices[contract_date_str] = latest_price
        
        return pd.Series(latest_prices, name=f'latest_{price_type.lower()}')
    
    def get_date_range(self) -> tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
        """
        Get overall date range across all contracts.
        
        Returns:
            Tuple of (earliest_date, latest_date) or (None, None) if empty
        """
        all_dates = []
        for contract_df in self.values():
            if not contract_df.empty:
                all_dates.extend(contract_df.index.tolist())
        
        if all_dates:
            return min(all_dates), max(all_dates)
        return None, None
    
    def filter_by_date_range(self, start_date: Union[str, pd.Timestamp], 
                           end_date: Union[str, pd.Timestamp]) -> 'DictFutureContractPrices':
        """
        Filter price data to only include dates within range.
        
        Args:
            start_date: Start date 
            end_date: End date
            
        Returns:
            New DictFutureContractPrices with filtered data
        """
        filtered = DictFutureContractPrices()
        
        for contract_date_str, contract_df in self.items():
            if not contract_df.empty:
                mask = (contract_df.index >= start_date) & (contract_df.index <= end_date)
                filtered_df = contract_df.loc[mask]
                
                if not filtered_df.empty:
                    filtered[contract_date_str] = filtered_df
        
        return filtered
    
    def summary_stats(self, price_type: str = 'FINAL_PRICE') -> pd.DataFrame:
        """
        Get summary statistics for each contract.
        
        Args:
            price_type: Column to analyze ('FINAL_PRICE', 'BID', 'ASK')
            
        Returns:
            DataFrame with summary statistics for each contract
        """
        stats_data = []
        
        for contract_date_str in self.sorted_contract_date_str():
            contract_df = self[contract_date_str]
            if not contract_df.empty and price_type in contract_df.columns:
                price_series = contract_df[price_type]
                stats = {
                    'contract': contract_date_str,
                    'count': len(price_series),
                    'mean': price_series.mean(),
                    'std': price_series.std(),
                    'min': price_series.min(),
                    'max': price_series.max(),
                    'first_date': price_series.index.min(),
                    'last_date': price_series.index.max()
                }
                stats_data.append(stats)
        
        return pd.DataFrame(stats_data)
    
    def has_bid_ask_data(self) -> bool:
        """
        Check if any bid/ask data is available.
        
        Returns:
            True if BID or ASK columns exist and have data
        """
        for contract_df in self.values():
            if not contract_df.empty:
                if 'BID' in contract_df.columns and contract_df['BID'].notna().any():
                    return True
                if 'ASK' in contract_df.columns and contract_df['ASK'].notna().any():
                    return True
        return False
    
    def count_total_observations(self) -> int:
        """
        Count total number of price observations across all contracts.
        
        Returns:
            Total number of price data points
        """
        total = 0
        for contract_df in self.values():
            total += len(contract_df)
        return total
    
    def add_contract_prices(self, contract_date_str: str, price_df: pd.DataFrame) -> None:
        """
        Add price DataFrame for a contract.
        
        Args:
            contract_date_str: Contract date string (e.g., '20240300')
            price_df: DataFrame with BID/ASK/FINAL_PRICE columns and date index
        """
        # Ensure the DataFrame has the expected columns
        expected_columns = ['BID', 'ASK', 'FINAL_PRICE']
        for col in expected_columns:
            if col not in price_df.columns:
                price_df[col] = None
        
        # Store a copy to avoid reference issues
        self[contract_date_str] = price_df.copy()
        
        # Clear cached sorted list
        if hasattr(self, '_all_contract_date_str_sorted'):
            delattr(self, '_all_contract_date_str_sorted')