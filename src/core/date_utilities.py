"""
Elementary date utilities for futures contract handling.

This module provides low-level helper functions for date manipulation
and validation that can be used by date classes.
"""

import datetime
from typing import Optional
import calendar


def parse_date_string(date_str: str) -> tuple[int, int, Optional[int]]:
    """Parse date string into year, month, day components."""
    if len(date_str) == 6:  # YYYYMM
        try:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            return year, month, None
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
    
    elif len(date_str) == 8:  # YYYYMMDD
        try:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            return year, month, day
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
    
    else:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYYMM or YYYYMMDD")


def validate_date_components(year: int, month: int, day: Optional[int] = None) -> bool:
    """Validate date components for reasonableness."""
    if not 1990 <= year <= 2050:
        return False
    
    if not 1 <= month <= 12:
        return False
    
    if day is not None:
        try:
            datetime.date(year, month, day)
            return True
        except ValueError:
            return False
    
    return True


def is_business_day(date_obj: datetime.date) -> bool:
    """Check if date is a business day (Monday-Friday)."""
    return date_obj.weekday() < 5


def add_business_days(date_obj: datetime.date, days: int) -> datetime.date:
    """Add business days to a date."""
    current = date_obj
    remaining_days = abs(days)
    direction = 1 if days >= 0 else -1
    
    while remaining_days > 0:
        current += datetime.timedelta(days=direction)
        if is_business_day(current):
            remaining_days -= 1
    
    return current


def safe_date_creation(year: int, month: int, day: int) -> Optional[datetime.date]:
    """Safely create a date, returning None if invalid."""
    try:
        # Handle month boundary issues
        max_day = calendar.monthrange(year, month)[1]
        actual_day = min(day, max_day)
        return datetime.date(year, month, actual_day)
    except ValueError:
        return None