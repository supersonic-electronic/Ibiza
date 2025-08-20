"""
Contract date objects for the Ibiza system.

This module provides date-related classes for futures contracts
including expiry dates and other contract-specific date handling.
"""

import datetime
from typing import Tuple, Optional, Union, List, Dict, Any
import calendar
from src.core.date_utilities import (
    parse_date_string, 
    validate_date_components, 
    is_business_day, 
    add_business_days,
    safe_date_creation
)


# Constant for when no expiry date is passed
NO_EXPIRY_DATE_PASSED = None

# Standard futures contract month codes
FUTURES_MONTH_CODES = {
    1: 'F',   # January
    2: 'G',   # February
    3: 'H',   # March
    4: 'J',   # April
    5: 'K',   # May
    6: 'M',   # June
    7: 'N',   # July
    8: 'Q',   # August
    9: 'U',   # September
    10: 'V',  # October
    11: 'X',  # November
    12: 'Z'   # December
}

# Reverse mapping for month codes to numbers
MONTH_CODE_TO_NUMBER = {v: k for k, v in FUTURES_MONTH_CODES.items()}

# Common futures trading months (quarterly cycles)
QUARTERLY_MONTHS = [3, 6, 9, 12]  # March, June, September, December


class ExpiryDate(datetime.datetime):
    """The actual date when a futures contract expires"""
    
    def as_tuple(self) -> Tuple[int, int, int]:
        """
        Return expiry date as a tuple of (year, month, day).
        
        Returns:
            Tuple containing (year, month, day)
        """
        return (self.year, self.month, self.day)
    
    @classmethod
    def from_str(cls, date_as_str: str) -> 'ExpiryDate':
        """
        Create ExpiryDate from string in YYYYMMDD format.
        
        Args:
            date_as_str: Date string in format "YYYYMMDD" (e.g., "20240315")
            
        Returns:
            ExpiryDate instance
            
        Example:
            >>> expiry = ExpiryDate.from_str("20240315")
            >>> expiry.year, expiry.month, expiry.day
            (2024, 3, 15)
        """
        as_date = datetime.datetime.strptime(date_as_str, "%Y%m%d")
        return cls(year=as_date.year, month=as_date.month, day=as_date.day)
    
    def as_str(self) -> str:
        """
        Convert expiry date to string in YYYYMMDD format.
        
        Returns:
            Date string in format "YYYYMMDD"
            
        Example:
            >>> expiry = ExpiryDate(2024, 3, 15)
            >>> expiry.as_str()
            '20240315'
        """
        return self.strftime("%Y%m%d")
    
    def __str__(self) -> str:
        """String representation using YYYYMMDD format."""
        return self.as_str()
    
    def __repr__(self) -> str:
        """Detailed representation of the ExpiryDate."""
        return f"ExpiryDate({self.year}, {self.month}, {self.day})"
    
    @classmethod
    def from_multiple_formats(cls, date_input: Union[str, datetime.date, datetime.datetime]) -> 'ExpiryDate':
        """
        Create ExpiryDate from multiple input formats.
        
        Args:
            date_input: Date in various formats (YYYYMMDD string, date, or datetime)
            
        Returns:
            ExpiryDate instance
        """
        if isinstance(date_input, str):
            return cls.from_str(date_input)
        elif isinstance(date_input, (datetime.date, datetime.datetime)):
            return cls(year=date_input.year, month=date_input.month, day=date_input.day)
        else:
            raise ValueError(f"Unsupported date input type: {type(date_input)}")
    
    def letter_month(self) -> str:
        """
        Get futures contract month letter code.
        
        Returns:
            Single letter futures month code (F, G, H, etc.)
            
        Example:
            >>> expiry = ExpiryDate(2024, 3, 15)
            >>> expiry.letter_month()
            'H'
        """
        return FUTURES_MONTH_CODES[self.month]
    
    def is_business_day(self) -> bool:
        """Check if this expiry date falls on a business day."""
        return is_business_day(self.date())
    
    def next_business_day(self) -> 'ExpiryDate':
        """Get the next business day after this expiry date."""
        next_bday = add_business_days(self.date(), 1)
        return ExpiryDate(next_bday.year, next_bday.month, next_bday.day)
    
    def previous_business_day(self) -> 'ExpiryDate':
        """Get the previous business day before this expiry date."""
        prev_bday = add_business_days(self.date(), -1)
        return ExpiryDate(prev_bday.year, prev_bday.month, prev_bday.day)
    
    def days_until_expiry(self, from_date: Optional[datetime.date] = None) -> int:
        """
        Calculate days until expiry.
        
        Args:
            from_date: Starting date (defaults to today)
            
        Returns:
            Number of days until expiry (negative if past)
        """
        if from_date is None:
            from_date = datetime.date.today()
        
        delta = self.date() - from_date
        return delta.days


