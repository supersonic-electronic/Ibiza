"""
Miscellaneous Utilities Module

Contains one-off utility functions for data transformations and maintenance tasks.
These are not part of the core system functionality but useful for data preparation.
"""

from pathlib import Path
from typing import Dict, Any

from src.core.utils import ensure_directory_exists, get_file_size_bytes


# =============================================================================
# FUTURES METADATA MERGE UTILITIES
# =============================================================================

def extract_instrument_code(contract_security: str) -> str:
    """
    Extract instrument code from contract security name.
    
    Examples:
        'ESH0 Index' -> 'ES'
        'CLZ5 Comdty' -> 'CL'
        'GCM3 Comdty' -> 'GC'
    """
    # Remove suffixes
    base = contract_security.replace(' Index', '').replace(' Comdty', '')
    
    # Extract instrument code by finding where numbers/month codes start
    # For futures, typically the instrument is 1-3 letters before the month/year code
    instrument = ''
    for i, char in enumerate(base):
        if char.isalpha():
            instrument += char
        else:
            # Stop at first non-letter
            break
    
    # Handle special case where month code is a letter (like H for March)
    # Common futures month codes: F,G,H,J,K,M,N,Q,U,V,X,Z
    month_codes = 'FGHJKMNQUVXZ'
    if len(instrument) > 2 and instrument[-1] in month_codes:
        # Remove the month code letter
        instrument = instrument[:-1]
    
    return instrument


def merge_futures_metadata(contract_data_path: Path, 
                         meta_data_path: Path,
                         output_path: Path,
                         drop_redundant: bool = True) -> None:
    """
    Merge contract-specific data with instrument metadata.
    
    Args:
        contract_data_path: Path to contract data parquet file
        meta_data_path: Path to metadata parquet file
        output_path: Path for merged output file
        drop_redundant: Whether to drop redundant columns
    """
    import pandas as pd
    
    # Load data
    contract_df = pd.read_parquet(contract_data_path)
    meta_df = pd.read_parquet(meta_data_path)
    
    print(f"Loading contract data: {contract_df.shape}")
    print(f"Loading meta data: {meta_df.shape}")
    
    # Extract instrument codes for joining
    contract_df['_instrument_code'] = contract_df['security'].apply(extract_instrument_code)
    
    # Extract instrument from meta security (ES1 Index -> ES)
    # Need to extract just the letters, not include the number
    meta_df['_instrument_code'] = meta_df['security'].apply(lambda x: ''.join(c for c in x.replace(' Index', '').replace(' Comdty', '') if c.isalpha()))
    
    # Identify columns to handle
    contract_cols = set(contract_df.columns)
    meta_cols = set(meta_df.columns)
    
    # Find overlapping columns (excluding join key)
    overlapping = (contract_cols & meta_cols) - {'_instrument_code'}
    print(f"Overlapping columns: {overlapping}")
    
    # Prepare meta dataframe for merge
    if drop_redundant:
        # Strategy: Keep contract version of overlapping columns
        meta_df_clean = meta_df.drop(columns=list(overlapping))
    else:
        # Keep both with suffixes
        meta_df_clean = meta_df
    
    # Perform merge
    merged_df = contract_df.merge(
        meta_df_clean, 
        on='_instrument_code', 
        how='left',
        suffixes=('', '_instrument')  # Only used if drop_redundant=False
    )
    
    # Handle specific redundancies
    if drop_redundant:
        # Exchange code consolidation
        if 'EXCH_CODE' in merged_df.columns and 'FUT_EXCH_NAME_SHRT' in merged_df.columns:
            # Prefer EXCH_CODE from meta, drop contract version
            merged_df = merged_df.drop(columns=['FUT_EXCH_NAME_SHRT'])
            merged_df = merged_df.rename(columns={'EXCH_CODE': 'exchange_code'})
        
        # Clean up security column naming
        if 'security_instrument' in merged_df.columns:
            merged_df = merged_df.rename(columns={
                'security': 'contract_security',
                'security_instrument': 'instrument_security'
            })
    
    # Drop temporary join column
    merged_df = merged_df.drop(columns=['_instrument_code'])
    
    # Reorder columns logically
    # Contract-specific first, then instrument-specific
    contract_specific_cols = [
        'security', 'FUT_LONG_NAME', 'FUT_MONTH_YR', 
        'FUT_NOTICE_FIRST', 'LAST_TRADEABLE_DT', 'FUT_DLV_DT_LAST',
        'ID_FULL_EXCHANGE_SYMBOL', 'EXCH_TRADE_STATUS', 'EXCH_MARKET_STATUS',
        'FUT_ROLL_DT', 'FUT_AGGTE_VOL'
    ]
    
    # Get instrument columns (all others)
    instrument_cols = [col for col in merged_df.columns if col not in contract_specific_cols]
    
    # Reorder
    final_cols = [col for col in contract_specific_cols if col in merged_df.columns] + instrument_cols
    merged_df = merged_df[final_cols]
    
    # Save merged data
    ensure_directory_exists(output_path.parent)
    merged_df.to_parquet(output_path, compression='snappy', index=False)
    
    print(f"\nMerge Summary:")
    print(f"- Merged {len(merged_df)} contracts with metadata")
    print(f"- Total columns: {len(merged_df.columns)}")
    print(f"- Dropped redundant columns: {overlapping if drop_redundant else 'None'}")
    print(f"- Output saved to: {output_path}")
    print(f"- File size: {get_file_size_bytes(output_path) / (1024 * 1024):.2f} MB")


def merge_all_futures_metadata(data_dir: Path, 
                             output_dir: Path,
                             pattern: str = "*") -> Dict[str, Any]:
    """
    Process all futures instruments in a directory.
    
    Args:
        data_dir: Directory containing futures data files
        output_dir: Output directory for merged files
        pattern: Glob pattern for instrument selection (default: "*" for all)
        
    Returns:
        Dictionary with merge statistics
    """
    from collections import defaultdict
    
    results = defaultdict(int)
    processed_instruments = []
    
    # Ensure output directory exists
    ensure_directory_exists(output_dir)
    
    # Find all meta files matching pattern
    meta_files = list(data_dir.glob(f"{pattern}_meta.parquet"))
    print(f"Found {len(meta_files)} metadata files to process")
    
    for meta_file in meta_files:
        # Extract instrument name
        instrument = meta_file.stem.replace('_meta', '')
        
        # Find corresponding contract data
        contract_file = data_dir / f"{instrument}_contract_data.parquet"
        
        if contract_file.exists():
            output_file = output_dir / f"{instrument}_merged_metadata.parquet"
            
            try:
                print(f"\nProcessing {instrument}...")
                merge_futures_metadata(contract_file, meta_file, output_file)
                results['success'] += 1
                processed_instruments.append(instrument)
            except Exception as e:
                print(f"Error merging {instrument}: {e}")
                results['failed'] += 1
        else:
            print(f"No contract data found for {instrument}")
            results['skipped'] += 1
    
    # Summary
    results['total'] = len(meta_files)
    results['processed_instruments'] = processed_instruments
    
    return dict(results)