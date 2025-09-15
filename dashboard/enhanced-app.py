#!/usr/bin/env python3
"""
Enhanced Flask web server for the Ibiza Interactive Dashboard.
Bloomberg-inspired design with advanced theming and interactive features.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from flask import Flask, render_template_string, render_template, send_from_directory, redirect, url_for, jsonify, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for importing Ibiza modules
sys.path.insert(0, os.path.abspath('..'))

# Try to import Ibiza data readers
try:
    from src.data.data_readers import DataReaderFactory
except ImportError:
    print("Warning: Could not import Ibiza data readers. Some features may not work.")
    DataReaderFactory = None

app = Flask(__name__)

# Base data directory
DATA_DIR = Path('../data')
FUTURES_PRICE_DIR = DATA_DIR / 'futures' / 'contract_prices'
FUTURES_META_DIR = DATA_DIR / 'futures' / 'unmerged_meta'

# Market descriptions mapping
def get_market_description(symbol):
    """Get descriptive name for futures markets"""
    descriptions = {
        'ES1': 'S&P 500 E-mini',
        'NQ1': 'NASDAQ 100 E-mini',
        'RTY1': 'Russell 2000 E-mini',
        'YM1': 'Dow Jones E-mini',
        'CL1': 'Crude Oil WTI',
        'GC1': 'Gold',
        'SI1': 'Silver',
        'NG1': 'Natural Gas',
        'HG1': 'Copper',
        'ZB1': '30-Year T-Bond',
        'ZN1': '10-Year T-Note',
        'ZF1': '5-Year T-Note',
        'C 1': 'Corn',
        'S 1': 'Soybeans',
        'W 1': 'Wheat',
        'KC1': 'Coffee',
        'CT1': 'Cotton',
        'SB1': 'Sugar',
        'CC1': 'Cocoa',
        'PA1': 'Palladium',
        'PL1': 'Platinum',
        'LA1': 'Aluminum',
        '6E1': 'Euro FX',
        '6J1': 'Japanese Yen',
        '6B1': 'British Pound',
        '6S1': 'Swiss Franc',
        '6C1': 'Canadian Dollar',
        '6A1': 'Australian Dollar',
        'DX1': 'US Dollar Index',
        'VIX1': 'VIX Volatility',
        'BTC1': 'Bitcoin',
        'ETH1': 'Ethereum'
    }
    return descriptions.get(symbol, f'{symbol} Future')

# Enhanced Dashboard HTML template with Bloomberg-inspired design
ENHANCED_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ibiza - Enhanced Interactive Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/enhanced-dashboard.css') }}?v=2">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <meta name="description" content="Ibiza Financial Data Management System - Interactive Dashboard for Futures Trading Analysis">
    <meta name="author" content="Ibiza Development Team">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E📊%3C/text%3E%3C/svg%3E">
</head>
<body>
    <div class="dashboard-container">
        
        <!-- Enhanced Sidebar -->
        <aside class="dashboard-sidebar">

            <!-- Navigation Menu -->
            <div class="sidebar-section">
                <h3 class="sidebar-title">
                    <i class="fas fa-compass"></i>
                    Navigation
                </h3>
                <nav class="navigation-menu">
                    <ul>
                        <li class="nav-item">
                            <a href="#" class="nav-link active" data-section="overview">
                                <i class="nav-icon fas fa-tachometer-alt"></i>
                                <span>Overview</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="#" class="nav-link" data-section="modules">
                                <i class="nav-icon fas fa-cubes"></i>
                                <span>Modules</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="#" class="nav-link" data-section="commands">
                                <i class="nav-icon fas fa-terminal"></i>
                                <span>Commands</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="#" class="nav-link" data-section="notebooks">
                                <i class="nav-icon fas fa-book"></i>
                                <span>Notebooks</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="#" class="nav-link" data-section="architecture">
                                <i class="nav-icon fas fa-sitemap"></i>
                                <span>Architecture</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="/query" class="nav-link">
                                <i class="nav-icon fas fa-search"></i>
                                <span>Data Query</span>
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>

            <!-- System Status -->
            <div class="sidebar-section">
                <h3 class="sidebar-title">
                    <i class="fas fa-heartbeat"></i>
                    System Status
                </h3>
                <div class="status-indicators">
                    <div class="status-item">
                        <span class="status-label">Data Readers</span>
                        <span class="status-badge status-implemented">
                            <i class="fas fa-check-circle"></i>
                            Active
                        </span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Futures Data</span>
                        <span class="status-badge status-implemented">
                            <i class="fas fa-database"></i>
                            146 Instruments
                        </span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Configuration</span>
                        <span class="status-badge status-partial">
                            <i class="fas fa-cog"></i>
                            Partial
                        </span>
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="sidebar-section">
                <h3 class="sidebar-title">
                    <i class="fas fa-rocket"></i>
                    Quick Actions
                </h3>
                <div class="quick-actions">
                    <a href="/jupyter" class="btn btn-primary btn-sm">
                        <i class="fas fa-play"></i>
                        Launch Jupyter
                    </a>
                    <a href="/status" class="btn btn-secondary btn-sm">
                        <i class="fas fa-info-circle"></i>
                        System Info
                    </a>
                </div>
            </div>
        </aside>

        <!-- Enhanced Header -->
        <header class="dashboard-header">
            <div class="header-content">
                <div class="header-brand">
                    <div class="brand-logo">
                        <img src="{{ url_for('static', filename='images/ibiza.png') }}" 
                             alt="Ibiza Alpha Detection System" 
                             class="logo-image"
                             width="200" 
                             height="auto">
                    </div>
                    <div class="brand-text">
                        <h1 class="header-title gradient-text">
                            <span class="brand-name">IBIZA</span>
                            <span class="brand-tagline">ALPHA DETECTION SYSTEM</span>
                        </h1>
                        <p class="header-subtitle">
                            Advanced Futures Trading Analysis & Management Platform
                        </p>
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-bar glass-effect">
                        <div class="progress-fill">
                            <i class="fas fa-rocket"></i>
                            45% Complete
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Enhanced Main Content -->
        <main class="dashboard-main">
            
            <!-- Overview Section -->
            <section id="overview" class="content-section active">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-chart-bar"></i>
                        System Overview
                    </h2>
                    <p class="section-subtitle">
                        Complete view of the Ibiza financial data management system capabilities
                    </p>
                </div>

                <!-- Theme Selection Section -->
                <div class="theme-selection-section">
                    <h3 class="theme-section-title">
                        <i class="fas fa-palette"></i>
                        Choose Your Experience
                    </h3>
                    <div class="theme-switcher-grid">
                        <div class="theme-option theme-ibiza active" data-theme="ibiza">
                            <div class="theme-preview"></div>
                            <span>🏝️ Ibiza</span>
                            <div class="theme-description">Official brand theme with teal accents</div>
                        </div>
                        <div class="theme-option theme-midnight" data-theme="midnight">
                            <div class="theme-preview"></div>
                            <span>🌙 Midnight</span>
                            <div class="theme-description">Dark blue professional theme</div>
                        </div>
                        <div class="theme-option theme-light" data-theme="light">
                            <div class="theme-preview"></div>
                            <span>☀️ Light</span>
                            <div class="theme-description">Clean bright interface</div>
                        </div>
                        <div class="theme-option theme-terminal" data-theme="terminal">
                            <div class="theme-preview"></div>
                            <span>💻 Terminal</span>
                            <div class="theme-description">Classic green on black</div>
                        </div>
                        <div class="theme-option theme-dark" data-theme="dark">
                            <div class="theme-preview"></div>
                            <span>🌚 Dark</span>
                            <div class="theme-description">Modern dark interface</div>
                        </div>
                    </div>
                </div>

                <div class="card-grid">
                    <div class="card floating">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-chart-pie"></i>
                                Project Status
                            </h3>
                            <span class="status-badge status-partial">
                                <i class="fas fa-clock"></i>
                                In Progress
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Enterprise-grade financial data management system for futures contracts with comprehensive analytics and visualization capabilities.</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-check"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">146 Futures Instruments Loaded</div>
                                        <div class="feature-description">Complete Bloomberg ticker format dataset</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-check"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Multi-format Data Readers</div>
                                        <div class="feature-description">Parquet, CSV, and ODS support</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-check"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Enterprise Logging System</div>
                                        <div class="feature-description">Environment-aware logging with caching</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-check"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Domain Objects & Validation</div>
                                        <div class="feature-description">Type-safe financial instrument modeling</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card floating">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-database"></i>
                                Data Inventory
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-check-circle"></i>
                                Fully Loaded
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Complete futures market data with Bloomberg ticker format covering major global markets:</p>
                            <div class="code-container">
                                <div class="code-header">
                                    <div class="code-language">
                                        <i class="fas fa-chart-line"></i>
                                        <span>Futures Tickers</span>
                                    </div>
                                    <button class="copy-button">
                                        <i class="fas fa-copy"></i>
                                        Copy
                                    </button>
                                </div>
                                <pre class="code-block"><code># Example Bloomberg tickers:
ES1 Index     # S&P 500 Futures
CL1 Comdty    # Crude Oil Futures
GC1 Comdty    # Gold Futures
NQ1 Index     # Nasdaq Futures</code></pre>
                            </div>
                        </div>
                    </div>

                    <div class="card floating">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-rocket"></i>
                                Quick Start
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-play"></i>
                                Ready
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Launch interactive environments and explore system capabilities:</p>
                        </div>
                        <div class="card-footer">
                            <a href="/jupyter" class="btn btn-primary" target="_blank">
                                <i class="fas fa-play"></i>
                                Launch Jupyter Lab
                            </a>
                            <a href="/status" class="btn btn-secondary">
                                <i class="fas fa-info-circle"></i>
                                System Status
                            </a>
                        </div>
                    </div>

                    <div class="card floating">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-cogs"></i>
                                Architecture Highlights
                            </h3>
                            <span class="status-badge status-info">
                                <i class="fas fa-code"></i>
                                Advanced
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Modern Python architecture with proven design patterns:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-layer-group"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Factory Pattern</div>
                                        <div class="feature-description">DataReaderFactory, LoggerFactory</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-sitemap"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Template Method</div>
                                        <div class="feature-description">BaseDataReader, BaseLogger</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-puzzle-piece"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Strategy Pattern</div>
                                        <div class="feature-description">Environment configurations</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Modules Section -->
            <section id="modules" class="content-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-cubes"></i>
                        Module Overview
                    </h2>
                    <p class="section-subtitle">
                        Detailed breakdown of implemented and pending system components
                    </p>
                </div>

                <div class="card-grid">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-file-alt"></i>
                                📊 Data Readers
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-check-circle"></i>
                                Implemented
                            </span>
                        </div>
                        <div class="card-content">
                            <p><strong>src/data/data_readers.py</strong></p>
                            <p>Multi-format data reading with factory pattern implementation:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-file"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="🔧 Key Methods:

📄 read_file(file_path) → DataFrame
   Load parquet file into pandas DataFrame

📊 get_metadata(file_path) → dict
   Extract file metadata without loading

✅ _validate_file(file_path) → bool
   Validate parquet file format

🗂️ _extract_schema() → dict
   Get column schema information">ParquetDataReader</div>
                                        <div class="feature-description">High-performance columnar storage</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-file-csv"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="🔧 Key Methods:

📄 read_file(file_path) → DataFrame
   Parse CSV files into pandas DataFrame

🔍 get_delimiter() → str
   Auto-detect CSV delimiter character

📋 _parse_header() → list
   Extract and validate column headers

🏷️ _infer_types() → dict
   Auto-detect column data types">CSVDataReader</div>
                                        <div class="feature-description">Universal text format support</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-file-excel"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="🔧 Key Methods:

📄 read_file(file_path) → DataFrame
   Load OpenDocument spreadsheet files

📋 get_sheets() → list
   List available worksheet names

📊 read_sheet(sheet_name) → DataFrame
   Load specific worksheet data

🧮 _parse_formulas() → dict
   Extract and evaluate formulas">ODSDataReader</div>
                                        <div class="feature-description">OpenDocument spreadsheet format</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-industry"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="Key Methods:
get_reader(format_type) → BaseDataReader
register_reader(format, class) → None
list_formats() → list
_validate_format() → bool">DataReaderFactory</div>
                                        <div class="feature-description">Unified creation interface</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/01_data_exploration.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-play"></i>
                                Demo Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-file-code"></i>
                                📝 Logger System
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-check-circle"></i>
                                Implemented
                            </span>
                        </div>
                        <div class="card-content">
                            <p><strong>src/core/logger.py</strong></p>
                            <p>Enterprise logging with environment configurations:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-factory"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="Key Methods:
get_logger(name) → Logger
set_environment(env) → None
clear_cache() → None
_create_logger() → Logger">LoggerFactory with Caching</div>
                                        <div class="feature-description">Thread-safe logger instances</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-cogs"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="Environment Configs:
DevLogger → console + debug
TestLogger → file + warning
ProdLogger → rotating + error
_setup_handlers() → list">Environment Strategies</div>
                                        <div class="feature-description">dev/test/prod configurations</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-sliders-h"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="Override Methods:
set_level(module, level) → None
add_handler(module, handler) → None
override_format(module, fmt) → None
_apply_overrides() → None">Module-specific Overrides</div>
                                        <div class="feature-description">Granular logging control</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-stream"></i>
                                    <div class="feature-content">
                                        <div class="feature-title method-tooltip" data-methods="Handler Types:
StreamHandler → console output
FileHandler → static log files
RotatingFileHandler → size-based
TimedRotatingFileHandler → time">Multiple Output Handlers</div>
                                        <div class="feature-description">Console, file, rotating handlers</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/03_module_testing.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-play"></i>
                                Demo Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-sliders-h"></i>
                                ⚙️ Configuration Objects
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-check-circle"></i>
                                Implemented
                            </span>
                        </div>
                        <div class="card-content">
                            <p><strong>src/config/config_objects.py</strong></p>
                            <p>Dataclass-based configuration with validation:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-exchange-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">RollParameterConfig</div>
                                        <div class="feature-description">Contract rolling parameters</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-check-double"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">DataQualityConfig</div>
                                        <div class="feature-description">Data validation thresholds</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-file-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">LoggingConfig</div>
                                        <div class="feature-description">Logging behavior settings</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-layer-group"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">EnvironmentConfig</div>
                                        <div class="feature-description">Composition root configuration</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/04_roll_parameters.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-play"></i>
                                Demo Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-building"></i>
                                🏦 Domain Objects
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-check-circle"></i>
                                Implemented
                            </span>
                        </div>
                        <div class="card-content">
                            <p><strong>src/objects/</strong></p>
                            <p>Financial instrument representations with type safety:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-coins"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">FuturesInstrument</div>
                                        <div class="feature-description">Immutable instrument objects</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-file-contract"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">FuturesContract</div>
                                        <div class="feature-description">Contract-specific data handling</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-chart-line"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">DictFutureContractPrices</div>
                                        <div class="feature-description">Price data dictionary with contract keys</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-calendar-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">ContractDateAndRollCycle</div>
                                        <div class="feature-description">Contract lifecycle management</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/02_price_analysis.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-play"></i>
                                Demo Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-tools"></i>
                                🛠️ Utilities
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-check-circle"></i>
                                Implemented
                            </span>
                        </div>
                        <div class="card-content">
                            <p><strong>src/core/utils.py</strong></p>
                            <p>Helper functions and utilities for system operations:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-folder-open"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Path Resolution</div>
                                        <div class="feature-description">Cross-platform path handling</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-file-import"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">File Operations</div>
                                        <div class="feature-description">Safe file manipulation utilities</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-info-circle"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Metadata Extraction</div>
                                        <div class="feature-description">File analysis without loading</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-clock"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Date Utilities</div>
                                        <div class="feature-description">Financial calendar operations</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/03_module_testing.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-play"></i>
                                Demo Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-exclamation-triangle"></i>
                                ❌ Configuration Manager
                            </h3>
                            <span class="status-badge status-missing">
                                <i class="fas fa-times-circle"></i>
                                Not Implemented
                            </span>
                        </div>
                        <div class="card-content">
                            <p><strong>src/config/config_manager.py</strong></p>
                            <p>Centralized configuration management (pending implementation):</p>
                            <div class="feature-list" style="opacity: 0.6;">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-file-code"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">YAML File Loading</div>
                                        <div class="feature-description">Configuration file parsing</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-exchange-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Environment Switching</div>
                                        <div class="feature-description">Dynamic environment configs</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-shield-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Configuration Validation</div>
                                        <div class="feature-description">Schema enforcement</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-sync-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Dynamic Reloading</div>
                                        <div class="feature-description">Hot configuration updates</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Commands Section -->
            <section id="commands" class="content-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-terminal"></i>
                        Commands & Examples
                    </h2>
                    <p class="section-subtitle">
                        Ready-to-use code examples for all implemented functionality
                    </p>
                </div>

                <div class="command-section">
                    <h3>Data Reading Examples</h3>
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-file-alt"></i>
                                    Read Parquet Files
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="code-container">
                                    <div class="code-header">
                                        <div class="code-language">
                                            <i class="fab fa-python"></i>
                                            <span>Python</span>
                                        </div>
                                        <button class="copy-button">
                                            <i class="fas fa-copy"></i>
                                            Copy
                                        </button>
                                    </div>
                                    <pre class="code-block"><code>from src.data.data_readers import DataReaderFactory

# Create reader instance
reader = DataReaderFactory.get_reader('parquet')

# Read futures price data
prices_df = reader.read_file('data/futures/ES1 Index_prices.parquet')

# Get metadata without loading full file
metadata = reader.get_metadata('data/futures/ES1 Index_meta.parquet')
print(f"Rows: {metadata['rows']}, Columns: {metadata['columns']}")</code></pre>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-layer-group"></i>
                                    Multiple File Loading
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="code-container">
                                    <div class="code-header">
                                        <div class="code-language">
                                            <i class="fab fa-python"></i>
                                            <span>Python</span>
                                        </div>
                                        <button class="copy-button">
                                            <i class="fas fa-copy"></i>
                                            Copy
                                        </button>
                                    </div>
                                    <pre class="code-block"><code>from src.data.data_readers import DataReaderFactory
import glob

# Get all futures price files
price_files = glob.glob('data/futures/*_prices.parquet')

# Read all files efficiently
reader = DataReaderFactory.get_reader('parquet')
all_data = reader.read_multiple_files(price_files)

# Access specific instrument
es_prices = all_data['data/futures/ES1 Index_prices.parquet']</code></pre>
                                </div>
                            </div>
                        </div>
                    </div>

                    <h3>Domain Object Examples</h3>
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-coins"></i>
                                    Create Futures Objects
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="code-container">
                                    <div class="code-header">
                                        <div class="code-language">
                                            <i class="fab fa-python"></i>
                                            <span>Python</span>
                                        </div>
                                        <button class="copy-button">
                                            <i class="fas fa-copy"></i>
                                            Copy
                                        </button>
                                    </div>
                                    <pre class="code-block"><code>from src.objects.instruments import FuturesInstrument
from src.objects.contracts import FuturesContract

# Create instrument
instrument = FuturesInstrument("ES1")

# Create contract for specific expiry
contract = FuturesContract(instrument, "20240315")

# Access contract properties
print(contract.date_str)        # "20240315"
print(contract.instrument_code) # "ES1"
print(contract.key)             # "ES1/20240315"</code></pre>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-chart-line"></i>
                                    Price Dictionary Usage
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="code-container">
                                    <div class="code-header">
                                        <div class="code-language">
                                            <i class="fab fa-python"></i>
                                            <span>Python</span>
                                        </div>
                                        <button class="copy-button">
                                            <i class="fas fa-copy"></i>
                                            Copy
                                        </button>
                                    </div>
                                    <pre class="code-block"><code>from src.objects.dict_future_contract_prices import DictFutureContractPrices

# Create price dictionary
price_dict = DictFutureContractPrices()

# Add contract prices
contract = FuturesContract("ES1", "20240315")
price_dict[contract] = prices_df

# Access with string (backwards compatible)
prices = price_dict.get_prices_for_contract_string("ES1/20240315")

# Get summary statistics
summary = price_dict.get_summary_dict()
print(summary)</code></pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Notebooks Section -->
            <section id="notebooks" class="content-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-book"></i>
                        Interactive Notebooks
                    </h2>
                    <p class="section-subtitle">
                        Comprehensive Jupyter notebooks for exploring and testing functionality
                    </p>
                </div>

                <div class="card-grid">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-search"></i>
                                📓 Data Exploration
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-chart-bar"></i>
                                Interactive
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Comprehensive exploration of all 146 futures instruments and their data structure, including:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-database"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Instrument Discovery</div>
                                        <div class="feature-description">Categorization by asset class</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-chart-area"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Data Structure Analysis</div>
                                        <div class="feature-description">Metadata and contract examination</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/01_data_exploration.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-external-link-alt"></i>
                                Open Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-chart-line"></i>
                                📈 Price Analysis
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-chart-line"></i>
                                Analytical
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Advanced price analysis with professional visualizations and statistical analysis:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-chart-bar"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Price Visualization</div>
                                        <div class="feature-description">Interactive charts and graphs</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-calculator"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Statistical Analysis</div>
                                        <div class="feature-description">Returns, volatility, correlations</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/02_price_analysis.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-external-link-alt"></i>
                                Open Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-vial"></i>
                                🔧 Module Testing
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-cogs"></i>
                                Testing
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Interactive testing environment for all system modules with live examples:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-play"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Module Validation</div>
                                        <div class="feature-description">Test each component interactively</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-bug"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Error Handling</div>
                                        <div class="feature-description">Exception testing and debugging</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/03_module_testing.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-external-link-alt"></i>
                                Open Notebook
                            </a>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-calendar-alt"></i>
                                📊 Roll Parameters
                            </h3>
                            <span class="status-badge status-implemented">
                                <i class="fas fa-exchange-alt"></i>
                                Financial
                            </span>
                        </div>
                        <div class="card-content">
                            <p>Advanced futures contract roll parameter analysis and management:</p>
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-sync-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Roll Cycle Analysis</div>
                                        <div class="feature-description">Contract expiry and rolling patterns</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-chart-pie"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Schedule Visualization</div>
                                        <div class="feature-description">Interactive roll schedule charts</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer">
                            <a href="/notebook/04_roll_parameters.ipynb" class="btn btn-primary" target="_blank">
                                <i class="fas fa-external-link-alt"></i>
                                Open Notebook
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Architecture Section -->
            <section id="architecture" class="content-section">
                <div class="section-header">
                    <h2 class="section-title">
                        <i class="fas fa-sitemap"></i>
                        System Architecture
                    </h2>
                    <p class="section-subtitle">
                        Complete class hierarchy and design patterns for all 22 system components
                    </p>
                </div>

                <!-- Class Statistics Overview -->
                <div class="card floating">
                    <div class="card-header">
                        <h3 class="card-title">
                            <i class="card-icon fas fa-cubes"></i>
                            Complete Class Hierarchy (22 Classes)
                        </h3>
                    </div>
                    <div class="card-content">
                        <div class="architecture-stats">
                            <div class="stat-group">
                                <div class="stat-item">
                                    <span class="stat-number">8</span>
                                    <span class="stat-label">Domain Objects</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number">7</span>
                                    <span class="stat-label">Data Infrastructure</span>
                                </div>
                            </div>
                            <div class="stat-group">
                                <div class="stat-item">
                                    <span class="stat-number">5</span>
                                    <span class="stat-label">Configuration Classes</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-number">2</span>
                                    <span class="stat-label">Enterprise Logging</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="diagram-container">
                    <h3>Architecture Diagrams</h3>
                    
                    <div class="diagram-tabs">
                        <button class="diagram-tab active" data-diagram="class_hierarchy">
                            <i class="fas fa-sitemap"></i>
                            Class Hierarchy
                        </button>
                        <button class="diagram-tab" data-diagram="data_flow">
                            <i class="fas fa-stream"></i>
                            Data Flow
                        </button>
                        <button class="diagram-tab" data-diagram="module_interactions">
                            <i class="fas fa-project-diagram"></i>
                            Module Interactions
                        </button>
                    </div>

                    <div id="class_hierarchy" class="diagram-content active">
                        <h4>Class Hierarchy & Design Patterns</h4>
                        <img src="{{ url_for('static', filename='images/class_hierarchy.svg') }}" 
                             alt="Class Hierarchy Diagram" 
                             class="diagram-img">
                        <p>Complete inheritance relationships showing all 22 classes with Factory, Template Method, and Strategy patterns.</p>
                    </div>

                    <div id="data_flow" class="diagram-content">
                        <h4>Data Flow Architecture</h4>
                        <img src="{{ url_for('static', filename='images/data_flow.svg') }}" 
                             alt="Data Flow Diagram" 
                             class="diagram-img">
                        <p>Complete data processing pipeline from 146 futures instruments to domain objects.</p>
                    </div>

                    <div id="module_interactions" class="diagram-content">
                        <h4>Module Interaction Diagram</h4>
                        <img src="{{ url_for('static', filename='images/module_interactions.svg') }}" 
                             alt="Module Interactions Diagram" 
                             class="diagram-img">
                        <p>Dependencies between all modules showing the complete modular architecture.</p>
                    </div>
                </div>

                <!-- Core Domain Objects Section -->
                <div class="architecture-section">
                    <h3>🏦 Core Domain Objects (Financial Trading)</h3>
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-coins"></i>
                                    Futures Instruments
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="class-list">
                                    <div class="class-item">
                                        <strong>FuturesInstrument</strong>
                                        <span class="file-ref">src/objects/instruments.py</span>
                                        <p>Core instrument representation (ES1, CL1, GC1)</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>FuturesInstrumentMetaData</strong> 
                                        <span class="class-tag dataclass">@dataclass</span>
                                        <span class="file-ref">src/objects/instruments.py</span>
                                        <p>Contract specifications (tick size, currency, etc.)</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>FuturesInstrumentWithMetaData</strong> 
                                        <span class="class-tag dataclass">@dataclass</span>
                                        <span class="file-ref">src/objects/instruments.py</span>
                                        <p>Composite: Instrument + Metadata</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-calendar-alt"></i>
                                    Contract Dates & Expiries
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="class-list">
                                    <div class="class-item">
                                        <strong>ExpiryDate</strong> 
                                        <span class="class-tag inherit">extends datetime</span>
                                        <span class="file-ref">src/objects/contract_dates.py</span>
                                        <p>Contract expiry with business day operations</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>SingleContractDate</strong>
                                        <span class="file-ref">src/objects/contract_dates.py</span>
                                        <p>YYYYMM/YYYYMMDD contract identifiers</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>ContractDate</strong>
                                        <span class="file-ref">src/objects/contract_dates.py</span>
                                        <p>Single and spread contract dates</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-file-contract"></i>
                                    Futures Contracts & Collections
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="class-list">
                                    <div class="class-item">
                                        <strong>FuturesContract</strong>
                                        <span class="file-ref">src/objects/contracts.py</span>
                                        <p>Complete contract: Instrument + Date + Expiry</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>ListOfFutureContracts</strong> 
                                        <span class="class-tag inherit">extends list</span>
                                        <span class="file-ref">src/objects/contracts.py</span>
                                        <p>Enhanced list with filtering and grouping</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>DictFutureContractPrices</strong> 
                                        <span class="class-tag inherit">extends dict</span>
                                        <span class="file-ref">src/objects/dict_future_contract_prices.py</span>
                                        <p>Contract → DataFrame price mapping</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Data Infrastructure Section -->
                <div class="architecture-section">
                    <h3>📊 Data Management Infrastructure</h3>
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-sitemap"></i>
                                    Data Reader Hierarchy
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="class-hierarchy-tree">
                                    <div class="class-item root">
                                        <strong>DataReader</strong> 
                                        <span class="class-tag abc">ABC</span>
                                        <span class="file-ref">src/data/data_readers.py</span>
                                        <p>Abstract interface for all data readers</p>
                                    </div>
                                    <div class="class-item child">
                                        <strong>BaseDataReader</strong>
                                        <span class="file-ref">src/data/data_readers.py</span>
                                        <p>Bloomberg ticker parsing, file inventory</p>
                                        <div class="grandchildren">
                                            <div class="class-item grandchild">
                                                <strong>ParquetDataReader</strong>
                                                <p>Optimized parquet with metadata</p>
                                            </div>
                                            <div class="class-item grandchild">
                                                <strong>CSVDataReader</strong>
                                                <p>Flexible CSV with encoding</p>
                                            </div>
                                            <div class="class-item grandchild">
                                                <strong>ODSDataReader</strong>
                                                <p>OpenDocument spreadsheet</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-industry"></i>
                                    Factory & Support Classes
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="class-list">
                                    <div class="class-item">
                                        <strong>DataReaderFactory</strong>
                                        <span class="file-ref">src/data/data_readers.py</span>
                                        <p>Creates readers based on file extensions</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>SupportedReaderFormats</strong> 
                                        <span class="class-tag enum">Enum</span>
                                        <span class="file-ref">src/data/data_readers.py</span>
                                        <p>File format definitions and extensions</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Enterprise Logging Section -->
                <div class="architecture-section">
                    <h3>📝 Enterprise Logging System</h3>
                    <div class="card-grid">
                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-file-alt"></i>
                                    Logger Hierarchy
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="class-hierarchy-tree">
                                    <div class="class-item root">
                                        <strong>Logger</strong> 
                                        <span class="class-tag abc">ABC</span>
                                        <span class="file-ref">src/core/logger.py</span>
                                        <p>Abstract logger interface</p>
                                    </div>
                                    <div class="class-item child">
                                        <strong>BaseLogger</strong>
                                        <span class="file-ref">src/core/logger.py</span>
                                        <p>YAML config support, environment awareness</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h4 class="card-title">
                                    <i class="card-icon fas fa-cogs"></i>
                                    Logging Infrastructure
                                </h4>
                            </div>
                            <div class="card-content">
                                <div class="class-list">
                                    <div class="class-item">
                                        <strong>LoggerFactory</strong>
                                        <span class="file-ref">src/core/logger.py</span>
                                        <p>Thread-safe logger creation with caching</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>LoggingConfig</strong>
                                        <span class="file-ref">src/core/logger.py</span>
                                        <p>YAML configuration loader</p>
                                    </div>
                                    <div class="class-item">
                                        <strong>Environment</strong> 
                                        <span class="class-tag enum">Enum</span>
                                        <span class="file-ref">src/core/logger.py</span>
                                        <p>DEV/TEST/PROD environment definitions</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Configuration Objects Section -->
                <div class="architecture-section">
                    <h3>⚙️ Configuration Objects</h3>
                    <div class="card">
                        <div class="card-header">
                            <h4 class="card-title">
                                <i class="card-icon fas fa-sliders-h"></i>
                                Configuration Dataclasses (5 Classes)
                            </h4>
                        </div>
                        <div class="card-content">
                            <div class="class-list">
                                <div class="class-item">
                                    <strong>EnvironmentConfig</strong> 
                                    <span class="class-tag dataclass">@dataclass</span>
                                    <span class="file-ref">src/config/config_objects.py</span>
                                    <p>Root configuration composition</p>
                                </div>
                                <div class="class-item">
                                    <strong>RollParameterConfig</strong> 
                                    <span class="class-tag dataclass">@dataclass</span>
                                    <span class="file-ref">src/config/config_objects.py</span>
                                    <p>Roll parameters with validation</p>
                                </div>
                                <div class="class-item">
                                    <strong>DataQualityConfig</strong> 
                                    <span class="class-tag dataclass">@dataclass</span>
                                    <span class="file-ref">src/config/config_objects.py</span>
                                    <p>Data quality thresholds</p>
                                </div>
                                <div class="class-item">
                                    <strong>FilePatternConfig</strong> 
                                    <span class="class-tag dataclass">@dataclass</span>
                                    <span class="file-ref">src/config/config_objects.py</span>
                                    <p>File discovery patterns</p>
                                </div>
                                <div class="class-item">
                                    <strong>LoggingConfig</strong> 
                                    <span class="class-tag dataclass">@dataclass</span>
                                    <span class="file-ref">src/config/config_objects.py</span>
                                    <p>Logging configuration structure</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Design Patterns Summary -->
                <div class="card-grid">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-puzzle-piece"></i>
                                Design Patterns Implementation
                            </h3>
                        </div>
                        <div class="card-content">
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-industry"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Abstract Factory</div>
                                        <div class="feature-description">DataReaderFactory, LoggerFactory</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-layer-group"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Template Method</div>
                                        <div class="feature-description">BaseDataReader, BaseLogger</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-chess"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Strategy</div>
                                        <div class="feature-description">Environment configs, format readers</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-building"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Composition</div>
                                        <div class="feature-description">FuturesInstrumentWithMetaData</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-paint-brush"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Decorator</div>
                                        <div class="feature-description">Enhanced list/dict classes</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-memory"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Singleton (Cached)</div>
                                        <div class="feature-description">Thread-safe logger instances</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-stream"></i>
                                Complete Data Processing Flow
                            </h3>
                        </div>
                        <div class="card-content">
                            <ol style="padding-left: 20px; color: var(--text-secondary);">
                                <li>Initialize LoggerFactory with environment</li>
                                <li>Load configuration objects (RollParameterConfig, etc.)</li>
                                <li>Create DataReaderFactory instance</li>
                                <li>Discover futures data files using BaseDataReader</li>
                                <li>Create FuturesInstrument and FuturesContract objects</li>
                                <li>Load price data into DictFutureContractPrices</li>
                                <li>Process with business logic and domain operations</li>
                                <li>Output results, metadata, and quality metrics</li>
                            </ol>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <i class="card-icon fas fa-shield-alt"></i>
                                System Quality Attributes
                            </h3>
                        </div>
                        <div class="card-content">
                            <div class="feature-list">
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-expand-arrows-alt"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Scalability</div>
                                        <div class="feature-description">Efficiently handles 146+ instruments</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-lock"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Type Safety</div>
                                        <div class="feature-description">Dataclass-based domain objects</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-users"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Thread Safety</div>
                                        <div class="feature-description">Concurrent access with caching</div>
                                    </div>
                                </div>
                                <div class="feature-item">
                                    <i class="feature-icon fas fa-tools"></i>
                                    <div class="feature-content">
                                        <div class="feature-title">Maintainability</div>
                                        <div class="feature-description">Modular, testable architecture</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <!-- Enhanced JavaScript -->
    <script src="{{ url_for('static', filename='js/enhanced-dashboard.js') }}?v=2"></script>
</body>
</html>
"""

