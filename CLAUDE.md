# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Ibiza**, a Python financial data management system focused on futures contracts. It's built as an enterprise-grade modular system for managing, processing, and analyzing futures market data with sophisticated configuration management, logging, and data handling capabilities.

## Development Philosophy and Guidelines

### Code Development Principles

**Design Approach:**
- Use object-oriented programming with proper class definitions
- Start with abstract classes first, then implement more granular concrete classes
- Avoid coupling between components and utilize best coding practices
- Break down complex code into helper functions with minimal boilerplate inside classes
- Each function should generally do one thing (Single Responsibility Principle)
- Avoid coupling parameters inside functions/classes - define globally when possible
- Make comments concise and to the point

**Development Workflow:**
- Always ask before jumping into creating or refactoring code
- Before any major changes, ask 3 clarifying questions to understand requirements
- When making changes, specify which modules have been updated and how
- Do not try to predict future specific usage or needs if not specified
- Code should be extensible to add functionalities without knowing exact future requirements
- Configuration parameters should generally be contained in configuration files - ask before creating new ones
- Do not create sample data in examples unless explicitly requested

**Domain Understanding:**
- **Futures** = entire market (e.g., S&P 500 Future ES1)
- **Contract** = specific contract (e.g., December 2022 ES1 Futures Contract)
- The attached parquet files contain: individual futures contract prices, contract-specific data, and futures-specific data

## Development Environment

- **Language**: Python 3.13+
- **Dependency Management**: Poetry (pyproject.toml configuration)
- **Data Formats**: Primarily Parquet files, with support for CSV and ODS formats

## Common Development Commands

```bash
# Install dependencies
poetry install

# Run the main application
python main.py

# Run tests (basic test file exists)
python test.py

# Add new dependencies
poetry add <package-name>

# Update dependencies
poetry update
```

## Architecture Overview

### Current Implementation Status

**Note**: The system is in active development. Several core components referenced in `main.py` are not yet implemented:
- `src/config/config_manager.py` (missing)
- `src/data/futures_data_manager.py` (missing)
- `src/core/futures_objects.py` (empty - prototype objects exist in `test.py`)
- `src/core/constants.py` (empty)

### Core Components

1. **Configuration System** (`src/config/`)
   - **Multi-Environment Architecture**: Single YAML file with environment sections
   - **Hybrid Configuration**: Combines immutable constants with flexible external config
   - **Validation Framework**: `RollParameterConfig.validate()` enforces business rules
   - **Thread-Safe Caching**: Configuration and logger caching with invalidation
   - **config_objects.py**: Dataclass-based configuration structures with composition

2. **Enterprise Logging System** (`src/core/logger.py`)
   - **Abstract Factory Pattern**: `LoggerFactory` creates environment-specific loggers
   - **Strategy Pattern**: Environment configurations (dev/test/prod) with different strategies
   - **Template Method**: `BaseLogger` provides common template with environment overrides
   - **Multi-Format Support**: Console, file, and rotating file handlers
   - **Module-Specific Configuration**: Per-module logging overrides

3. **Data Management System** (`src/data/`)
   - **Abstract Factory Pattern**: `DataReaderFactory` creates format-specific readers
   - **Template Method Pattern**: `BaseDataReader` provides common functionality
   - **Strategy Pattern**: Format-specific readers (Parquet, CSV, ODS)
   - **Metadata Extraction**: Efficient file analysis without loading full datasets
   - **Path Resolution**: Cross-platform path handling with base directory context

4. **Core Utilities** (`src/core/`)
   - **utils.py**: Path handling, file operations, metadata extraction utilities
   - **logger.py**: Enterprise logging factory with environment-based configurations
   - **Domain Objects**: (To be implemented) Immutable dataclasses for futures and contracts

### Design Pattern Implementation

**Class Hierarchies:**
```
Logger (ABC)
├── BaseLogger (concrete template)
└── LoggerFactory (factory with caching)

DataReader (ABC)  
├── BaseDataReader (template implementation)
    ├── ParquetDataReader
    ├── CSVDataReader  
    └── ODSDataReader

Configuration Objects (dataclasses):
├── FilePatternConfig
├── DataQualityConfig
├── LoggingConfig  
├── RollParameterConfig (with validation)
└── EnvironmentConfig (composition root)
```

### Data Structure and Organization

**File Naming Conventions:**
- **Futures Data** (`data/futures/`): `{INSTRUMENT}_{TYPE}.parquet`
  - `{INSTRUMENT}_contract_data.parquet`: Contract-specific data
  - `{INSTRUMENT}_meta.parquet`: Futures metadata 
  - `{INSTRUMENT}_prices.parquet`: Price data
- **Holiday Data** (`data/holidays/`): `{EXCHANGE}holidays.parquet`

**Configuration Files:**
- `config/futures_config.yaml`: Environment settings, file patterns, data quality thresholds
- `config/roll_parameters.ods`: Roll parameters (Instrument, HoldRollCycle, PricedRollCycle, etc.)
- `src/config/logging_config.yaml`: Environment-specific logging configurations

### Error Handling Patterns

- **Graceful Degradation**: Optional dependency handling with fallbacks
- **Structured Error Reporting**: Standardized error dictionaries across formats  
- **Exception Chaining**: Context preservation with re-raising
- **Module-Specific Handling**: Environment-appropriate error management

### Business Domain Logic

**Futures Trading Domain:**
- Roll parameter validation enforcing financial market business rules
- Contract month representation with human-readable labels (`Mar 2026`)
- Instrument composition patterns with metadata aggregation
- Integration with financial market calendars

**Data Quality Framework:**
- Configurable thresholds for price observations, data gaps, volume requirements
- Data quality scoring system (partially implemented)
- File validation with existence and content checks

## Main Application Flow (When Complete)

1. Initialize `ConfigurationManager` with environment
2. Create `ConfigurableFuturesDataManager` 
3. Build inventory from data files using file patterns
4. Load roll parameters for instruments from ODS/CSV
5. Aggregate and save metadata with quality scoring

## Key Dependencies

- **pandas**: Data manipulation and file I/O
- **pyarrow**: Parquet file support with metadata extraction
- **pandas-market-calendars**: Financial market calendars and holiday handling
- **pyyaml**: YAML configuration parsing
- **odfpy/openpyxl**: ODS/Excel file support for roll parameters

## Development Notes

- System integrates with Bloomberg data (evident from ticker patterns like "ES1 Index")
- Production configuration expects logs in `/var/log/application/`
- Parquet files use Snappy compression by default for optimal storage
- Thread-safe operations throughout for enterprise deployment