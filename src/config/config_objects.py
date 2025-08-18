from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class FilePatternConfig:
    """File pattern configuration - can be overridden per environment"""
    meta_pattern: str = "*meta*.parquet"
    price_pattern: str = "*price*.parquet"
    contract_pattern: str = "*contract*.parquet"
    separator: str = "_"
    extension: str = ".parquet"


@dataclass
class DataQualityConfig:
    """Data quality thresholds - adjustable per environment"""
    min_price_observations: int = 20
    max_price_gap_days: int = 5
    min_volume_for_liquidity: int = 100
    max_missing_data_percent: float = 0.1
    min_data_quality_score: float = 0.7


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None


@dataclass
class RollParameterConfig:
    """Roll parameters for a specific instrument"""
    instrument_code: str
    hold_rollcycle: str
    priced_rollcycle: str
    roll_offset_days: int
    carry_offset: int
    expiry_offset: int

    def validate(self) -> List[str]:
        """Validate roll parameters"""
        issues = []
        if self.roll_offset_days > 0:
            issues.append(f"roll_offset_days should be negative or zero: {self.roll_offset_days}")
        if self.carry_offset not in [-1, 1]:
            issues.append(f"carry_offset should be -1 or 1: {self.carry_offset}")
        return issues


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    name: str
    data_path: str
    output_path: str
    file_patterns: FilePatternConfig = field(default_factory=FilePatternConfig)
    data_quality: DataQualityConfig = field(default_factory=DataQualityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Market-specific settings
    roll_parameters: Dict[str, RollParameterConfig] = field(default_factory=dict)
    instrument_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)