@app.route('/')
def enhanced_dashboard():
    """Enhanced dashboard with Bloomberg-inspired design."""
    return render_template('dashboard.html', current_page='dashboard')

@app.route('/api/system-status')
def api_system_status():
    """API endpoint for system status."""
    try:
        # Import Ibiza modules to check status
        from src.data.data_readers import DataReaderFactory
        from src.core.logger import LoggerFactory
        
        status = {
            'overall_health': 'healthy',
            'components': {
                'data_readers': {'status': 'operational', 'health': 100},
                'logger_system': {'status': 'operational', 'health': 100},
                'configuration': {'status': 'partial', 'health': 60},
                'domain_objects': {'status': 'operational', 'health': 100},
                'utilities': {'status': 'operational', 'health': 100}
            },
            'data_summary': {
                'futures_instruments': 146,
                'data_formats_supported': ['parquet', 'csv', 'ods'],
                'completion_percentage': 45
            },
            'last_updated': '2024-01-15T10:30:00Z'
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'overall_health': 'error',
            'error': str(e)
        }), 500

@app.route('/status')
def system_status():
    """Enhanced system status page."""
    return render_template('system_status.html', current_page='status')

@app.route('/docs')
def documentation():
    """Comprehensive documentation page."""
    return render_template('documentation.html', current_page='docs')

