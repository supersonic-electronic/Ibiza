"""
Future instrument objects for the Ibiza system.

This module provides the FuturesInstrument class which represents
a futures instrument (e.g., ES1, CL1) with associated metadata and operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


META_FIELD_LIST = [
    'future_ticker',
    'future_asset_class',
    'future_exchange_id',
    'future_trade_months',
    'future_contract_size',
    'future_tick_size',
    'future_tick_value',
    'future_price_multiplier',
    'future_nominal_contract_value',
    'future_first_trade_date',
    'future_trading_hours',
    'future_currency',
    'future_number_ticks'
]


@dataclass
class FuturesInstrumentMetaData:
    """
    Metadata for a futures instrument containing contract specifications.
    
    This dataclass holds essential information about futures contracts
    including pricing, sizing, and trading specifications.
    """
    future_ticker: str
    future_asset_class: str
    future_exchange_id: str
    future_trade_months: str
    future_contract_size: float
    future_tick_size: float
    future_tick_value: float
    future_price_multiplier: float
    future_nominal_contract_value: float
    future_first_trade_date: datetime
    future_trading_hours: str
    future_currency: str
    future_number_ticks: float
    
    def as_dict(self) -> dict:
        """
        Convert the metadata to a dictionary representation.
        
        Uses META_FIELD_LIST to ensure proper field order.
        
        Returns:
            Dictionary of metadata fields in META_FIELD_LIST order
        """
        keys = META_FIELD_LIST
        self_as_dict = dict([(key, getattr(self, key)) for key in keys])
        return self_as_dict
    
    @classmethod
    def from_dict(cls, input_dict: Dict[str, Any]) -> 'FuturesInstrumentMetaData':
        """
        Create a FuturesInstrumentMetaData instance from a dictionary.
        
        Args:
            input_dict: Dictionary containing metadata fields with keys matching META_FIELD_LIST
            
        Returns:
            FuturesInstrumentMetaData instance
        """
        keys = META_FIELD_LIST
        args_list = [input_dict[key] for key in keys]
        return cls(*args_list)


class FuturesInstrument:
    """
    Represents a futures instrument in the trading system.
    
    A futures instrument is a standardized contract specification
    (e.g., S&P 500 futures represented as ES1).
    """
    
    def __init__(self, instrument_code: str, **kwargs):
        """
        Initialize a FutureInstrument.
        
        Args:
            instrument_code: The unique identifier for the instrument (e.g., 'ES1')
            **kwargs: Additional attributes to store on the instrument
        """
        self._instrument_code = instrument_code.upper() if instrument_code else ''
        self._attributes = kwargs
    
    @classmethod
    def create_from_dict(cls, data_dict: Dict[str, Any]) -> 'FuturesInstrument':
        """
        Create a FutureInstrument from a dictionary.
        
        Args:
            data_dict: Dictionary containing instrument data
            
        Returns:
            FutureInstrument instance
            
        Raises:
            ValueError: If instrument_code is not provided in the dictionary
        """
        if 'instrument_code' not in data_dict:
            raise ValueError("Dictionary must contain 'instrument_code' key")
        
        data_copy = data_dict.copy()
        instrument_code = data_copy.pop('instrument_code')
        return cls(instrument_code=instrument_code, **data_copy)
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Convert the FutureInstrument to a dictionary representation.
        
        Returns:
            Dictionary containing all instrument attributes
        """
        result = {'instrument_code': self._instrument_code}
        result.update(self._attributes)
        return result
    
    @classmethod
    def empty(cls) -> 'FuturesInstrument':
        """
        Create an empty FutureInstrument instance.
        
        Returns:
            FutureInstrument with empty string as instrument_code
        """
        return cls(instrument_code='')
    
    @property
    def instrument_code(self) -> str:
        """Get the instrument code."""
        return self._instrument_code
    
    @property
    def key(self) -> str:
        """
        Get the unique key for this instrument.
        
        For now, this is the same as instrument_code but could be
        extended in the future to include exchange or other identifiers.
        """
        return self._instrument_code
    
    @property
    def is_empty(self) -> bool:
        """Check if this is an empty instrument."""
        return self._instrument_code == ''
    
    def __str__(self) -> str:
        """String representation of the instrument."""
        return f"FuturesInstrument({self._instrument_code})"
    
    def __repr__(self) -> str:
        """Detailed representation of the instrument."""
        attrs = ', '.join(f"{k}={v!r}" for k, v in self._attributes.items())
        if attrs:
            return f"FuturesInstrument(instrument_code={self._instrument_code!r}, {attrs})"
        return f"FuturesInstrument(instrument_code={self._instrument_code!r})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on instrument code."""
        if not isinstance(other, FuturesInstrument):
            return False
        return self._instrument_code == other._instrument_code
    
    def __hash__(self) -> int:
        """Make the instrument hashable based on its code."""
        return hash(self._instrument_code)
    
    def get(self, attribute: str, default: Any = None) -> Any:
        """
        Get an attribute value with a default fallback.
        
        Args:
            attribute: The attribute name to retrieve
            default: Default value if attribute doesn't exist
            
        Returns:
            The attribute value or default
        """
        if attribute == 'instrument_code':
            return self._instrument_code
        return self._attributes.get(attribute, default)
    
    def has_attribute(self, attribute: str) -> bool:
        """
        Check if the instrument has a specific attribute.
        
        Args:
            attribute: The attribute name to check
            
        Returns:
            True if the attribute exists
        """
        return attribute == 'instrument_code' or attribute in self._attributes


