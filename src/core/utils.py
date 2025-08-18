"""
Path Utilities Module

Cross-platform path handling utilities and file analysis helpers.
"""

import os
import pathlib
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

import pandas as pd

# Format-specific imports with graceful degradation
try:
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False


# =============================================================================
# PATH UTILITIES
# =============================================================================

def resolve_data_path(path: Union[str, Path], base_dir: Optional[Union[str, Path]] = None) -> Path:
    """Resolve path to absolute path with cross-platform compatibility."""
    path_obj = Path(path)

    if str(path_obj).startswith('~'):
        path_obj = path_obj.expanduser()

    if path_obj.is_absolute():
        return path_obj.resolve()

    if base_dir is not None:
        base_path = Path(base_dir).expanduser().resolve()
        return (base_path / path_obj).resolve()
    else:
        return path_obj.resolve()


def validate_path_exists(path: Union[str, Path], must_be_file: bool = True) -> bool:
    """Validate that path exists and optionally that it's a file."""
    path_obj = Path(path)

    if not path_obj.exists():
        return False

    if must_be_file and not path_obj.is_file():
        return False

    return True


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure directory exists, creating it if necessary."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_files_in_directory(directory: Union[str, Path],
                          pattern: str = "*",
                          recursive: bool = False) -> List[Path]:
    """Get list of files in directory matching pattern."""
    dir_path = Path(directory)

    if not dir_path.exists() or not dir_path.is_dir():
        return []

    if recursive:
        return list(dir_path.rglob(pattern))
    else:
        return list(dir_path.glob(pattern))


def get_filenames_only(file_paths: List[Path]) -> List[str]:
    """Extract just filenames from list of Path objects."""
    return [path.name for path in file_paths]


def filter_by_extensions(files: List[Path], extensions: List[str]) -> List[Path]:
    """Filter files by supported extensions."""
    return [f for f in files if f.suffix.lower() in extensions]


# =============================================================================
# FILE ANALYSIS UTILITIES
# =============================================================================

def get_file_size_bytes(file_path: Union[str, Path]) -> int:
    """Get file size in bytes."""
    path_obj = Path(file_path)
    return path_obj.stat().st_size if path_obj.exists() else 0


def extract_dataframe_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract metadata from DataFrame."""
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': df.columns.tolist(),
        'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()}
    }


def create_file_info_dict(rows: Optional[int] = None,
                         columns: Optional[int] = None,
                         column_names: Optional[List[str]] = None,
                         file_size: Optional[int] = None,
                         data_types: Optional[Dict[str, str]] = None,
                         format_specific: Optional[Dict[str, Any]] = None,
                         error: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized file info dictionary."""
    return {
        'rows': rows,
        'columns': columns,
        'column_names': column_names or [],
        'file_size': file_size or 0,
        'data_types': data_types or {},
        'format_specific': format_specific or {},
        'error': error
    }


# =============================================================================
# PARQUET-SPECIFIC UTILITIES
# =============================================================================

def get_parquet_metadata_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Extract metadata from parquet file without loading data."""
    if not PARQUET_AVAILABLE:
        raise ImportError("pyarrow is required for parquet metadata extraction")

    path_obj = Path(file_path)

    try:
        parquet_file = pq.ParquetFile(path_obj)
        metadata = parquet_file.metadata
        schema = parquet_file.schema_arrow

        # Extract column information
        column_names = [field.name for field in schema]
        data_types = {field.name: str(field.type) for field in schema}

        return {
            'rows': metadata.num_rows,
            'columns': len(column_names),
            'column_names': column_names,
            'data_types': data_types,
            'format_specific': {
                'num_row_groups': metadata.num_row_groups,
                'serialized_size': metadata.serialized_size
            }
        }

    except Exception as e:
        return {'error': str(e)}


# =============================================================================
# CSV-SPECIFIC UTILITIES
# =============================================================================

def sample_csv_structure(file_path: Union[str, Path],
                        sample_rows: int = 5,
                        encoding: str = 'utf-8') -> pd.DataFrame:
    """Sample CSV structure by reading first few rows."""
    return pd.read_csv(file_path, nrows=sample_rows, encoding=encoding)


def estimate_csv_rows_from_sample(file_path: Union[str, Path],
                                 sample_data: pd.DataFrame,
                                 encoding: str = 'utf-8') -> int:
    """Estimate total CSV rows based on sample and file size."""
    path_obj = Path(file_path)
    file_size = get_file_size_bytes(path_obj)

    if len(sample_data) == 0:
        return 0

    try:
        # Fallback: count lines (more accurate but slower)
        with open(path_obj, 'r', encoding=encoding) as f:
            line_count = sum(1 for _ in f)
        return max(0, line_count - 1)  # Subtract header
    except Exception:
        # Rough estimation based on file size if line counting fails
        estimated_bytes_per_row = file_size / (sample_rows + 1) if sample_rows > 0 else file_size
        return int(file_size / estimated_bytes_per_row) if estimated_bytes_per_row > 0 else 0


def get_csv_file_info(file_path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
    """Get comprehensive CSV file information."""
    try:
        file_size = get_file_size_bytes(file_path)
        sample_data = sample_csv_structure(file_path, encoding=encoding)

        if len(sample_data) > 0:
            estimated_rows = estimate_csv_rows_from_sample(file_path, sample_data, encoding)
            metadata = extract_dataframe_metadata(sample_data)

            return create_file_info_dict(
                rows=estimated_rows,
                columns=metadata['columns'],
                column_names=metadata['column_names'],
                file_size=file_size,
                data_types=metadata['data_types'],
                format_specific={
                    'encoding': encoding,
                    'sample_rows': len(sample_data)
                }
            )
        else:
            return create_file_info_dict(
                rows=0,
                file_size=file_size,
                format_specific={'encoding': encoding}
            )

    except Exception as e:
        return create_file_info_dict(
            file_size=get_file_size_bytes(file_path),
            error=str(e)
        )


# =============================================================================
# ODS-SPECIFIC UTILITIES
# =============================================================================

def sample_ods_structure(file_path: Union[str, Path],
                        sheet_name: Union[str, int] = 0,
                        sample_rows: int = 5) -> pd.DataFrame:
    """Sample ODS structure by reading first few rows."""
    return pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        engine='odf',
        nrows=sample_rows
    )


def get_ods_file_info(file_path: Union[str, Path],
                     sheet_name: Union[str, int] = 0) -> Dict[str, Any]:
    """Get comprehensive ODS file information."""
    try:
        file_size = get_file_size_bytes(file_path)
        sample_data = sample_ods_structure(file_path, sheet_name)

        if len(sample_data) > 0:
            metadata = extract_dataframe_metadata(sample_data)

            return create_file_info_dict(
                rows=None,  # Cannot efficiently estimate for ODS
                columns=metadata['columns'],
                column_names=metadata['column_names'],
                file_size=file_size,
                data_types=metadata['data_types'],
                format_specific={
                    'sheet_name': sheet_name,
                    'sample_rows': len(sample_data),
                    'note': 'Row count estimation not available for ODS format'
                }
            )
        else:
            return create_file_info_dict(
                file_size=file_size,
                format_specific={'sheet_name': sheet_name}
            )

    except Exception as e:
        return create_file_info_dict(
            file_size=get_file_size_bytes(file_path),
            error=str(e)
        )