@app.route('/status-legacy')
def system_status_legacy():
    """Legacy system status page."""
    try:
        # Import Ibiza modules to check status
        from src.data.data_readers import DataReaderFactory
        from src.core.logger import LoggerFactory
        
        status_html = """
        <html>
        <head>
            <title>Ibiza System Status</title>
            <link rel="stylesheet" href="/static/css/enhanced-dashboard.css">
            <style>
                body { padding: 2rem; background: var(--background); color: var(--text-primary); }
                .status-header { text-align: center; margin-bottom: 2rem; }
                .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
                .status-card { 
                    background: var(--surface); 
                    border: 1px solid var(--border-color); 
                    border-radius: var(--border-radius); 
                    padding: 1.5rem;
                    transition: var(--transition);
                    position: relative;
                    overflow: hidden;
                }
                .status-card:hover {
                    transform: translateY(-4px);
                    box-shadow: var(--shadow-lg);
                    border-color: var(--primary-color);
                }
                .status-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: var(--primary-color);
                    opacity: 0;
                    transition: var(--transition);
                }
                .status-card:hover::before { opacity: 1; }
                .status-card h3 { 
                    margin-bottom: 1rem; 
                    display: flex; 
                    align-items: center; 
                    justify-content: space-between;
                    font-size: 1.1rem;
                }
                .status-card .status-badge { 
                    /* Remove floating animation for status page */
                    animation: none !important;
                    margin-left: auto;
                }
                .status-card p { 
                    color: var(--text-secondary); 
                    margin: 0;
                    font-size: 0.9rem;
                }
                .back-button {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.75rem 1.25rem;
                    background: var(--primary-color);
                    color: var(--text-inverse);
                    text-decoration: none;
                    border-radius: var(--border-radius-sm);
                    font-weight: 500;
                    transition: var(--transition);
                    margin-bottom: 2rem;
                }
                .back-button:hover {
                    background: var(--primary-dark);
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body data-theme="midnight">
            <a href="/" class="back-button">
                <i class="fas fa-arrow-left"></i>
                Back to Dashboard
            </a>
            
            <div class="status-header">
                <h1>🏥 Ibiza System Status</h1>
                <p>Real-time monitoring of system components and data inventory</p>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>
                        📊 Data Readers
                        <span class="status-badge status-implemented">
                            <i class="fas fa-check-circle"></i>
                            Operational
                        </span>
                    </h3>
                    <p>Multi-format data reading capability active (Parquet, CSV, ODS)</p>
                </div>
                
                <div class="status-card">
                    <h3>
                        📝 Logger System
                        <span class="status-badge status-implemented">
                            <i class="fas fa-check-circle"></i>
                            Operational
                        </span>
                    </h3>
                    <p>Enterprise logging with environment configurations</p>
                </div>
                
                <div class="status-card">
                    <h3>
                        ⚙️ Configuration
                        <span class="status-badge status-partial">
                            <i class="fas fa-clock"></i>
                            Partial
                        </span>
                    </h3>
                    <p>Configuration objects implemented, manager pending</p>
                </div>
                
                <div class="status-card">
                    <h3>
                        🏦 Domain Objects
                        <span class="status-badge status-implemented">
                            <i class="fas fa-check-circle"></i>
                            Operational
                        </span>
                    </h3>
                    <p>Futures instruments and contracts fully functional</p>
                </div>
                
                <div class="status-card">
                    <h3>
                        📈 Data Inventory
                        <span class="status-badge status-info">
                            <i class="fas fa-database"></i>
                            146 Instruments
                        </span>
                    </h3>
                    <p>Complete futures market data loaded with Bloomberg ticker format</p>
                </div>
                
                <div class="status-card">
                    <h3>
                        🔧 Utilities
                        <span class="status-badge status-implemented">
                            <i class="fas fa-check-circle"></i>
                            Operational
                        </span>
                    </h3>
                    <p>Path handling, date utilities, and metadata extraction</p>
                </div>
            </div>
            
            <script src="/static/js/enhanced-dashboard.js?v=2"></script>
        </body>
        </html>
        """
        
        return status_html
    except Exception as e:
        return f"<h1>❌ System Status Error</h1><p>Error: {e}</p>"

