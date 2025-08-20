# Ibiza - Futures Data Management System

A Python financial data management system focused on futures contracts, built as an enterprise-grade modular system for managing, processing, and analyzing futures market data.

## Overview

Ibiza provides sophisticated configuration management, logging, and data handling capabilities for futures trading operations. The system is designed with enterprise-grade patterns and supports multiple data formats including Parquet, CSV, and ODS files.

**Architectural Inspiration**: This project draws inspiration from [pysystemtrade](https://github.com/robcarver17/pysystemtrade/) while implementing a custom system tailored to specific requirements.

## Key Features

- **Multi-Environment Configuration**: Single YAML file with environment-specific sections
- **Enterprise Logging System**: Factory pattern with environment-based configurations
- **Flexible Data Management**: Support for Parquet, CSV, and ODS formats
- **Financial Domain Logic**: Futures and contract management with roll parameter validation
- **Thread-Safe Operations**: Caching and configuration management for enterprise deployment

## Quick Start

### Prerequisites

- Python 3.13+
- Poetry for dependency management

### Installation

```bash
# Clone the repository
git clone https://github.com/supersonic-electronic/Ibiza.git
cd Ibiza

# Install dependencies
poetry install
```

### Running the Application

```bash
# Run the main application
python main.py

# Run tests
python test.py
```

## Architecture

### Core Components

1. **Configuration System** (`src/config/`)
   - Multi-environment YAML configuration
   - Dataclass-based configuration objects
   - Validation framework for business rules

2. **Logging System** (`src/core/logger.py`)
   - Abstract factory pattern for environment-specific loggers
   - Multiple output formats (console, file, rotating)
   - Module-specific configuration overrides

3. **Data Management** (`src/data/`)
   - Abstract factory for format-specific readers
   - Metadata extraction without full dataset loading
   - Cross-platform path handling

4. **Domain Objects** (`src/objects/`)
   - Futures and contract representations
   - Roll parameter management
   - Financial market calendar integration

### Design Patterns

- **Abstract Factory**: Logger and data reader creation
- **Template Method**: Base classes with environment overrides
- **Strategy Pattern**: Format-specific implementations
- **Composition**: Configuration object hierarchies

## Data Structure

### File Organization

```
data/
├── futures/
│   ├── {INSTRUMENT}_contract_data.parquet
│   ├── {INSTRUMENT}_meta.parquet
│   └── {INSTRUMENT}_prices.parquet
└── holidays/
    └── {EXCHANGE}holidays.parquet

config/
├── futures_config.yaml
├── roll_parameters.ods
└── logging_config.yaml
```

### Supported Formats

- **Parquet**: Primary format with Snappy compression
- **CSV**: Legacy data support
- **ODS**: Roll parameter configuration

## Development

### Project Structure

```
src/
├── config/          # Configuration management
├── core/            # Core utilities and logging
├── data/            # Data readers and managers
└── objects/         # Domain objects

docs/                # Documentation and diagrams
tests/               # Test files
```

### Development Commands

```bash
# Add new dependency
poetry add <package-name>

# Update dependencies
poetry update

# Run with specific environment
ENVIRONMENT=dev python main.py
```

## Configuration

The system uses environment-based configuration:

- **Development**: Console logging, debug level
- **Testing**: File logging, structured output
- **Production**: Rotating logs in `/var/log/application/`

Configuration is managed through YAML files with validation and caching.

## Financial Domain

### Futures vs Contracts

- **Futures**: Entire market (e.g., S&P 500 Future ES1)
- **Contract**: Specific contract (e.g., December 2022 ES1 Futures Contract)

### Data Integration

- Bloomberg data integration (ticker patterns like "ES1 Index")
- Financial market calendars and holiday handling
- Roll parameter validation with business rules

## Dependencies

- **pandas**: Data manipulation and file I/O
- **pyarrow**: Parquet file support
- **pandas-market-calendars**: Financial market calendars
- **pyyaml**: YAML configuration parsing
- **odfpy/openpyxl**: ODS/Excel file support

## License

This project is proprietary software. All rights reserved.

## Contributing

This is a private project. Please contact the maintainers for contribution guidelines.