class SingleContractDate:
    """
    A single contract identifier like '202403' (March 2024)
    Can be YYYYMM (monthly) or YYYYMMDD (daily/weekly)
    """
    
    def __init__(self, date_str: str, 
                 expiry_date: Optional[ExpiryDate] = NO_EXPIRY_DATE_PASSED,
                 approx_expiry_offset: int = 0):
        """
        Initialize a SingleContractDate.
        
        Args:
            date_str: Contract date identifier
                     - "202403" for March 2024 contract (monthly)
                     - "20240315" for specific date contract (daily/weekly)
            expiry_date: Optional actual expiry date for the contract
            approx_expiry_offset: Days offset for approximate expiry calculation
        """
        self._date_str = self._normalize_date_str(date_str)
        self._expiry_date = expiry_date
        self._approx_expiry_offset = approx_expiry_offset
    
    def _normalize_date_str(self, date_str: str) -> str:
        """
        Normalize date string format.
        
        Args:
            date_str: Input date string
            
        Returns:
            Normalized date string
            - "202403" becomes "20240300" (monthly contracts get trailing zeros)
            - "20240315" stays "20240315" (daily contracts unchanged)
        """
        if len(date_str) == 6:  # YYYYMM format (monthly)
            return date_str + "00"  # Add trailing zeros
        elif len(date_str) == 8:  # YYYYMMDD format (daily/weekly)
            return date_str
        else:
            raise ValueError(f"Invalid date string format: {date_str}. Expected YYYYMM or YYYYMMDD")
    
    @property
    def date_str(self) -> str:
        """Get the normalized date string."""
        return self._date_str
    
    @property
    def original_format(self) -> str:
        """
        Get the original format without trailing zeros.
        
        Returns:
            Original format string (YYYYMM for monthly, YYYYMMDD for daily)
        """
        if self._date_str.endswith("00"):
            return self._date_str[:-2]  # Remove trailing zeros for monthly
        return self._date_str
    
    @property
    def expiry_date(self) -> Optional[ExpiryDate]:
        """Get the expiry date if set."""
        return self._expiry_date
    
    @property
    def approx_expiry_offset(self) -> int:
        """Get the approximate expiry offset in days."""
        return self._approx_expiry_offset
    
    def is_monthly(self) -> bool:
        """Check if this is a monthly contract (ends with 00)."""
        return self._date_str.endswith("00")
    
    def is_daily(self) -> bool:
        """Check if this is a daily/weekly contract (specific date)."""
        return not self.is_monthly()
    
    def __str__(self) -> str:
        """String representation using original format."""
        return self.original_format
    
    def __repr__(self) -> str:
        """Detailed representation of the SingleContractDate."""
        return f"SingleContractDate('{self.original_format}')"
    
    def __eq__(self, other) -> bool:
        """Check equality based on normalized date string."""
        if not isinstance(other, SingleContractDate):
            return False
        return self._date_str == other._date_str
    
    def __hash__(self) -> int:
        """Make the contract date hashable."""
        return hash(self._date_str)
    
    @property
    def year(self) -> int:
        """Get the contract year."""
        return int(self._date_str[:4])
    
    @property 
    def month(self) -> int:
        """Get the contract month."""
        return int(self._date_str[4:6])
    
    @property
    def day(self) -> Optional[int]:
        """Get the contract day (None for monthly contracts)."""
        if self.is_monthly():
            return None
        return int(self._date_str[6:8])
    
    def letter_month(self) -> str:
        """
        Get futures contract month letter code.
        
        Returns:
            Single letter futures month code (F, G, H, etc.)
            
        Example:
            >>> contract = SingleContractDate("202403")
            >>> contract.letter_month()
            'H'
        """
        return FUTURES_MONTH_CODES[self.month]
    
    def as_date(self) -> datetime.date:
        """
        Convert to datetime.date object.
        
        For monthly contracts, uses the 1st of the month.
        
        Returns:
            datetime.date representation
            
        Example:
            >>> monthly = SingleContractDate("202403")
            >>> monthly.as_date()
            datetime.date(2024, 3, 1)
        """
        if self.is_monthly():
            return datetime.date(self.year, self.month, 1)
        else:
            return datetime.date(self.year, self.month, self.day)
    
    def quarter(self) -> int:
        """
        Get the quarter for this contract.
        
        Returns:
            Quarter number (1-4)
            
        Example:
            >>> contract = SingleContractDate("202403")  # March
            >>> contract.quarter()
            1
        """
        return (self.month - 1) // 3 + 1
    
    def is_quarterly_month(self) -> bool:
        """Check if this contract is in a quarterly month."""
        return self.month in QUARTERLY_MONTHS
    
    def is_valid_contract_month(self, quarterly_only: bool = False) -> bool:
        """
        Check if this is a valid contract month.
        
        Args:
            quarterly_only: If True, only allow quarterly months
            
        Returns:
            True if valid contract month
        """
        if quarterly_only:
            return self.is_quarterly_month()
        return 1 <= self.month <= 12
    
    def next_contract_month(self, quarterly_only: bool = False) -> 'SingleContractDate':
        """
        Get the next contract month.
        
        Args:
            quarterly_only: If True, jump to next quarterly month
            
        Returns:
            SingleContractDate for next contract month
        """
        next_month = self.month + 1
        next_year = self.year
        
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        if quarterly_only:
            while next_month not in QUARTERLY_MONTHS:
                next_month += 1
                if next_month > 12:
                    next_month = 1
                    next_year += 1
        
        next_date_str = f"{next_year:04d}{next_month:02d}"
        return SingleContractDate(
            next_date_str,
            expiry_date=self._expiry_date,
            approx_expiry_offset=self._approx_expiry_offset
        )
    
    def previous_contract_month(self, quarterly_only: bool = False) -> 'SingleContractDate':
        """
        Get the previous contract month.
        
        Args:
            quarterly_only: If True, jump to previous quarterly month
            
        Returns:
            SingleContractDate for previous contract month
        """
        prev_month = self.month - 1
        prev_year = self.year
        
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        
        if quarterly_only:
            while prev_month not in QUARTERLY_MONTHS:
                prev_month -= 1
                if prev_month < 1:
                    prev_month = 12
                    prev_year -= 1
        
        prev_date_str = f"{prev_year:04d}{prev_month:02d}"
        return SingleContractDate(
            prev_date_str,
            expiry_date=self._expiry_date,
            approx_expiry_offset=self._approx_expiry_offset
        )
    
    def approximate_expiry_date(self, offset_days: Optional[int] = None) -> ExpiryDate:
        """
        Calculate approximate expiry date.
        
        Args:
            offset_days: Days offset (uses instance offset if not provided)
            
        Returns:
            Approximate ExpiryDate
        """
        if offset_days is None:
            offset_days = self._approx_expiry_offset
        
        if offset_days == 0:
            offset_days = 15  # Default to middle of month
        
        # Ensure we don't exceed month boundaries
        max_day = calendar.monthrange(self.year, self.month)[1]
        actual_day = min(offset_days, max_day)
        
        return ExpiryDate(self.year, self.month, actual_day)
    
    def days_until_expiry(self, from_date: Optional[datetime.date] = None) -> Optional[int]:
        """
        Calculate days until expiry if expiry date is known.
        
        Args:
            from_date: Starting date (defaults to today)
            
        Returns:
            Number of days until expiry, or None if no expiry date set
        """
        if self._expiry_date is None:
            return None
        
        if from_date is None:
            from_date = datetime.date.today()
        
        delta = self._expiry_date.date() - from_date
        return delta.days
    
    @classmethod
    def from_components(cls, year: int, month: int, day: Optional[int] = None, 
                       expiry_date: Optional[ExpiryDate] = NO_EXPIRY_DATE_PASSED,
                       approx_expiry_offset: int = 0) -> 'SingleContractDate':
        """
        Create SingleContractDate from year/month/day components.
        
        Args:
            year: Contract year
            month: Contract month
            day: Contract day (None for monthly contracts)
            expiry_date: Optional expiry date
            approx_expiry_offset: Approximate expiry offset
            
        Returns:
            SingleContractDate instance
        """
        if not validate_date_components(year, month, day):
            raise ValueError(f"Invalid date components: {year}-{month}-{day}")
        
        if day is None:
            date_str = f"{year:04d}{month:02d}"
        else:
            date_str = f"{year:04d}{month:02d}{day:02d}"
        
        return cls(date_str, expiry_date, approx_expiry_offset)