@app.route('/jupyter')
def launch_jupyter():
    """Launch Jupyter Lab with enhanced message."""
    jupyter_html = """
    <html>
    <head>
        <title>Jupyter Lab Launcher</title>
        <link rel="stylesheet" href="/static/css/enhanced-dashboard.css">
        <style>
            body { padding: 2rem; text-align: center; }
            .launcher-content { max-width: 600px; margin: 0 auto; }
        </style>
    </head>
    <body data-theme="midnight">
        <div class="launcher-content">
            <h1>🚀 Launching Jupyter Lab</h1>
            <p>Starting interactive notebook environment for Ibiza data analysis...</p>
            
            <div class="card">
                <h3>Manual Launch Instructions:</h3>
                <div class="code-container">
                    <div class="code-block">
cd /home/jin23/Code/Ibiza/dashboard
jupyter lab --notebook-dir=notebooks --port=8889 --no-browser
                    </div>
                </div>
                <p>Then navigate to: <a href="http://localhost:8889/lab" target="_blank">http://localhost:8889/lab</a></p>
            </div>
            
            <div class="quick-actions">
                <a href="/" class="btn btn-primary">
                    <i class="fas fa-arrow-left"></i>
                    Back to Dashboard
                </a>
            </div>
        </div>
        <script src="/static/js/enhanced-dashboard.js"></script>
    </body>
    </html>
    """
    return jupyter_html

