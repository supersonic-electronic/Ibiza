"""
Enterprise Logging System

A comprehensive, configurable logging system for the entire codebase.
Supports YAML configuration, multiple environments, and modular logging.
"""

import logging
import logging.handlers
import os
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import threading


# =============================================================================
# ENVIRONMENT AND CONFIGURATION
# =============================================================================

class Environment(Enum):
    """Supported application environments."""
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class LoggingConfig:
    """Manages loading and parsing of logging configuration files."""

    DEFAULT_CONFIG_DIR = "src/config"
    CONFIG_FILE_PATTERN = "logging_config.yaml"

    _config_cache = {}
    _cache_lock = threading.Lock()

    @classmethod
    def load_config(cls, environment: Environment, config_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Load logging configuration for specified environment.

        Args:
            environment: Target environment
            config_dir: Directory containing config files (uses default if None)

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        config_key = f"{environment.value}_{config_dir or cls.DEFAULT_CONFIG_DIR}"

        # Thread-safe config caching
        with cls._cache_lock:
            if config_key in cls._config_cache:
                return cls._config_cache[config_key]

        config_path = cls._resolve_config_path(environment, config_dir)

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                # Load all YAML documents (dev, test, prod sections)
                all_configs = list(yaml.safe_load_all(f))

                # Find the config for the specified environment
                config = cls._find_environment_config(all_configs, environment)

            # Validate configuration structure
            cls._validate_config(config)

            # Cache the configuration
            with cls._cache_lock:
                cls._config_cache[config_key] = config

            return config

        except FileNotFoundError:
            raise FileNotFoundError(f"Logging configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in logging configuration: {e}")

    @classmethod
    def _resolve_config_path(cls, environment: Environment, config_dir: Optional[str] = None) -> Path:
        """Resolve the path to the configuration file."""
        base_dir = Path(config_dir or cls.DEFAULT_CONFIG_DIR)
        return base_dir / cls.CONFIG_FILE_PATTERN

    @classmethod
    def _find_environment_config(cls, all_configs: List[Dict[str, Any]], environment: Environment) -> Dict[str, Any]:
        """Find configuration for specific environment from YAML documents."""
        # For single file with multiple environment sections
        # We'll look for environment-specific config in the YAML structure
        # This assumes the YAML has sections or we use the first config and adapt it

        if not all_configs:
            raise ValueError("No configuration found in YAML file")

        # For now, use the first config (you can extend this to handle multiple environments in one file)
        base_config = all_configs[0]

        # You could extend this to look for environment-specific overrides
        # For example: base_config.get(environment.value, base_config)

        return base_config

    @classmethod
    def _validate_config(cls, config: Dict[str, Any]) -> None:
        """Validate configuration structure."""
        if 'logging' not in config:
            raise ValueError("Configuration must contain 'logging' section")

        logging_config = config['logging']
        required_sections = ['global', 'handlers']

        for section in required_sections:
            if section not in logging_config:
                raise ValueError(f"Configuration must contain '{section}' section")

    @classmethod
    def get_module_config(cls, config: Dict[str, Any], module_name: str) -> Dict[str, Any]:
        """Get configuration for specific module."""
        modules_config = config.get('logging', {}).get('modules', {})
        return modules_config.get(module_name, {})

    @classmethod
    def clear_cache(cls) -> None:
        """Clear configuration cache (useful for testing)."""
        with cls._cache_lock:
            cls._config_cache.clear()


# =============================================================================
# ABSTRACT LOGGER INTERFACE
# =============================================================================

class Logger(ABC):
    """Abstract logger interface defining core logging methods."""

    @abstractmethod
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        pass

    @abstractmethod
    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        pass

    @abstractmethod
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        pass

    @abstractmethod
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        pass

    @abstractmethod
    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        pass


# =============================================================================
# BASE LOGGER IMPLEMENTATION
# =============================================================================

class BaseLogger(Logger):
    """
    Base logger implementation with configuration-driven setup.

    Provides common functionality for all loggers including:
    - YAML configuration loading
    - Handler management
    - Formatting
    - Environment awareness
    """

    def __init__(self,
                 name: str,
                 module_name: str,
                 environment: Environment = Environment.DEV,
                 config_dir: Optional[str] = None):
        """
        Initialize base logger.

        Args:
            name: Logger name (usually component/class name)
            module_name: Module name for module-specific config (required)
            environment: Target environment
            config_dir: Configuration directory
        """
        self.name = name
        self.environment = environment
        self.module_name = module_name

        # Load configuration
        self.config = LoggingConfig.load_config(environment, config_dir)

        # Create underlying Python logger
        self._logger = logging.getLogger(name)

        # Configure logger if not already configured
        if not self._logger.handlers:
            self._configure_logger()

    def _configure_logger(self) -> None:
        """Configure the logger based on loaded configuration."""
        # Get global and module-specific configurations
        global_config = self.config['logging']['global']
        module_config = LoggingConfig.get_module_config(self.config, self.module_name)

        # Determine effective configuration
        effective_config = self._merge_configs(global_config, module_config)

        # Set logger level
        level = self._parse_log_level(effective_config.get('level', 'INFO'))
        self._logger.setLevel(level)

        # Create and add handlers
        handler_names = effective_config.get('handlers', ['console', 'file'])
        for handler_name in handler_names:
            handler = self._create_handler(handler_name)
            if handler:
                self._logger.addHandler(handler)

        # Prevent propagation to avoid duplicate messages
        self._logger.propagate = False

    def _merge_configs(self, global_config: Dict[str, Any], module_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge global and module-specific configurations."""
        merged = global_config.copy()
        merged.update(module_config)
        return merged

    def _parse_log_level(self, level_str: str) -> int:
        """Parse log level string to logging constant."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level_str.upper(), logging.INFO)

    def _create_handler(self, handler_name: str) -> Optional[logging.Handler]:
        """Create handler based on configuration."""
        handlers_config = self.config['logging'].get('handlers', {})
        handler_config = handlers_config.get(handler_name, {})

        if not handler_config.get('enabled', False):
            return None

        handler = None

        if handler_name == 'console':
            handler = logging.StreamHandler()
        elif handler_name in ['file', 'error_file', 'critical_file']:
            handler = self._create_file_handler(handler_config)

        if handler:
            # Set level
            level = self._parse_log_level(handler_config.get('level', 'INFO'))
            handler.setLevel(level)

            # Set formatter
            format_str = handler_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            date_format = handler_config.get('date_format', '%Y-%m-%d %H:%M:%S')
            formatter = logging.Formatter(format_str, date_format)
            handler.setFormatter(formatter)

        return handler

    def _create_file_handler(self, handler_config: Dict[str, Any]) -> Optional[logging.Handler]:
        """Create rotating file handler."""
        log_path = Path(handler_config.get('path', 'logs/application.log'))

        # Ensure log directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Parse max size
        max_size = self._parse_file_size(handler_config.get('max_size', '10MB'))
        backup_count = handler_config.get('backup_count', 5)

        return logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )

    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string to bytes."""
        size_str = size_str.upper()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}

        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                number = size_str[:-len(suffix)]
                return int(float(number) * multiplier)

        # Default to bytes if no suffix
        return int(size_str)

    # Implementation of abstract methods
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        self._logger.exception(message, *args, **kwargs)


# =============================================================================
# LOGGER FACTORY
# =============================================================================

class LoggerFactory:
    """
    Factory for creating loggers throughout the application.

    Provides centralized logger creation with environment awareness
    and configuration management.
    """

    _current_environment = Environment.DEV
    _config_dir = None
    _logger_cache = {}
    _cache_lock = threading.Lock()

    @classmethod
    def set_environment(cls, environment: Environment) -> None:
        """Set global environment for all new loggers."""
        cls._current_environment = environment
        cls.clear_cache()  # Clear cache to force reconfiguration

    @classmethod
    def set_config_directory(cls, config_dir: str) -> None:
        """Set configuration directory for all new loggers."""
        cls._config_dir = config_dir
        cls.clear_cache()

    @classmethod
    def create_logger(cls,
                     name: str,
                     module_name: str,
                     environment: Optional[Environment] = None,
                     config_dir: Optional[str] = None) -> Logger:
        """
        Create a logger for the specified component.

        Args:
            name: Logger name (usually component/class name)
            module_name: Module name for specific configuration (required)
            environment: Environment (uses global if None)
            config_dir: Configuration directory (uses global if None)

        Returns:
            Configured Logger instance
        """
        # Use global settings if not specified
        env = environment or cls._current_environment
        cfg_dir = config_dir or cls._config_dir

        # Create cache key
        cache_key = f"{name}_{module_name}_{env.value}_{cfg_dir}"

        # Thread-safe logger caching
        with cls._cache_lock:
            if cache_key in cls._logger_cache:
                return cls._logger_cache[cache_key]

        # Create new logger
        logger = BaseLogger(
            name=name,
            module_name=module_name,
            environment=env,
            config_dir=cfg_dir
        )

        # Cache the logger
        with cls._cache_lock:
            cls._logger_cache[cache_key] = logger

        return logger

    @classmethod
    def get_logger_for_class(cls, class_instance, module_name: str, **kwargs) -> Logger:
        """
        Convenience method to create logger using class name.

        Args:
            class_instance: Instance of the class needing a logger
            module_name: Module name for configuration (required)
            **kwargs: Additional arguments for logger creation
        """
        return cls.create_logger(
            class_instance.__class__.__name__,
            module_name=module_name,
            **kwargs
        )

    @classmethod
    def clear_cache(cls) -> None:
        """Clear logger cache (useful for reconfiguration)."""
        with cls._cache_lock:
            cls._logger_cache.clear()

    @classmethod
    def configure_for_testing(cls) -> None:
        """Quick configuration for testing environments."""
        cls.set_environment(Environment.TEST)

    @classmethod
    def configure_for_production(cls, config_dir: str = "/etc/app/config") -> None:
        """Quick configuration for production environments."""
        cls.set_environment(Environment.PROD)
        cls.set_config_directory(config_dir)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_logger(name: str, module_name: str, **kwargs) -> Logger:
    """
    Convenience function to create a logger.

    Args:
        name: Logger name
        module_name: Module name for configuration (required)
        **kwargs: Additional arguments
    """
    return LoggerFactory.create_logger(name, module_name=module_name, **kwargs)


def get_class_logger(class_instance, module_name: str, **kwargs) -> Logger:
    """
    Convenience function to create logger for class instance.

    Args:
        class_instance: Instance of the class needing a logger
        module_name: Module name for configuration (required)
        **kwargs: Additional arguments
    """
    return LoggerFactory.get_logger_for_class(class_instance, module_name=module_name, **kwargs)


def set_global_environment(environment: str) -> None:
    """Set global logging environment from string."""
    try:
        env = Environment(environment.lower())
        LoggerFactory.set_environment(env)
    except ValueError:
        raise ValueError(f"Unknown environment: {environment}. Supported: {[e.value for e in Environment]}")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Example 1: Basic usage with explicit module name
    logger = LoggerFactory.create_logger("ExampleComponent", module_name="data_readers")
    logger.info("Basic logger created")

    # Example 2: Module-specific logger
    db_logger = LoggerFactory.create_logger("DatabaseManager", module_name="database")
    db_logger.info("Database logger with module-specific config")

    # Example 3: Class-based logger with explicit module
    class ExampleService:
        def __init__(self):
            self.log = LoggerFactory.get_logger_for_class(self, module_name="services")
            self.log.info("Service initialized")

        def do_work(self):
            self.log.debug("Starting work")
            self.log.info("Work completed successfully")

    service = ExampleService()
    service.do_work()

    # Example 4: Environment configuration
    LoggerFactory.set_environment(Environment.PROD)
    prod_logger = LoggerFactory.create_logger("ProductionComponent", module_name="production")
    prod_logger.warning("Production logger configured")

    # Example 5: Testing configuration
    LoggerFactory.configure_for_testing()
    test_logger = LoggerFactory.create_logger("TestComponent", module_name="testing")
    test_logger.error("Test environment configured")

    # Example 6: Using convenience functions
    conv_logger = get_logger("ConvenienceComponent", module_name="utilities")
    conv_logger.info("Created via convenience function")

    print("Enterprise logging system demonstration completed!")