class ContractDate:
    """
    Comprehensive contract date class supporting single and spread contracts.
    
    This class can handle:
    - Single contracts: ContractDate("202403") or ContractDate("20240315")
    - Spread contracts: ContractDate(["202403", "202406"])
    - Complex contract specifications with expiry dates and offsets
    """
    
    def __init__(self, contract_date_input, 
                 expiry_date: Optional[ExpiryDate] = NO_EXPIRY_DATE_PASSED,
                 approx_expiry_offset: int = 0):
        """
        Initialize a ContractDate.
        
        Args:
            contract_date_input: Can be:
                - str: Single contract date ("202403", "20240315")
                - SingleContractDate: Existing single contract
                - list: Multiple contract dates for spreads
            expiry_date: Optional expiry date
            approx_expiry_offset: Approximate expiry offset in days
        """
        self._contract_dates = self._parse_input(contract_date_input, expiry_date, approx_expiry_offset)
        self._expiry_date = expiry_date
        self._approx_expiry_offset = approx_expiry_offset
    
    def _parse_input(self, contract_input, expiry_date, approx_expiry_offset) -> List[SingleContractDate]:
        """Parse various input formats into list of SingleContractDate objects."""
        if isinstance(contract_input, str):
            # Single contract string
            return [SingleContractDate(contract_input, expiry_date, approx_expiry_offset)]
        
        elif isinstance(contract_input, SingleContractDate):
            # Single contract object
            return [contract_input]
        
        elif isinstance(contract_input, list):
            # Multiple contracts (spread)
            result = []
            for item in contract_input:
                if isinstance(item, str):
                    result.append(SingleContractDate(item, expiry_date, approx_expiry_offset))
                elif isinstance(item, SingleContractDate):
                    result.append(item)
                else:
                    raise ValueError(f"Invalid contract date item in list: {type(item)}")
            return result
        
        else:
            raise ValueError(f"Invalid contract date input type: {type(contract_input)}")
    
    @property
    def is_single_contract(self) -> bool:
        """Check if this represents a single contract."""
        return len(self._contract_dates) == 1
    
    @property
    def is_spread_contract(self) -> bool:
        """Check if this represents a spread contract."""
        return len(self._contract_dates) > 1
    
    @property
    def contract_dates(self) -> List[SingleContractDate]:
        """Get all contract dates."""
        return self._contract_dates.copy()
    
    @property
    def single_contract_date(self) -> SingleContractDate:
        """
        Get single contract date.
        
        Returns:
            SingleContractDate if this is a single contract
            
        Raises:
            ValueError: If this is a spread contract
        """
        if not self.is_single_contract:
            raise ValueError("Cannot get single contract date from spread contract")
        return self._contract_dates[0]
    
    @property
    def front_contract(self) -> SingleContractDate:
        """Get the front (earliest) contract."""
        return min(self._contract_dates, key=lambda x: (x.year, x.month, x.day or 0))
    
    @property
    def back_contract(self) -> SingleContractDate:
        """Get the back (latest) contract."""
        return max(self._contract_dates, key=lambda x: (x.year, x.month, x.day or 0))
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with contract date information
        """
        result = {
            'contract_dates': [cd.original_format for cd in self._contract_dates],
            'is_single': self.is_single_contract,
            'is_spread': self.is_spread_contract
        }
        
        if self._expiry_date is not None:
            result['expiry_date'] = self._expiry_date.as_str()
        
        if self._approx_expiry_offset != 0:
            result['approx_expiry_offset'] = self._approx_expiry_offset
            
        return result
    
    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]) -> 'ContractDate':
        """
        Create ContractDate from dictionary.
        
        Args:
            data_dict: Dictionary containing contract date data
            
        Returns:
            ContractDate instance
        """
        contract_dates = data_dict['contract_dates']
        
        # Handle single contract vs spread
        if len(contract_dates) == 1:
            contract_input = contract_dates[0]
        else:
            contract_input = contract_dates
        
        # Parse expiry date if present
        expiry_date = NO_EXPIRY_DATE_PASSED
        if 'expiry_date' in data_dict:
            expiry_date = ExpiryDate.from_str(data_dict['expiry_date'])
        
        approx_expiry_offset = data_dict.get('approx_expiry_offset', 0)
        
        return cls(contract_input, expiry_date, approx_expiry_offset)
    
    @classmethod
    def create_empty(cls) -> 'ContractDate':
        """Create an empty contract date."""
        return cls("")
    
    def is_empty(self) -> bool:
        """Check if this is an empty contract."""
        return len(self._contract_dates) == 1 and self._contract_dates[0].original_format == ""
    
    def update_expiry_date(self, new_expiry: ExpiryDate) -> 'ContractDate':
        """
        Create new ContractDate with updated expiry date.
        
        Args:
            new_expiry: New expiry date
            
        Returns:
            New ContractDate instance with updated expiry
        """
        # Create new contract dates with updated expiry
        updated_contracts = []
        for cd in self._contract_dates:
            updated_contracts.append(
                SingleContractDate(
                    cd.original_format, 
                    new_expiry, 
                    cd.approx_expiry_offset
                )
            )
        
        return ContractDate(updated_contracts, new_expiry, self._approx_expiry_offset)
    
    def letter_months(self) -> List[str]:
        """Get futures month letters for all contracts."""
        return [cd.letter_month() for cd in self._contract_dates]
    
    def years(self) -> List[int]:
        """Get years for all contracts."""
        return [cd.year for cd in self._contract_dates]
    
    def months(self) -> List[int]:
        """Get months for all contracts."""
        return [cd.month for cd in self._contract_dates]
    
    def as_spread_string(self, separator: str = "-") -> str:
        """
        Get string representation for spread contracts.
        
        Args:
            separator: Character to separate contract dates
            
        Returns:
            Spread string representation
            
        Example:
            >>> spread = ContractDate(["202403", "202406"])
            >>> spread.as_spread_string()
            '202403-202406'
        """
        return separator.join(cd.original_format for cd in self._contract_dates)
    
    def expiry_dates(self) -> List[Optional[ExpiryDate]]:
        """Get expiry dates for all contracts."""
        return [cd.expiry_date for cd in self._contract_dates]
    
    def days_until_expiry(self, from_date: Optional[datetime.date] = None) -> List[Optional[int]]:
        """Get days until expiry for all contracts."""
        return [cd.days_until_expiry(from_date) for cd in self._contract_dates]
    
    def next_contract_month(self, quarterly_only: bool = False) -> 'ContractDate':
        """
        Get next contract month(s).
        
        Args:
            quarterly_only: If True, jump to quarterly months only
            
        Returns:
            ContractDate with next contract months
        """
        next_contracts = [cd.next_contract_month(quarterly_only) for cd in self._contract_dates]
        return ContractDate(next_contracts, self._expiry_date, self._approx_expiry_offset)
    
    def previous_contract_month(self, quarterly_only: bool = False) -> 'ContractDate':
        """
        Get previous contract month(s).
        
        Args:
            quarterly_only: If True, jump to quarterly months only
            
        Returns:
            ContractDate with previous contract months
        """
        prev_contracts = [cd.previous_contract_month(quarterly_only) for cd in self._contract_dates]
        return ContractDate(prev_contracts, self._expiry_date, self._approx_expiry_offset)
    
    def sort_contracts(self, reverse: bool = False) -> 'ContractDate':
        """
        Sort contracts by date.
        
        Args:
            reverse: If True, sort in descending order
            
        Returns:
            New ContractDate with sorted contracts
        """
        sorted_contracts = sorted(
            self._contract_dates, 
            key=lambda x: (x.year, x.month, x.day or 0),
            reverse=reverse
        )
        return ContractDate(sorted_contracts, self._expiry_date, self._approx_expiry_offset)
    
    def __str__(self) -> str:
        """String representation."""
        if self.is_single_contract:
            return self._contract_dates[0].original_format
        else:
            return self.as_spread_string()
    
    def __repr__(self) -> str:
        """Detailed representation."""
        if self.is_single_contract:
            return f"ContractDate('{self._contract_dates[0].original_format}')"
        else:
            contract_strs = [cd.original_format for cd in self._contract_dates]
            return f"ContractDate({contract_strs})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on contract dates."""
        if not isinstance(other, ContractDate):
            return False
        return self._contract_dates == other._contract_dates
    
    def __hash__(self) -> int:
        """Make hashable."""
        return hash(tuple(cd.original_format for cd in self._contract_dates))
    
    def __len__(self) -> int:
        """Get number of contracts."""
        return len(self._contract_dates)
    
    def __getitem__(self, index: int) -> SingleContractDate:
        """Get contract by index."""
        return self._contract_dates[index]
    
    def __iter__(self):
        """Iterate over contracts."""
        return iter(self._contract_dates)