@app.route('/query')
def query_interface():
    """Data query interface with MCP DuckDB integration."""
    try:
        return render_template('query_interface_new.html', current_page='query')
    except:
        # Use the working direct HTML version as fallback
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Ibiza - Data Query Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #0f1629; color: #f1f5f9; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 20px; }
        .card h3 { margin: 0 0 15px 0; color: #0ea5e9; }
        input, select, button { padding: 8px 12px; border: 1px solid #475569; border-radius: 4px; background: #334155; color: #f1f5f9; margin: 4px 0; }
        button { background: #0ea5e9; cursor: pointer; font-weight: bold; }
        button:hover { background: #0284c7; }
        button:disabled { background: #475569; cursor: not-allowed; }
        .file-list { max-height: 200px; overflow-y: auto; border: 1px solid #475569; border-radius: 4px; background: #334155; }
        .file-item { padding: 10px; border-bottom: 1px solid #475569; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
        .file-item:hover { background: #475569; }
        .file-item.selected { background: #0ea5e9; color: white; }
        .results { background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 20px; margin-top: 20px; display: none; }
        .results table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .results th, .results td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #475569; }
        .results th { background: #334155; }
        .results tr:hover { background: #334155; }
        .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
        .status.success { background: #065f46; color: #10b981; }
        .status.error { background: #7f1d1d; color: #f87171; }
        .status.info { background: #1e40af; color: #60a5fa; }
        input[type="checkbox"] { margin-right: 8px; }
        label { display: flex; align-items: center; margin: 8px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Ibiza Data Query Interface</h1>
            <p>Query and analyze futures market data with MCP DuckDB integration</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📁 File Selection</h3>
                <input type="text" id="fileSearch" placeholder="Search files (e.g., ES1, CL1, GC1...)" style="width: 100%;">
                <div id="fileList" class="file-list" style="margin: 10px 0;">
                    <div style="padding: 20px; text-align: center; color: #94a3b8;">Loading files...</div>
                </div>
                <div id="selectedFiles"></div>
            </div>
            
            <div class="card">
                <h3>📅 Date Range</h3>
                <label>Start Date:</label>
                <input type="date" id="startDate" style="width: 100%;">
                <label>End Date:</label>
                <input type="date" id="endDate" style="width: 100%;">
            </div>
            
            <div class="card">
                <h3>📊 Columns</h3>
                <label><input type="checkbox" name="column" value="date" checked disabled> Date</label>
                <label><input type="checkbox" name="column" value="security" checked> Security</label>
                <label><input type="checkbox" name="column" value="PX_LAST" checked> Last Price</label>
                <label><input type="checkbox" name="column" value="PX_BID"> Bid Price</label>
                <label><input type="checkbox" name="column" value="PX_ASK"> Ask Price</label>
            </div>
            
            <div class="card">
                <h3>🚀 Execute</h3>
                <div id="queryStatus">Configure your query and click execute</div>
                <button id="executeBtn" onclick="executeQuery()" disabled style="width: 100%; margin: 15px 0;">Execute Query</button>
                <button onclick="clearQuery()" style="width: 100%;">Clear All</button>
            </div>
        </div>
        
        <div id="results" class="results">
            <h3>📋 Query Results</h3>
            <div id="resultsInfo"></div>
            <div id="resultsContent"></div>
            <button onclick="exportCSV()" style="margin-top: 15px;">💾 Export CSV</button>
        </div>
    </div>
    
    <script>
        let availableFiles = [];
        let selectedFiles = new Set();
        let currentResults = null;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setDefaultDates();
            loadFiles();
            setupEventListeners();
        });
        
        function setDefaultDates() {
            const today = new Date();
            const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
            document.getElementById('endDate').value = today.toISOString().split('T')[0];
            document.getElementById('startDate').value = thirtyDaysAgo.toISOString().split('T')[0];
        }
        
        function setupEventListeners() {
            document.getElementById('fileSearch').addEventListener('input', (e) => {
                filterFiles(e.target.value);
            });
            
            document.querySelectorAll('input[name="column"]').forEach(cb => {
                cb.addEventListener('change', updateQueryStatus);
            });
            
            document.getElementById('startDate').addEventListener('change', updateQueryStatus);
            document.getElementById('endDate').addEventListener('change', updateQueryStatus);
        }
        
        async function loadFiles() {
            try {
                const response = await fetch('/api/available-files');
                availableFiles = await response.json();
                renderFiles(availableFiles);
            } catch (error) {
                document.getElementById('fileList').innerHTML = '<div class="status error">Error loading files: ' + error.message + '</div>';
            }
        }
        
        function renderFiles(files) {
            const fileList = document.getElementById('fileList');
            if (files.length === 0) {
                fileList.innerHTML = '<div style="padding: 20px; text-align: center;">No files found</div>';
                return;
            }
            
            fileList.innerHTML = files.map(file => 
                `<div class="file-item" data-path="${file.path}" onclick="toggleFile('${file.path}')">
                    <div>
                        <div style="font-weight: bold;">${file.name}</div>
                        <div style="font-size: 0.85em; color: #94a3b8;">${file.size} • ${file.records} records</div>
                    </div>
                    <input type="checkbox" onclick="event.stopPropagation()">
                </div>`
            ).join('');
        }
        
        function filterFiles(query) {
            const filtered = availableFiles.filter(file => 
                file.name.toLowerCase().includes(query.toLowerCase())
            );
            renderFiles(filtered);
        }
        
        function toggleFile(filePath) {
            const fileItem = document.querySelector(`[data-path="${filePath}"]`);
            const checkbox = fileItem.querySelector('input[type="checkbox"]');
            
            if (selectedFiles.has(filePath)) {
                selectedFiles.delete(filePath);
                fileItem.classList.remove('selected');
                checkbox.checked = false;
            } else {
                selectedFiles.add(filePath);
                fileItem.classList.add('selected');
                checkbox.checked = true;
            }
            
            updateSelectedDisplay();
            updateQueryStatus();
        }
        
        function updateSelectedDisplay() {
            const container = document.getElementById('selectedFiles');
            if (selectedFiles.size === 0) {
                container.innerHTML = '';
                return;
            }
            
            const tags = Array.from(selectedFiles).map(path => {
                const fileName = path.split('/').pop().replace('_prices.parquet', '');
                return `<span style="background: #0ea5e9; color: white; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 0.85em; display: inline-block;">${fileName}</span>`;
            }).join('');
            
            container.innerHTML = '<div style="margin-top: 10px;"><strong>Selected:</strong><br>' + tags + '</div>';
        }
        
        function updateQueryStatus() {
            const hasFiles = selectedFiles.size > 0;
            const hasDateRange = document.getElementById('startDate').value && document.getElementById('endDate').value;
            const hasColumns = document.querySelectorAll('input[name="column"]:checked').length > 0;
            
            const canExecute = hasFiles && hasDateRange && hasColumns;
            const btn = document.getElementById('executeBtn');
            const status = document.getElementById('queryStatus');
            
            btn.disabled = !canExecute;
            
            if (canExecute) {
                status.innerHTML = `<div class="status success">Ready: ${selectedFiles.size} files, ${document.querySelectorAll('input[name="column"]:checked').length} columns</div>`;
            } else {
                let missing = [];
                if (!hasFiles) missing.push('select files');
                if (!hasDateRange) missing.push('set date range');
                if (!hasColumns) missing.push('choose columns');
                status.innerHTML = `<div class="status info">Please: ${missing.join(', ')}</div>`;
            }
        }
        
        async function executeQuery() {
            const columns = Array.from(document.querySelectorAll('input[name="column"]:checked')).map(cb => cb.value).join(', ');
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            const fileQueries = Array.from(selectedFiles).map(filePath => 
                `SELECT ${columns} FROM parquet_scan('${filePath}')`
            );
            
            let sql = fileQueries.join(' UNION ALL ');
            if (startDate && endDate) {
                sql = `SELECT * FROM (${sql}) WHERE date >= '${startDate}' AND date <= '${endDate}'`;
            }
            sql += ' ORDER BY date DESC, security LIMIT 100';
            
            const btn = document.getElementById('executeBtn');
            const originalText = btn.textContent;
            btn.textContent = 'Executing...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/execute-query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql: sql })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    displayResults(result);
                } else {
                    const error = await response.json();
                    throw new Error(error.error || 'Query failed');
                }
            } catch (error) {
                document.getElementById('results').innerHTML = `<div class="status error">Query failed: ${error.message}</div>`;
                document.getElementById('results').style.display = 'block';
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        }
        
        function displayResults(result) {
            currentResults = result;
            document.getElementById('results').style.display = 'block';
            document.getElementById('resultsInfo').innerHTML = `<div class="status success">${result.rowCount} rows returned</div>`;
            
            if (result.data.length === 0) {
                document.getElementById('resultsContent').innerHTML = '<div style="padding: 20px; text-align: center;">No data found</div>';
                return;
            }
            
            let html = '<table><thead><tr>';
            result.columns.forEach(col => html += `<th>${col}</th>`);
            html += '</tr></thead><tbody>';
            
            result.data.slice(0, 50).forEach(row => {
                html += '<tr>';
                result.columns.forEach(col => {
                    const value = row[col];
                    html += `<td>${typeof value === 'number' ? value.toLocaleString() : (value || '')}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table>';
            
            if (result.data.length > 50) {
                html += `<div style="padding: 10px; text-align: center; color: #94a3b8;">Showing first 50 rows of ${result.data.length}</div>`;
            }
            
            document.getElementById('resultsContent').innerHTML = html;
        }
        
        function exportCSV() {
            if (!currentResults) return;
            
            const csv = [
                currentResults.columns.join(','),
                ...currentResults.data.map(row => 
                    currentResults.columns.map(col => {
                        const value = row[col];
                        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
                    }).join(',')
                )
            ].join('\\n');
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ibiza_query_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function clearQuery() {
            selectedFiles.clear();
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
                item.querySelector('input[type="checkbox"]').checked = false;
            });
            document.getElementById('fileSearch').value = '';
            document.getElementById('selectedFiles').innerHTML = '';
            document.getElementById('results').style.display = 'none';
            setDefaultDates();
            renderFiles(availableFiles);
            updateQueryStatus();
        }
    </script>
</body>
</html>'''

@app.route('/query-test')
def query_test():
    """Simple test version of query interface."""
    return render_template('query_simple_test.html')

@app.route('/query-diagnostic')
def query_diagnostic():
    """Diagnostic page to debug query interface issues."""
    return render_template('query_diagnostic.html')

@app.route('/minimal-test')
def minimal_test():
    """Absolute minimal test page."""
    return render_template('minimal_test.html')

@app.route('/query-working')
def query_working():
    """Working query interface using direct HTML."""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Ibiza Query Interface - Working Version</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #0f1629; color: #f1f5f9; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 20px; }
        .card h3 { margin: 0 0 15px 0; color: #0ea5e9; }
        input, select, button { padding: 8px 12px; border: 1px solid #475569; border-radius: 4px; background: #334155; color: #f1f5f9; margin: 4px 0; }
        button { background: #0ea5e9; cursor: pointer; font-weight: bold; }
        button:hover { background: #0284c7; }
        button:disabled { background: #475569; cursor: not-allowed; }
        .file-list { max-height: 200px; overflow-y: auto; border: 1px solid #475569; border-radius: 4px; background: #334155; }
        .file-item { padding: 10px; border-bottom: 1px solid #475569; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
        .file-item:hover { background: #475569; }
        .file-item.selected { background: #0ea5e9; color: white; }
        .results { background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 20px; margin-top: 20px; display: none; }
        .results table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .results th, .results td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #475569; }
        .results th { background: #334155; }
        .results tr:hover { background: #334155; }
        .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
        .status.success { background: #065f46; color: #10b981; }
        .status.error { background: #7f1d1d; color: #f87171; }
        .status.info { background: #1e40af; color: #60a5fa; }
        input[type="checkbox"] { margin-right: 8px; }
        label { display: flex; align-items: center; margin: 8px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Ibiza Data Query Interface</h1>
            <p>Query and analyze futures market data</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📁 File Selection</h3>
                <input type="text" id="fileSearch" placeholder="Search files (e.g., ES1, CL1, GC1...)" style="width: 100%;">
                <div id="fileList" class="file-list" style="margin: 10px 0;">
                    <div style="padding: 20px; text-align: center; color: #94a3b8;">Loading files...</div>
                </div>
                <div id="selectedFiles"></div>
            </div>
            
            <div class="card">
                <h3>📅 Date Range</h3>
                <label>Start Date:</label>
                <input type="date" id="startDate" style="width: 100%;">
                <label>End Date:</label>
                <input type="date" id="endDate" style="width: 100%;">
            </div>
            
            <div class="card">
                <h3>📊 Columns</h3>
                <label><input type="checkbox" name="column" value="date" checked disabled> Date</label>
                <label><input type="checkbox" name="column" value="security" checked> Security</label>
                <label><input type="checkbox" name="column" value="PX_LAST" checked> Last Price</label>
                <label><input type="checkbox" name="column" value="PX_BID"> Bid Price</label>
                <label><input type="checkbox" name="column" value="PX_ASK"> Ask Price</label>
            </div>
            
            <div class="card">
                <h3>🚀 Execute</h3>
                <div id="queryStatus">Configure your query and click execute</div>
                <button id="executeBtn" onclick="executeQuery()" disabled style="width: 100%; margin: 15px 0;">Execute Query</button>
                <button onclick="clearQuery()" style="width: 100%;">Clear All</button>
            </div>
        </div>
        
        <div id="results" class="results">
            <h3>📋 Query Results</h3>
            <div id="resultsInfo"></div>
            <div id="resultsContent"></div>
            <button onclick="exportCSV()" style="margin-top: 15px;">💾 Export CSV</button>
        </div>
    </div>
    
    <script>
        let availableFiles = [];
        let selectedFiles = new Set();
        let currentResults = null;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setDefaultDates();
            loadFiles();
            setupEventListeners();
        });
        
        function setDefaultDates() {
            const today = new Date();
            const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
            document.getElementById('endDate').value = today.toISOString().split('T')[0];
            document.getElementById('startDate').value = thirtyDaysAgo.toISOString().split('T')[0];
        }
        
        function setupEventListeners() {
            document.getElementById('fileSearch').addEventListener('input', (e) => {
                filterFiles(e.target.value);
            });
            
            document.querySelectorAll('input[name="column"]').forEach(cb => {
                cb.addEventListener('change', updateQueryStatus);
            });
            
            document.getElementById('startDate').addEventListener('change', updateQueryStatus);
            document.getElementById('endDate').addEventListener('change', updateQueryStatus);
        }
        
        async function loadFiles() {
            try {
                const response = await fetch('/api/available-files');
                availableFiles = await response.json();
                renderFiles(availableFiles);
            } catch (error) {
                document.getElementById('fileList').innerHTML = '<div class="status error">Error loading files: ' + error.message + '</div>';
            }
        }
        
        function renderFiles(files) {
            const fileList = document.getElementById('fileList');
            if (files.length === 0) {
                fileList.innerHTML = '<div style="padding: 20px; text-align: center;">No files found</div>';
                return;
            }
            
            fileList.innerHTML = files.map(file => 
                `<div class="file-item" data-path="${file.path}" onclick="toggleFile('${file.path}')">
                    <div>
                        <div style="font-weight: bold;">${file.name}</div>
                        <div style="font-size: 0.85em; color: #94a3b8;">${file.size} • ${file.records} records</div>
                    </div>
                    <input type="checkbox" onclick="event.stopPropagation()">
                </div>`
            ).join('');
        }
        
        function filterFiles(query) {
            const filtered = availableFiles.filter(file => 
                file.name.toLowerCase().includes(query.toLowerCase())
            );
            renderFiles(filtered);
        }
        
        function toggleFile(filePath) {
            const fileItem = document.querySelector(`[data-path="${filePath}"]`);
            const checkbox = fileItem.querySelector('input[type="checkbox"]');
            
            if (selectedFiles.has(filePath)) {
                selectedFiles.delete(filePath);
                fileItem.classList.remove('selected');
                checkbox.checked = false;
            } else {
                selectedFiles.add(filePath);
                fileItem.classList.add('selected');
                checkbox.checked = true;
            }
            
            updateSelectedDisplay();
            updateQueryStatus();
        }
        
        function updateSelectedDisplay() {
            const container = document.getElementById('selectedFiles');
            if (selectedFiles.size === 0) {
                container.innerHTML = '';
                return;
            }
            
            const tags = Array.from(selectedFiles).map(path => {
                const fileName = path.split('/').pop().replace('_prices.parquet', '');
                return `<span style="background: #0ea5e9; color: white; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 0.85em; display: inline-block;">${fileName}</span>`;
            }).join('');
            
            container.innerHTML = '<div style="margin-top: 10px;"><strong>Selected:</strong><br>' + tags + '</div>';
        }
        
        function updateQueryStatus() {
            const hasFiles = selectedFiles.size > 0;
            const hasDateRange = document.getElementById('startDate').value && document.getElementById('endDate').value;
            const hasColumns = document.querySelectorAll('input[name="column"]:checked').length > 0;
            
            const canExecute = hasFiles && hasDateRange && hasColumns;
            const btn = document.getElementById('executeBtn');
            const status = document.getElementById('queryStatus');
            
            btn.disabled = !canExecute;
            
            if (canExecute) {
                status.innerHTML = `<div class="status success">Ready: ${selectedFiles.size} files, ${document.querySelectorAll('input[name="column"]:checked').length} columns</div>`;
            } else {
                let missing = [];
                if (!hasFiles) missing.push('select files');
                if (!hasDateRange) missing.push('set date range');
                if (!hasColumns) missing.push('choose columns');
                status.innerHTML = `<div class="status info">Please: ${missing.join(', ')}</div>`;
            }
        }
        
        async function executeQuery() {
            const columns = Array.from(document.querySelectorAll('input[name="column"]:checked')).map(cb => cb.value).join(', ');
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            const fileQueries = Array.from(selectedFiles).map(filePath => 
                `SELECT ${columns} FROM parquet_scan('${filePath}')`
            );
            
            let sql = fileQueries.join(' UNION ALL ');
            if (startDate && endDate) {
                sql = `SELECT * FROM (${sql}) WHERE date >= '${startDate}' AND date <= '${endDate}'`;
            }
            sql += ' ORDER BY date DESC, security LIMIT 100';
            
            const btn = document.getElementById('executeBtn');
            const originalText = btn.textContent;
            btn.textContent = 'Executing...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/execute-query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql: sql })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    displayResults(result);
                } else {
                    const error = await response.json();
                    throw new Error(error.error || 'Query failed');
                }
            } catch (error) {
                document.getElementById('results').innerHTML = `<div class="status error">Query failed: ${error.message}</div>`;
                document.getElementById('results').style.display = 'block';
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        }
        
        function displayResults(result) {
            currentResults = result;
            document.getElementById('results').style.display = 'block';
            document.getElementById('resultsInfo').innerHTML = `<div class="status success">${result.rowCount} rows returned</div>`;
            
            if (result.data.length === 0) {
                document.getElementById('resultsContent').innerHTML = '<div style="padding: 20px; text-align: center;">No data found</div>';
                return;
            }
            
            let html = '<table><thead><tr>';
            result.columns.forEach(col => html += `<th>${col}</th>`);
            html += '</tr></thead><tbody>';
            
            result.data.slice(0, 50).forEach(row => {
                html += '<tr>';
                result.columns.forEach(col => {
                    const value = row[col];
                    html += `<td>${typeof value === 'number' ? value.toLocaleString() : (value || '')}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table>';
            
            if (result.data.length > 50) {
                html += `<div style="padding: 10px; text-align: center; color: #94a3b8;">Showing first 50 rows of ${result.data.length}</div>`;
            }
            
            document.getElementById('resultsContent').innerHTML = html;
        }
        
        function exportCSV() {
            if (!currentResults) return;
            
            const csv = [
                currentResults.columns.join(','),
                ...currentResults.data.map(row => 
                    currentResults.columns.map(col => {
                        const value = row[col];
                        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
                    }).join(',')
                )
            ].join('\\n');
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ibiza_query_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function clearQuery() {
            selectedFiles.clear();
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
                item.querySelector('input[type="checkbox"]').checked = false;
            });
            document.getElementById('fileSearch').value = '';
            document.getElementById('selectedFiles').innerHTML = '';
            document.getElementById('results').style.display = 'none';
            setDefaultDates();
            renderFiles(availableFiles);
            updateQueryStatus();
        }
    </script>
</body>
</html>'''

@app.route('/direct-test')
def direct_test():
    """Direct HTML response without templates."""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Direct Test</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .box { border: 3px solid #007acc; padding: 20px; margin: 10px; background: white; }
        button { padding: 15px; background: #007acc; color: white; border: none; font-size: 16px; }
    </style>
</head>
<body>
    <h1 style="color: #007acc;">DIRECT HTML TEST</h1>
    
    <div class="box">
        <h2>Direct Response Test</h2>
        <p>This HTML is returned directly from Flask without templates.</p>
        <p style="color: green; font-weight: bold;">If you see this, basic HTML works!</p>
    </div>
    
    <div class="box">
        <h3>API Test</h3>
        <button onclick="testAPI()" id="apiBtn">Test API Connection</button>
        <div id="apiResult" style="margin-top: 10px; padding: 10px; background: #f9f9f9;"></div>
    </div>
    
    <div class="box">
        <h3>Interactive Test</h3>
        <input type="text" id="testInput" placeholder="Type something..." style="padding: 10px; width: 200px;">
        <button onclick="showInput()">Show Input</button>
        <div id="inputResult" style="margin-top: 10px;"></div>
    </div>
    
    <script>
        console.log('Direct test page loaded');
        
        function testAPI() {
            const btn = document.getElementById('apiBtn');
            const result = document.getElementById('apiResult');
            
            btn.textContent = 'Testing...';
            result.innerHTML = 'Connecting to API...';
            
            fetch('/api/available-files')
                .then(response => {
                    console.log('API response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('API data received:', data.length, 'items');
                    result.innerHTML = '<strong>SUCCESS!</strong> Found ' + data.length + ' files. First file: ' + (data[0] ? data[0].name : 'none');
                    result.style.background = '#d4edda';
                    btn.textContent = 'API Works!';
                })
                .catch(error => {
                    console.error('API error:', error);
                    result.innerHTML = '<strong>ERROR:</strong> ' + error.message;
                    result.style.background = '#f8d7da';
                    btn.textContent = 'API Failed';
                });
        }
        
        function showInput() {
            const input = document.getElementById('testInput').value;
            document.getElementById('inputResult').innerHTML = 'You typed: <strong>' + input + '</strong>';
        }
        
        // Auto-test API after 1 second
        setTimeout(testAPI, 1000);
    </script>
</body>
</html>'''

@app.route('/api/available-files')
def api_available_files():
    """API endpoint to get available data files with MCP integration"""
    try:
        from mcp_integration import mcp_integration
        
        # Use MCP integration to get files with metadata
        files = mcp_integration.get_available_files_with_duckdb()
        return jsonify(files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-query', methods=['POST'])
def api_execute_query():
    """API endpoint to execute data query using DuckDB"""
    try:
        import duckdb
        
        data = request.get_json()
        sql_query = data.get('sql', '')
        
        if not sql_query:
            return jsonify({'error': 'SQL query is required'}), 400
        
        # Initialize DuckDB connection
        conn = duckdb.connect(':memory:')
        
        try:
            # Execute query
            start_time = datetime.now()
            result = conn.execute(sql_query).fetchdf()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Return results
            return jsonify({
                'data': result.to_dict('records'),
                'columns': list(result.columns),
                'rowCount': len(result),
                'executionTime': round(execution_time, 3),
                'status': 'success'
            })
            
        except Exception as query_error:
            return jsonify({
                'error': f'Query execution failed: {str(query_error)}',
                'status': 'error'
            }), 400
            
        finally:
            conn.close()
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/notebook/<path:filename>')
def serve_notebook(filename):
    """Serve notebook files."""
    return send_from_directory('notebooks', filename)

# Add static file handling for enhanced assets
@app.route('/static/<path:filename>')
def enhanced_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

# New routes for futures charts functionality
@app.route('/charts')
def futures_charts():
    """Route for futures charts page."""
    return render_template('futures_charts.html', current_page='charts')

@app.route('/api/available-futures-markets')
def api_available_futures_markets():
    """API endpoint that returns a list of available futures markets from the parquet files."""
    try:
        # Try to use DataReaderFactory if available
        if DataReaderFactory is not None:
            # Get list of price files from the contract_prices directory
            price_files = list(FUTURES_PRICE_DIR.glob('*_prices.parquet'))
            
            markets = []
            for file_path in price_files:
                # Extract market name (remove _prices.parquet suffix)
                market_name = file_path.stem.replace('_prices', '')
                
                # Categorize by Comdty vs Index
                if 'Comdty' in market_name:
                    market_type = 'Commodity'
                elif 'Index' in market_name:
                    market_type = 'Index'
                else:
                    market_type = 'Unknown'
                
                # Get descriptive name for the market
                clean_symbol = market_name.replace(' Comdty', '').replace(' Index', '')
                description = get_market_description(clean_symbol)
                
                markets.append({
                    'symbol': market_name,
                    'name': description,
                    'type': market_type,
                    'display_name': clean_symbol,
                    'description': description,
                    'file_path': str(file_path)
                })
            
            # Sort by display name
            markets.sort(key=lambda x: x['display_name'])
            
            return jsonify({
                'status': 'success',
                'markets': markets,
                'total_count': len(markets)
            })
        
        else:
            # Fallback to mock data when DataReaderFactory is not available
            mock_markets = [
                {'symbol': 'ES1 Index', 'type': 'Index', 'display_name': 'ES1', 'file_path': 'mock'},
                {'symbol': 'CL1 Comdty', 'type': 'Commodity', 'display_name': 'CL1', 'file_path': 'mock'},
                {'symbol': 'GC1 Comdty', 'type': 'Commodity', 'display_name': 'GC1', 'file_path': 'mock'},
                {'symbol': 'NQ1 Index', 'type': 'Index', 'display_name': 'NQ1', 'file_path': 'mock'},
                {'symbol': 'RTY1 Index', 'type': 'Index', 'display_name': 'RTY1', 'file_path': 'mock'}
            ]
            
            return jsonify({
                'status': 'success',
                'markets': mock_markets,
                'total_count': len(mock_markets),
                'note': 'Using mock data - DataReaderFactory not available'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def build_contract_metadata_map(market):
    """
    Build a comprehensive mapping from contract codes to actual metadata.
    This replaces all hardcoded year parsing with LAST_TRADEABLE_DT from metadata.
    
    Returns: dict mapping contract codes to expiration dates and metadata
    """
    try:
        # Get the appropriate metadata file
        if 'Index' in market:
            contract_file = f"data/futures/unmerged_meta/{market}_contract_data.parquet"
        else:
            contract_file = f"data/futures/unmerged_meta/{market}_contract_data.parquet"
        
        if not os.path.exists(contract_file):
            return {}
        
        # Load contract metadata
        df = pd.read_parquet(contract_file)
        
        contract_map = {}
        for _, row in df.iterrows():
            security = row['security']
            contract_code = security.replace(' Index', '').replace(' Comdty', '')
            
            # Use actual expiration date from metadata
            expiry_date = row['LAST_TRADEABLE_DT']
            if pd.isna(expiry_date):
                continue
                
            contract_map[contract_code] = {
                'expiry_date': expiry_date,
                'fut_month_yr': row.get('FUT_MONTH_YR', ''),
                'long_name': row.get('FUT_LONG_NAME', ''),
                'exchange': row.get('FUT_EXCH_NAME_SHRT', ''),
                'security': security,
                'roll_date': row.get('FUT_ROLL_DT'),
                'delivery_date': row.get('FUT_DLV_DT_LAST')
            }
            
        return contract_map
        
    except Exception as e:
        print(f"Error building contract metadata map for {market}: {e}")
        return {}

def generate_contracts_from_metadata(market):
    """Generate contracts from metadata using DuckDB for accurate information"""
    try:
        import duckdb
        from datetime import datetime
        
        # Look for metadata file first
        metadata_file = Path(f'../data/futures/metadata/{market}_merged_metadata.parquet')
        if not metadata_file.exists():
            return generate_contracts_from_data(market)  # Fallback to price data method
            
        # Query metadata with DuckDB for accurate contract information
        conn = duckdb.connect()
        
        query = f"""
        SELECT 
            security,
            FUT_MONTH_YR,
            FUT_GEN_MONTH,
            LAST_TRADEABLE_DT,
            FUT_LONG_NAME,
            FUT_CONT_SIZE,
            FUT_TICK_SIZE,
            exchange_code
        FROM '{metadata_file}'
        WHERE security IS NOT NULL
        ORDER BY LAST_TRADEABLE_DT DESC
        """
        
        result = conn.execute(query).fetchdf()
        conn.close()
        
        if result.empty:
            return generate_contracts_from_data(market)  # Fallback
            
        contracts = []
        
        for _, row in result.iterrows():
            security = row['security']
            contract_code = security.replace(' Index', '').replace(' Comdty', '')
            
            # Parse month and year from FUT_MONTH_YR (e.g., "MAR 30", "SEP 97")
            try:
                month_year_str = row['FUT_MONTH_YR']
                month_name, year_str = month_year_str.split()
                
                # FIXED: Use actual expiry date from metadata - no hardcoded year parsing!
                expiry_date = row['LAST_TRADEABLE_DT']
                if pd.isna(expiry_date):
                    print(f"Missing LAST_TRADEABLE_DT for {contract_code}, skipping")
                    continue
                
                # Get year from actual expiry date
                expiry_dt = pd.to_datetime(expiry_date)
                year = expiry_dt.year
                expiry_str = expiry_dt.strftime('%Y-%m-%d')
                    
                # Extract month code from contract code for display
                if len(contract_code) >= 3:
                    if len(contract_code) >= 4 and contract_code[-2:].isdigit():
                        month_code = contract_code[-3]
                    else:
                        month_code = contract_code[-2]
                else:
                    month_code = 'Unknown'
                
                contracts.append({
                    'symbol': contract_code,
                    'contract_id': contract_code,
                    'expiry_date': expiry_str,
                    'expiry': expiry_str,  # Add both fields for UI compatibility
                    'last_trading_date': expiry_str,
                    'delivery_month': f"{month_name} {year}",
                    'month_code': month_code,
                    'year': year,
                    'displayName': f"{contract_code} ({month_name} {year})",
                    'contractName': contract_code,
                    'underlying': market,
                    'isActive': True,
                    'long_name': row.get('FUT_LONG_NAME', ''),
                    'contract_size': row.get('FUT_CONT_SIZE', 0),
                    'tick_size': row.get('FUT_TICK_SIZE', 0),
                    'exchange': row.get('exchange_code', ''),
                    'trading_months': row.get('FUT_GEN_MONTH', '')
                })
                
            except Exception as e:
                print(f"Error parsing contract {security}: {e}")
                continue
                
        # Sort by expiry date (most recent first)
        contracts.sort(key=lambda x: x['expiry_date'], reverse=True)
        return contracts
        
    except Exception as e:
        print(f"Error generating contracts from metadata for {market}: {e}")
        return generate_contracts_from_data(market)  # Fallback

def month_name_to_number(month_name):
    """Convert month name to number"""
    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    return month_map.get(month_name.upper(), 1)

def generate_contracts_from_data(market):
    """Generate contracts from actual price data with metadata lookup for expiry dates"""
    try:
        # FIXED: Try to get metadata mapping first to avoid hardcoded year parsing
        contract_map = build_contract_metadata_map(market)
        
        # Look for price data file
        price_file = FUTURES_PRICE_DIR / f'{market}_prices.parquet'
        
        if not price_file.exists():
            return generate_mock_contracts(market)  # Fall back to mock
        
        # Read price data
        import pandas as pd
        price_data = pd.read_parquet(price_file)
        
        if 'security' not in price_data.columns or 'date' not in price_data.columns:
            return generate_mock_contracts(market)
        
        # Get unique contracts and their date ranges
        contract_data = price_data.groupby('security').agg({
            'date': ['min', 'max'],
            'PX_LAST': 'count'
        }).reset_index()
        
        contract_data.columns = ['security', 'first_date', 'last_date', 'data_points']
        
        # Parse contract information
        contracts = []
        month_names = {
            'H': 'March', 'M': 'June', 'U': 'September', 'Z': 'December',
            'F': 'January', 'G': 'February', 'J': 'April', 'K': 'May',
            'N': 'July', 'Q': 'August', 'V': 'October', 'X': 'November'
        }
        
        for _, row in contract_data.iterrows():
            security = row['security']
            
            # Extract contract details from security name (e.g., "ESH5 Index" -> "ESH5")
            contract_code = security.replace(' Index', '').replace(' Comdty', '')
            
            # FIXED: Try to get expiry date from metadata first
            if contract_code in contract_map:
                # Use actual expiry date from metadata - no hardcoded parsing!
                metadata = contract_map[contract_code]
                expiry_date = metadata['expiry_date']
                expiry_str = pd.to_datetime(expiry_date).strftime('%Y-%m-%d')
                year = pd.to_datetime(expiry_date).year
                
                # Extract month code for display
                month_code = 'Unknown'
                if len(contract_code) >= 3:
                    if len(contract_code) >= 4 and contract_code[-2:].isdigit():
                        month_code = contract_code[-3]
                    else:
                        month_code = contract_code[-2]
                
                month_name = month_names.get(month_code, 'Unknown')
                
            else:
                # Fallback: use last trading date from price data (less accurate)
                print(f"Warning: No metadata found for {contract_code}, using price data dates")
                expiry_str = row['last_date'].strftime('%Y-%m-%d')
                
                # Extract month code for display (no hardcoded year parsing)
                month_code = 'Unknown'
                if len(contract_code) >= 3:
                    if len(contract_code) >= 4 and contract_code[-2:].isdigit():
                        month_code = contract_code[-3]
                    elif contract_code[-1].isdigit():
                        month_code = contract_code[-2]
                    else:
                        month_code = contract_code[-2] if len(contract_code) >= 2 else 'U'
                
                # Use actual year from price data (last_date)
                year = row['last_date'].year
                
                month_name = month_names.get(month_code, 'Unknown')
                
            contracts.append({
                'symbol': contract_code,
                'contract_id': contract_code,
                'expiry_date': expiry_str,
                'expiry': expiry_str,  # Add both fields for UI compatibility
                'last_trading_date': expiry_str,
                'delivery_month': f"{month_name} {year}",
                'month_code': month_code,
                'year': year,
                'displayName': f"{contract_code} ({month_name} {year})",
                'contractName': contract_code,
                'underlying': market,
                'isActive': pd.to_datetime(expiry_str) > pd.Timestamp.now(),
                'data_points': int(row['data_points']),
                'first_date': row['first_date'].strftime('%Y-%m-%d'),
                    'last_date': row['last_date'].strftime('%Y-%m-%d')
                })
        
        # Sort by expiry date (most recent first, but return all contracts)
        contracts.sort(key=lambda x: x['expiry_date'], reverse=True)
        return contracts  # Return all available contracts
        
    except Exception as e:
        print(f"Error generating contracts from data for {market}: {e}")
        return generate_mock_contracts(market)  # Fall back to mock

def generate_mock_contracts(market):
    """Generate realistic mock contracts based on actual futures market patterns"""
    from datetime import datetime, timedelta
    import calendar
    
    # Clean market symbol for contract generation
    base_symbol = market.replace(' Index', '').replace(' Comdty', '').replace('1', '')
    
    # Realistic contract month codes based on actual market trading
    market_specific_months = {
        'ES': {'H': ('March', 3), 'M': ('June', 6), 'U': ('September', 9), 'Z': ('December', 12)},
        'CL': {'F': ('January', 1), 'G': ('February', 2), 'H': ('March', 3), 'J': ('April', 4), 
               'K': ('May', 5), 'M': ('June', 6), 'N': ('July', 7), 'Q': ('August', 8),
               'U': ('September', 9), 'V': ('October', 10), 'X': ('November', 11), 'Z': ('December', 12)},
        'GC': {'G': ('February', 2), 'J': ('April', 4), 'M': ('June', 6), 'Q': ('August', 8), 
               'V': ('October', 10), 'Z': ('December', 12)},
        'NG': {'F': ('January', 1), 'G': ('February', 2), 'H': ('March', 3), 'J': ('April', 4), 
               'K': ('May', 5), 'M': ('June', 6), 'N': ('July', 7), 'Q': ('August', 8),
               'U': ('September', 9), 'V': ('October', 10), 'X': ('November', 11), 'Z': ('December', 12)}
    }
    
    # Default quarterly contracts for unknown markets
    default_months = {'H': ('March', 3), 'M': ('June', 6), 'U': ('September', 9), 'Z': ('December', 12)}
    
    # Select appropriate month codes
    month_codes = market_specific_months.get(base_symbol, default_months)
    
    contracts = []
    current_year = datetime.now().year
    
    # Generate contracts for current and next 2 years
    for year in range(current_year, current_year + 3):
        for code, (month_name, month_num) in month_codes.items():
            # Contract expiry is typically third Friday of the month
            expiry_date = get_third_friday(year, month_num)
            last_trading_date = expiry_date - timedelta(days=1)
            
            year_suffix = str(year)[-1]  # Last digit of year
            contract_symbol = f"{base_symbol}{code}{year_suffix}"
            
            # Only include future contracts (not expired)
            if expiry_date > datetime.now().date():
                contracts.append({
                    'symbol': contract_symbol,
                    'contract_id': contract_symbol,
                    'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                    'expiry': expiry_date.strftime('%Y-%m-%d'),  # Add both fields for compatibility
                    'last_trading_date': last_trading_date.strftime('%Y-%m-%d'),
                    'delivery_month': f"{month_name} {year}",
                    'month_code': code,
                    'year': year,
                    'displayName': f"{contract_symbol} ({month_name} {year})",
                    'contractName': contract_symbol,
                    'underlying': market,
                    'isActive': True,
                    'long_name': f"Mock {market} Future",
                    'exchange': 'Mock Exchange'
                })
    
    return sorted(contracts, key=lambda x: x['expiry_date'])[:12]  # Return next 12 contracts

def get_third_friday(year, month):
    """Get the third Friday of a given month/year"""
    from datetime import date, timedelta
    
    # First day of the month
    first_day = date(year, month, 1)
    
    # Find first Friday
    days_until_friday = (4 - first_day.weekday()) % 7
    first_friday = first_day + timedelta(days=days_until_friday)
    
    # Third Friday is 14 days later
    third_friday = first_friday + timedelta(days=14)
    
    return third_friday

@app.route('/api/futures-metadata/<market>')
def api_futures_metadata(market):
    """API endpoint that returns metadata for a specific futures market."""
    try:
        import duckdb
        
        # Look for metadata file
        metadata_file = Path(f'../data/futures/metadata/{market}_merged_metadata.parquet')
        if not metadata_file.exists():
            return jsonify({
                'status': 'error',
                'error': f'Metadata not found for {market}'
            }), 404
            
        # Query metadata with DuckDB
        conn = duckdb.connect()
        
        query = f"""
        WITH base_info AS (
            SELECT DISTINCT
                FUT_CONT_SIZE,
                FUT_VAL_PT,
                FUT_TICK_SIZE,
                FUT_TICK_VAL,
                PRICE_MULTIPLIER,
                exchange_code,
                FUTURES_CATEGORY,
                FUT_TRADING_HRS,
                FUT_GEN_MONTH,
                NOTIONAL_CURRENCY_1
            FROM '{metadata_file}'
            WHERE security IS NOT NULL
            LIMIT 1
        ),
        contract_stats AS (
            SELECT 
                COUNT(DISTINCT security) as total_contracts,
                MIN(LAST_TRADEABLE_DT) as earliest_expiry,
                MAX(LAST_TRADEABLE_DT) as latest_expiry,
                MAX(FUT_LONG_NAME) as sample_long_name
            FROM '{metadata_file}'
            WHERE security IS NOT NULL
        )
        SELECT 
            contract_stats.sample_long_name as FUT_LONG_NAME,
            base_info.*,
            contract_stats.total_contracts,
            contract_stats.earliest_expiry,
            contract_stats.latest_expiry
        FROM base_info, contract_stats
        """
        
        result = conn.execute(query).fetchdf()
        conn.close()
        
        if result.empty:
            return jsonify({
                'status': 'error',
                'error': f'No metadata found for {market}'
            }), 404
            
        row = result.iloc[0]
        
        # Format trading months
        trading_months_raw = row.get('FUT_GEN_MONTH', '')
        trading_months_formatted = format_trading_months(trading_months_raw)
        
        # Format currency
        currency = row.get('NOTIONAL_CURRENCY_1')
        if currency is None or pd.isna(currency):
            currency = 'USD'
            
        # Format data range
        earliest = pd.to_datetime(row['earliest_expiry']).strftime('%Y-%m-%d') if pd.notna(row['earliest_expiry']) else 'N/A'
        latest = pd.to_datetime(row['latest_expiry']).strftime('%Y-%m-%d') if pd.notna(row['latest_expiry']) else 'N/A'
        
        # Helper function to handle pandas NA values and string conversions
        def safe_format(value, format_str, default='N/A'):
            if value is None or (hasattr(pd, 'isna') and pd.isna(value)):
                return default
            try:
                # Convert string to float if needed
                if isinstance(value, str) and format_str in ["${:.2f}", "{:,.0f}"]:
                    value = float(value)
                return format_str.format(value)
            except:
                return default
                
        metadata = {
            'market': market,
            'long_name': str(row.get('FUT_LONG_NAME', '')).replace('FUT', 'Futures').strip() if row.get('FUT_LONG_NAME') is not None else 'N/A',
            'contract_size': safe_format(row.get('FUT_CONT_SIZE'), "{:,.0f}"),
            'tick_size': safe_format(row.get('FUT_TICK_SIZE'), "${:.2f}"),
            'tick_value': safe_format(row.get('FUT_TICK_VAL'), "${:.2f}"),
            'point_value': safe_format(row.get('FUT_VAL_PT'), "${:.2f}"),
            'price_multiplier': safe_format(row.get('PRICE_MULTIPLIER'), "{:,.0f}", '1'),
            'exchange': str(row.get('exchange_code', 'N/A')) if row.get('exchange_code') is not None else 'N/A',
            'category': str(row.get('FUTURES_CATEGORY', 'N/A')) if row.get('FUTURES_CATEGORY') is not None else 'N/A',
            'trading_hours': str(row.get('FUT_TRADING_HRS', 'N/A')) if row.get('FUT_TRADING_HRS') is not None else 'N/A',
            'trading_months': trading_months_formatted,
            'trading_months_raw': trading_months_raw,
            'currency': currency,
            'total_contracts': int(row['total_contracts']) if row['total_contracts'] is not None else 0,
            'data_range': f"{earliest} to {latest}",
            'earliest_expiry': earliest,
            'latest_expiry': latest
        }
        
        return jsonify({
            'status': 'success',
            'metadata': metadata
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def format_trading_months(months_str):
    """Convert trading month codes to readable format"""
    if not months_str or pd.isna(months_str):
        return 'N/A'
        
    month_names = {
        'F': 'Jan', 'G': 'Feb', 'H': 'Mar', 'J': 'Apr', 
        'K': 'May', 'M': 'Jun', 'N': 'Jul', 'Q': 'Aug',
        'U': 'Sep', 'V': 'Oct', 'X': 'Nov', 'Z': 'Dec'
    }
    
    formatted_months = []
    for char in months_str:
        if char in month_names:
            formatted_months.append(month_names[char])
    
    if len(formatted_months) == 4 and formatted_months == ['Mar', 'Jun', 'Sep', 'Dec']:
        return 'Quarterly (Mar, Jun, Sep, Dec)'
    elif len(formatted_months) == 12:
        return 'Monthly (All months)'
    elif len(formatted_months) == 2:
        return f'Semi-annual ({", ".join(formatted_months)})'
    else:
        return ', '.join(formatted_months)

@app.route('/api/futures-contracts/<market>')
def api_futures_contracts(market):
    """API endpoint that returns available contracts for a specific market."""
    try:
        # Use metadata-based contract generation first (most accurate)
        contracts = generate_contracts_from_metadata(market)
        
        if contracts and len(contracts) > 0:
            return jsonify({
                'status': 'success',
                'contracts': contracts,
                'total_count': len(contracts),
                'data_source': 'metadata'
            })
        
        # Fallback to legacy contract file method
        contract_file = FUTURES_META_DIR / f'{market}_contract_data.parquet'
        
        if contract_file.exists():
            # Try to read contract file, but fall back to mock if data is incomplete
            try:
                import pandas as pd
                contract_data = pd.read_parquet(contract_file)
                
                # Check if we have real contract data
                if len(contract_data) > 0 and 'contract_id' in contract_data.columns:
                    first_row = contract_data.iloc[0]
                    if (pd.notna(first_row.get('contract_id')) and 
                        str(first_row.get('contract_id')).strip() not in ['', 'Unknown']):
                        # We have real data, use it
                        contracts = []
                        for _, row in contract_data.iterrows():
                            contract_info = {
                                'contract_id': str(row.get('contract_id', 'Unknown')),
                                'expiry_date': str(row.get('expiry_date', 'Unknown')),
                                'last_trading_date': str(row.get('last_trading_date', 'Unknown')),
                                'delivery_month': str(row.get('delivery_month', 'Unknown'))
                            }
                            contracts.append(contract_info)
                        
                        return jsonify({
                            'status': 'success',
                            'market': market,
                            'contracts': contracts,
                            'total_count': len(contracts)
                        })
            except Exception as e:
                print(f"Error reading contract file: {e}")
                pass  # Fall through to mock data generation
        
        # Generate contracts from actual price data
        contracts = generate_contracts_from_data(market)
        
        return jsonify({
            'status': 'success',
            'market': market,
            'contracts': contracts,
            'total_count': len(contracts),
            'note': 'Generated from actual price data' if contracts else 'Using mock data'
        })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/futures-chart-data', methods=['POST'])
def api_futures_chart_data():
    """API endpoint that returns price data for selected contracts (POST request)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        contracts = data.get('contracts', [])
        date_range = data.get('date_range', {})
        
        if not contracts:
            return jsonify({'error': 'No contracts specified'}), 400
        
        # Try to use DataReaderFactory if available
        if DataReaderFactory is not None:
            chart_data = []
            
            for contract in contracts:
                market = contract.get('market', '')
                if not market:
                    continue
                    
                # Look for price data file
                price_file = FUTURES_PRICE_DIR / f'{market}_prices.parquet'
                
                if price_file.exists():
                    # Read directly with pandas to avoid logger issues
                    import pandas as pd
                    price_data = pd.read_parquet(price_file)
                    
                    # Filter by date range if provided
                    if date_range.get('start_date') and 'date' in price_data.columns:
                        price_data = price_data[price_data['date'] >= date_range['start_date']]
                    if date_range.get('end_date') and 'date' in price_data.columns:
                        price_data = price_data[price_data['date'] <= date_range['end_date']]
                    
                    # For futures, we need to filter by the specific contract code
                    contract_id = contract.get('contract_id', '')
                    if contract_id and 'security' in price_data.columns:
                        # Filter for the specific contract (e.g., ESU5 -> ESU5 Index)
                        # The data uses single digit years: ESH5 = March 2025
                        if len(contract_id) >= 3:
                            # Just append " Index" to the contract code
                            contract_pattern = f"{contract_id} Index"
                            
                            # Filter data for this specific contract
                            contract_data = price_data[price_data['security'] == contract_pattern]
                            if len(contract_data) == 0:
                                # Try alternative patterns
                                contract_data = price_data[price_data['security'].str.contains(contract_id, na=False)]
                        else:
                            contract_data = price_data
                    else:
                        contract_data = price_data
                    
                    # Convert to chart format using actual column names
                    chart_points = []
                    for _, row in contract_data.head(1000).iterrows():  # Limit to 1000 points for performance
                        point = {
                            'date': str(row.get('date', '')),
                            'contract': str(row.get('security', market)),
                            'px_last': float(row.get('PX_LAST', 0)) if pd.notna(row.get('PX_LAST', 0)) else None,
                            'px_bid': float(row.get('PX_BID', 0)) if pd.notna(row.get('PX_BID', 0)) else None,
                            'px_ask': float(row.get('PX_ASK', 0)) if pd.notna(row.get('PX_ASK', 0)) else None,
                            'volume': int(row.get('volume', 0)) if pd.notna(row.get('volume', 0)) else None
                        }
                        chart_points.append(point)
                    
                    chart_data.append({
                        'market': market,
                        'data': chart_points,
                        'total_points': len(chart_points)
                    })
            
            return jsonify({
                'status': 'success',
                'chart_data': chart_data,
                'requested_contracts': len(contracts),
                'returned_markets': len(chart_data)
            })
        
        else:
            # Fallback to mock data when DataReaderFactory is not available
            mock_chart_data = []
            
            for contract in contracts:
                market = contract.get('market', 'Unknown')
                
                # Generate mock price data
                mock_points = []
                base_date = datetime(2024, 1, 1)
                base_price = 100.0
                
                for i in range(100):  # 100 mock data points
                    current_date = base_date + timedelta(days=i)
                    price_change = np.random.normal(0, 1) * 0.5
                    base_price += price_change
                    
                    point = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'open': round(base_price, 2),
                        'high': round(base_price + abs(np.random.normal(0, 0.5)), 2),
                        'low': round(base_price - abs(np.random.normal(0, 0.5)), 2),
                        'close': round(base_price + np.random.normal(0, 0.3), 2),
                        'volume': int(np.random.normal(10000, 2000))
                    }
                    mock_points.append(point)
                
                mock_chart_data.append({
                    'market': market,
                    'data': mock_points,
                    'total_points': len(mock_points)
                })
            
            return jsonify({
                'status': 'success',
                'chart_data': mock_chart_data,
                'requested_contracts': len(contracts),
                'returned_markets': len(mock_chart_data),
                'note': 'Using mock data - DataReaderFactory not available'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Ibiza Interactive Dashboard...")
    print("✨ Features:")
    print("   • Bloomberg-inspired theme system with 4 professional themes")
    print("   • Advanced responsive design with mobile support")
    print("   • Enhanced syntax highlighting and code copying")
    print("   • Interactive diagram visualization")
    print("   • Real-time system status monitoring")
    print("   • Comprehensive module documentation")
    print("")
    print("🌐 Dashboard available at: http://localhost:5003")
    print("📊 System status at: http://localhost:5003/status")
    print("🛑 Use Ctrl+C to stop the server")
    print("")
    
    app.run(host='0.0.0.0', port=5003, debug=True)