@dataclass
class FuturesInstrumentWithMetaData:
    """
    Composite class combining a FutureInstrument with its metadata.
    
    This class provides a unified interface for accessing both the instrument
    identification and its detailed contract specifications.
    """
    instrument: FuturesInstrument
    meta_data: FuturesInstrumentMetaData
    
    @property
    def instrument_code(self) -> str:
        """Get the instrument code from the underlying instrument."""
        return self.instrument.instrument_code
    
    @property
    def key(self) -> str:
        """Get the unique key for this instrument (same as instrument_code)."""
        return self.instrument_code
    
    def as_dict(self) -> dict:
        """
        Convert to dictionary representation.
        
        Combines metadata fields with instrument_code.
        
        Returns:
            Dictionary with all metadata fields plus instrument_code
        """
        meta_data_dict = self.meta_data.as_dict()
        meta_data_dict["instrument_code"] = self.instrument_code
        return meta_data_dict
    
    @classmethod
    def from_dict(cls, input_dict: Dict[str, Any]) -> 'FuturesInstrumentWithMetaData':
        """
        Create instance from dictionary.
        
        Args:
            input_dict: Dictionary containing instrument_code and metadata fields
            
        Returns:
            FuturesInstrumentWithMetaData instance
        """
        # Create a copy to avoid modifying the original
        dict_copy = input_dict.copy()
        instrument_code = dict_copy.pop("instrument_code")
        
        instrument = FuturesInstrument(instrument_code)
        meta_data = FuturesInstrumentMetaData.from_dict(dict_copy)
        
        return cls(instrument, meta_data)
    
    @classmethod
    def create_empty(cls) -> 'FuturesInstrumentWithMetaData':
        """
        Create an empty instance.
        
        Returns:
            FuturesInstrumentWithMetaData with empty instrument and default metadata
        """
        instrument = FuturesInstrument.empty()
        meta_data = FuturesInstrumentMetaData()
        
        return cls(instrument, meta_data)
    
    def empty(self) -> bool:
        """Check if this is an empty instrument."""
        return self.instrument.is_empty
    
    def __eq__(self, other) -> bool:
        """
        Check equality based on both instrument and metadata.
        
        Args:
            other: Another FuturesInstrumentWithMetaData instance
            
        Returns:
            True if both instrument and metadata match
        """
        if not isinstance(other, FuturesInstrumentWithMetaData):
            return False
            
        instrument_matches = self.instrument == other.instrument
        meta_data_matches = self.meta_data == other.meta_data
        
        return instrument_matches and meta_data_matches