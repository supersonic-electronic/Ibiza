"""
Futures contract objects for the Ibiza system.

This module provides the FuturesContract class which combines
FuturesInstrument and ContractDate to represent complete futures contracts.
"""

from typing import Optional, Union, Dict, Any
from src.objects.instruments import FuturesInstrument
from src.objects.contract_dates import ContractDate, ExpiryDate, SingleContractDate
import datetime


class FuturesContract:
    """
    Represents a complete futures contract combining instrument and contract date.
    
    A futures contract consists of:
    - An instrument (e.g., ES1 for S&P 500 E-mini)
    - A contract date (e.g., 202403 for March 2024)
    
    Can handle both single contracts and spread contracts.
    """
    
    def __init__(self, instrument: Union[str, FuturesInstrument], 
                 contract_date: Union[str, list, ContractDate, SingleContractDate]):
        """
        Initialize a FuturesContract.
        
        Args:
            instrument: FuturesInstrument object or instrument code string
            contract_date: ContractDate object, date string, or list for spreads
            
        Examples:
            >>> contract = FuturesContract("ES1", "202403")
            >>> spread = FuturesContract("ES1", ["202403", "202406"])
        """
        # Handle instrument input
        if isinstance(instrument, str):
            self.instrument = FuturesInstrument(instrument)
        elif isinstance(instrument, FuturesInstrument):
            self.instrument = instrument
        else:
            raise ValueError(f"Invalid instrument type: {type(instrument)}")
        
        # Handle contract date input
        if isinstance(contract_date, (str, list)):
            self.contract_date = ContractDate(contract_date)
        elif isinstance(contract_date, SingleContractDate):
            self.contract_date = ContractDate(contract_date)
        elif isinstance(contract_date, ContractDate):
            self.contract_date = contract_date
        else:
            raise ValueError(f"Invalid contract_date type: {type(contract_date)}")
    
    @property
    def instrument_code(self) -> str:
        """Get the instrument code."""
        return self.instrument.instrument_code
    
    @property
    def date_str(self) -> str:
        """Get the contract date string representation."""
        return str(self.contract_date)
    
    @property
    def key(self) -> str:
        """
        Get the composite key for this contract.
        
        Format: "INSTRUMENT_CODE/DATE" for single contracts
        Format: "INSTRUMENT_CODE/DATE1-DATE2" for spread contracts
        
        Returns:
            Composite key string
            
        Examples:
            >>> contract = FuturesContract("ES1", "202403")
            >>> contract.key
            'ES1/202403'
            >>> spread = FuturesContract("ES1", ["202403", "202406"])
            >>> spread.key
            'ES1/202403-202406'
        """
        return f"{self.instrument_code}/{self.date_str}"
    
    @property
    def expiry_date(self) -> Optional[ExpiryDate]:
        """Get the expiry date (for single contracts only)."""
        if self.is_single_contract:
            return self.contract_date.single_contract_date.expiry_date
        return None
    
    @property
    def is_single_contract(self) -> bool:
        """Check if this is a single contract."""
        return self.contract_date.is_single_contract
    
    @property
    def is_spread_contract(self) -> bool:
        """Check if this is a spread contract."""
        return self.contract_date.is_spread_contract
    
    @property
    def is_monthly(self) -> bool:
        """Check if this is a monthly contract (single contract only)."""
        if self.is_single_contract:
            return self.contract_date.single_contract_date.is_monthly()
        return False
    
    @property
    def is_daily(self) -> bool:
        """Check if this is a daily/weekly contract (single contract only)."""
        if self.is_single_contract:
            return self.contract_date.single_contract_date.is_daily()
        return False
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Convert the contract to a dictionary representation.
        
        Returns:
            Dictionary containing instrument and contract date information
        """
        result = {
            'instrument_code': self.instrument_code,
            'contract_date': self.contract_date.as_dict()
        }
        return result
    
    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]) -> 'FuturesContract':
        """
        Create a FuturesContract from a dictionary.
        
        Args:
            data_dict: Dictionary containing contract data
            
        Returns:
            FuturesContract instance
        """
        instrument_code = data_dict['instrument_code']
        contract_date = ContractDate.from_dict(data_dict['contract_date'])
        
        return cls(instrument_code, contract_date)
    
    @classmethod
    def from_key(cls, key_string: str) -> 'FuturesContract':
        """
        Create a FuturesContract from a composite key string.
        
        Args:
            key_string: Composite key in format "INSTRUMENT/DATE" or "INSTRUMENT/DATE1-DATE2"
            
        Returns:
            FuturesContract instance
            
        Examples:
            >>> contract = FuturesContract.from_key("ES1/202403")
            >>> spread = FuturesContract.from_key("ES1/202403-202406")
        """
        if '/' not in key_string:
            raise ValueError(f"Invalid key format: {key_string}. Expected 'INSTRUMENT/DATE'")
        
        instrument_code, date_part = key_string.split('/', 1)
        
        # Handle spread contracts (contains '-')
        if '-' in date_part:
            date_parts = date_part.split('-')
            contract_date = date_parts
        else:
            contract_date = date_part
        
        return cls(instrument_code, contract_date)
    
    @classmethod
    def create_empty(cls) -> 'FuturesContract':
        """Create an empty futures contract."""
        return cls("", "")
    
    def is_empty(self) -> bool:
        """Check if this is an empty contract."""
        return self.instrument.is_empty and self.contract_date.is_empty()
    
    def as_key(self) -> str:
        """Get the composite key (alias for key property)."""
        return self.key
    
    def update_expiry_date(self, new_expiry: ExpiryDate) -> 'FuturesContract':
        """
        Create a new contract with updated expiry date.
        
        Args:
            new_expiry: New expiry date
            
        Returns:
            New FuturesContract instance with updated expiry
        """
        updated_contract_date = self.contract_date.update_expiry_date(new_expiry)
        return FuturesContract(self.instrument, updated_contract_date)
    
    def replace_instrument(self, new_instrument: Union[str, FuturesInstrument]) -> 'FuturesContract':
        """
        Create a new contract with a different instrument.
        
        Args:
            new_instrument: New instrument code or FuturesInstrument object
            
        Returns:
            New FuturesContract instance with different instrument
        """
        return FuturesContract(new_instrument, self.contract_date)
    
    def replace_contract_date(self, new_contract_date: Union[str, list, ContractDate]) -> 'FuturesContract':
        """
        Create a new contract with a different contract date.
        
        Args:
            new_contract_date: New contract date specification
            
        Returns:
            New FuturesContract instance with different date
        """
        return FuturesContract(self.instrument, new_contract_date)
    
    def next_contract(self, quarterly_only: bool = False) -> 'FuturesContract':
        """
        Get the next contract month.
        
        Args:
            quarterly_only: If True, jump to next quarterly month
            
        Returns:
            FuturesContract for next contract month
        """
        next_contract_date = self.contract_date.next_contract_month(quarterly_only)
        return FuturesContract(self.instrument, next_contract_date)
    
    def previous_contract(self, quarterly_only: bool = False) -> 'FuturesContract':
        """
        Get the previous contract month.
        
        Args:
            quarterly_only: If True, jump to previous quarterly month
            
        Returns:
            FuturesContract for previous contract month
        """
        prev_contract_date = self.contract_date.previous_contract_month(quarterly_only)
        return FuturesContract(self.instrument, prev_contract_date)
    
    def days_until_expiry(self, from_date: Optional[datetime.date] = None) -> Optional[int]:
        """
        Calculate days until expiry (for single contracts with known expiry).
        
        Args:
            from_date: Starting date (defaults to today)
            
        Returns:
            Number of days until expiry, or None if no expiry date
        """
        if self.is_single_contract:
            return self.contract_date.single_contract_date.days_until_expiry(from_date)
        return None
    
    def letter_month(self) -> str:
        """
        Get futures month letter for single contracts.
        
        Returns:
            Single letter futures month code
            
        Raises:
            ValueError: If this is a spread contract
        """
        if not self.is_single_contract:
            raise ValueError("Cannot get single letter month from spread contract")
        return self.contract_date.single_contract_date.letter_month()
    
    def letter_months(self) -> list[str]:
        """Get futures month letters for all contract dates."""
        return self.contract_date.letter_months()
    
    def approximate_expiry_date(self, offset_days: Optional[int] = None) -> Optional[ExpiryDate]:
        """
        Calculate approximate expiry date for single contracts.
        
        Args:
            offset_days: Days offset (uses contract's offset if not provided)
            
        Returns:
            Approximate ExpiryDate for single contracts, None for spreads
        """
        if self.is_single_contract:
            return self.contract_date.single_contract_date.approximate_expiry_date(offset_days)
        return None
    
    def __str__(self) -> str:
        """String representation using the composite key."""
        return self.key
    
    def __repr__(self) -> str:
        """Detailed representation of the contract."""
        return f"FuturesContract('{self.instrument_code}', '{self.date_str}')"
    
    def __eq__(self, other) -> bool:
        """Check equality based on instrument and contract date."""
        if not isinstance(other, FuturesContract):
            return False
        return (self.instrument == other.instrument and 
                self.contract_date == other.contract_date)
    
    def __hash__(self) -> int:
        """Make the contract hashable based on its key."""
        return hash(self.key)
    
    def __lt__(self, other) -> bool:
        """Enable sorting by instrument code then contract date."""
        if not isinstance(other, FuturesContract):
            return NotImplemented
        
        if self.instrument_code != other.instrument_code:
            return self.instrument_code < other.instrument_code
        
        # Compare by front contract date for spreads
        self_front = self.contract_date.front_contract
        other_front = other.contract_date.front_contract
        
        return (self_front.year, self_front.month, self_front.day or 0) < \
               (other_front.year, other_front.month, other_front.day or 0)
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        return self == other or self < other


class ListOfFutureContracts(list):
    """
    Extended list class specifically for handling FuturesContract objects.
    
    Provides contract-specific operations beyond standard list functionality.
    """
    
    def __init__(self, contracts=None):
        """
        Initialize list of futures contracts.
        
        Args:
            contracts: Optional initial list of FuturesContract objects
        """
        super().__init__()
        if contracts is not None:
            self.extend(contracts)
        self.validate()
    
    def validate(self) -> None:
        """Ensure all items are FuturesContract objects."""
        for item in self:
            if not isinstance(item, FuturesContract):
                raise ValueError(f"All items must be FuturesContract objects, got {type(item)}")
    
    def count_contracts(self) -> int:
        """Get the number of contracts in the list."""
        return len(self)
    
    def is_empty(self) -> bool:
        """Check if the list is empty."""
        return len(self) == 0
    
    def unique_instruments(self) -> list[str]:
        """
        Get unique instrument codes in the list.
        
        Returns:
            List of unique instrument codes
        """
        return list(set(contract.instrument_code for contract in self))
    
    def get_contract_dates(self) -> list[str]:
        """Get list of all contract date strings."""
        return [contract.date_str for contract in self]
    
    def get_instrument_codes(self) -> list[str]:
        """Get list of all instrument codes."""
        return [contract.instrument_code for contract in self]
    
    def get_keys(self) -> list[str]:
        """Get list of all contract keys."""
        return [contract.key for contract in self]
    
    def filter_by_instrument(self, instrument_code: str) -> 'ListOfFutureContracts':
        """
        Filter contracts by instrument code.
        
        Args:
            instrument_code: Instrument code to filter by
            
        Returns:
            New ListOfFutureContracts with matching contracts
        """
        filtered = [contract for contract in self if contract.instrument_code == instrument_code]
        return ListOfFutureContracts(filtered)
    
    def filter_by_instrument_as_list(self, instrument_code: str) -> list[FuturesContract]:
        """
        Filter contracts by instrument code, return as plain list.
        
        Args:
            instrument_code: Instrument code to filter by
            
        Returns:
            Plain Python list of matching FuturesContract objects
        """
        return [contract for contract in self if contract.instrument_code == instrument_code]
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> 'ListOfFutureContracts':
        """
        Filter contracts by date range (for single contracts).
        
        Args:
            start_date: Start date string (YYYYMM or YYYYMMDD)
            end_date: End date string (YYYYMM or YYYYMMDD)
            
        Returns:
            New ListOfFutureContracts with contracts in range
        """
        filtered = []
        for contract in self:
            if contract.is_single_contract:
                contract_date = contract.date_str
                if start_date <= contract_date <= end_date:
                    filtered.append(contract)
        return ListOfFutureContracts(filtered)
    
    def filter_by_date_range_as_list(self, start_date: str, end_date: str) -> list[FuturesContract]:
        """
        Filter contracts by date range, return as plain list.
        
        Args:
            start_date: Start date string (YYYYMM or YYYYMMDD)
            end_date: End date string (YYYYMM or YYYYMMDD)
            
        Returns:
            Plain Python list of matching FuturesContract objects
        """
        filtered = []
        for contract in self:
            if contract.is_single_contract:
                contract_date = contract.date_str
                if start_date <= contract_date <= end_date:
                    filtered.append(contract)
        return filtered
    
    def filter_single_contracts(self) -> 'ListOfFutureContracts':
        """Filter to only single contracts (no spreads)."""
        filtered = [contract for contract in self if contract.is_single_contract]
        return ListOfFutureContracts(filtered)
    
    def filter_single_contracts_as_list(self) -> list[FuturesContract]:
        """Filter to only single contracts, return as plain list."""
        return [contract for contract in self if contract.is_single_contract]
    
    def filter_spread_contracts(self) -> 'ListOfFutureContracts':
        """Filter to only spread contracts."""
        filtered = [contract for contract in self if contract.is_spread_contract]
        return ListOfFutureContracts(filtered)
    
    def filter_spread_contracts_as_list(self) -> list[FuturesContract]:
        """Filter to only spread contracts, return as plain list."""
        return [contract for contract in self if contract.is_spread_contract]
    
    def sort_by_date(self, reverse: bool = False) -> 'ListOfFutureContracts':
        """
        Sort contracts by date.
        
        Args:
            reverse: If True, sort in descending order
            
        Returns:
            New sorted ListOfFutureContracts
        """
        sorted_contracts = sorted(self, key=lambda x: x.contract_date.front_contract.as_date(), reverse=reverse)
        return ListOfFutureContracts(sorted_contracts)
    
    def sort_by_date_as_list(self, reverse: bool = False) -> list[FuturesContract]:
        """
        Sort contracts by date, return as plain list.
        
        Args:
            reverse: If True, sort in descending order
            
        Returns:
            Plain Python list of sorted FuturesContract objects
        """
        return sorted(self, key=lambda x: x.contract_date.front_contract.as_date(), reverse=reverse)
    
    def sort_by_instrument(self, reverse: bool = False) -> 'ListOfFutureContracts':
        """
        Sort contracts by instrument code then date.
        
        Args:
            reverse: If True, sort in descending order
            
        Returns:
            New sorted ListOfFutureContracts
        """
        sorted_contracts = sorted(self, reverse=reverse)  # Uses FuturesContract.__lt__
        return ListOfFutureContracts(sorted_contracts)
    
    def sort_by_instrument_as_list(self, reverse: bool = False) -> list[FuturesContract]:
        """
        Sort contracts by instrument code then date, return as plain list.
        
        Args:
            reverse: If True, sort in descending order
            
        Returns:
            Plain Python list of sorted FuturesContract objects
        """
        return sorted(self, reverse=reverse)  # Uses FuturesContract.__lt__
    
    def group_by_instrument(self) -> Dict[str, 'ListOfFutureContracts']:
        """
        Group contracts by instrument code.
        
        Returns:
            Dictionary with instrument codes as keys and ListOfFutureContracts as values
        """
        groups = {}
        for contract in self:
            instrument_code = contract.instrument_code
            if instrument_code not in groups:
                groups[instrument_code] = ListOfFutureContracts()
            groups[instrument_code].append(contract)
        return groups
    
    def as_dict(self) -> Dict[str, FuturesContract]:
        """
        Convert to dictionary with contract keys as keys.
        
        Returns:
            Dictionary keyed by contract keys
        """
        return {contract.key: contract for contract in self}
    
    @classmethod
    def from_dict(cls, contracts_dict: Dict[str, FuturesContract]) -> 'ListOfFutureContracts':
        """
        Create ListOfFutureContracts from dictionary.
        
        Args:
            contracts_dict: Dictionary of contract key -> FuturesContract
            
        Returns:
            ListOfFutureContracts instance
        """
        return cls(list(contracts_dict.values()))
    
    def unique(self) -> 'ListOfFutureContracts':
        """
        Remove duplicate contracts.
        
        Returns:
            New ListOfFutureContracts with unique contracts only
        """
        seen = set()
        unique_contracts = []
        for contract in self:
            if contract.key not in seen:
                seen.add(contract.key)
                unique_contracts.append(contract)
        return ListOfFutureContracts(unique_contracts)
    
    def difference(self, other_list: 'ListOfFutureContracts') -> 'ListOfFutureContracts':
        """
        Get contracts not in another list.
        
        Args:
            other_list: List to compare against
            
        Returns:
            New ListOfFutureContracts with contracts not in other_list
        """
        other_keys = set(contract.key for contract in other_list)
        filtered = [contract for contract in self if contract.key not in other_keys]
        return ListOfFutureContracts(filtered)
    
    def intersection(self, other_list: 'ListOfFutureContracts') -> 'ListOfFutureContracts':
        """
        Get contracts common to both lists.
        
        Args:
            other_list: List to intersect with
            
        Returns:
            New ListOfFutureContracts with common contracts
        """
        other_keys = set(contract.key for contract in other_list)
        filtered = [contract for contract in self if contract.key in other_keys]
        return ListOfFutureContracts(filtered)
    
    def union(self, other_list: 'ListOfFutureContracts') -> 'ListOfFutureContracts':
        """
        Combine unique contracts from both lists.
        
        Args:
            other_list: List to union with
            
        Returns:
            New ListOfFutureContracts with combined unique contracts
        """
        combined = ListOfFutureContracts(self)
        combined.extend(other_list)
        return combined.unique()
    
    def next_contracts(self, quarterly_only: bool = False) -> 'ListOfFutureContracts':
        """
        Get next contract months for all contracts.
        
        Args:
            quarterly_only: If True, jump to next quarterly months
            
        Returns:
            New ListOfFutureContracts with next contract months
        """
        next_contracts = [contract.next_contract(quarterly_only) for contract in self]
        return ListOfFutureContracts(next_contracts)
    
    def previous_contracts(self, quarterly_only: bool = False) -> 'ListOfFutureContracts':
        """
        Get previous contract months for all contracts.
        
        Args:
            quarterly_only: If True, jump to previous quarterly months
            
        Returns:
            New ListOfFutureContracts with previous contract months
        """
        prev_contracts = [contract.previous_contract(quarterly_only) for contract in self]
        return ListOfFutureContracts(prev_contracts)
    
    def remove_invalid(self) -> 'ListOfFutureContracts':
        """
        Remove any non-FuturesContract items.
        
        Returns:
            New ListOfFutureContracts with only valid contracts
        """
        valid = [item for item in self if isinstance(item, FuturesContract)]
        return ListOfFutureContracts(valid)
    
    def summary(self) -> str:
        """
        Get human-readable summary of the contract list.
        
        Returns:
            Summary string with counts and breakdown
        """
        if self.is_empty():
            return "Empty contract list"
        
        total = self.count_contracts()
        unique_insts = len(self.unique_instruments())
        single_count = len(self.filter_single_contracts())
        spread_count = len(self.filter_spread_contracts())
        
        summary_lines = [
            f"Contract List Summary:",
            f"  Total contracts: {total}",
            f"  Unique instruments: {unique_insts}",
            f"  Single contracts: {single_count}",
            f"  Spread contracts: {spread_count}"
        ]
        
        if unique_insts <= 10:  # Show instruments if not too many
            instruments = sorted(self.unique_instruments())
            summary_lines.append(f"  Instruments: {', '.join(instruments)}")
        
        return "\n".join(summary_lines)
    
    def __str__(self) -> str:
        """Compact string representation."""
        if self.is_empty():
            return "[]"
        
        if len(self) <= 5:
            keys = [contract.key for contract in self]
            return f"[{', '.join(keys)}]"
        else:
            first_few = [contract.key for contract in self[:3]]
            return f"[{', '.join(first_few)}, ... ({len(self)} total)]"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"ListOfFutureContracts({len(self)} contracts)"