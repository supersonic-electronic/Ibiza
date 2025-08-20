#!/usr/bin/env python3
"""
Example script showing how to use the metadata merge utilities.

Usage:
    # Merge single instrument
    poetry run python merge_metadata_example.py
    
    # Merge all instruments
    poetry run python merge_metadata_example.py --all
    
    # Merge specific pattern
    poetry run python merge_metadata_example.py --pattern "ES*"
"""

import argparse
from pathlib import Path
from src.core.misc_utils import merge_futures_metadata, merge_all_futures_metadata


def main():
    parser = argparse.ArgumentParser(description="Merge futures contract and metadata files")
    parser.add_argument('--all', action='store_true', help='Process all instruments')
    parser.add_argument('--pattern', default='*', help='Pattern for instrument selection (e.g., "ES*")')
    parser.add_argument('--input-dir', default='data/futures', help='Input directory')
    parser.add_argument('--output-dir', default='data/futures/metadata', help='Output directory')
    
    args = parser.parse_args()
    
    data_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if args.all:
        # Process all instruments
        print(f"Merging all futures metadata from {data_dir}")
        results = merge_all_futures_metadata(data_dir, output_dir, pattern=args.pattern)
        
        print("\n=== Final Summary ===")
        print(f"Total files found: {results['total']}")
        print(f"Successfully merged: {results['success']}")
        print(f"Failed: {results.get('failed', 0)}")
        print(f"Skipped (no contract data): {results.get('skipped', 0)}")
        
        if results['processed_instruments']:
            print(f"\nProcessed instruments: {', '.join(results['processed_instruments'])}")
    else:
        # Single instrument example - ES1 Index
        print("Merging ES1 Index metadata as example...")
        
        contract_file = data_dir / "ES1 Index_contract_data.parquet"
        meta_file = data_dir / "ES1 Index_meta.parquet"
        output_file = output_dir / "ES1 Index_merged_metadata.parquet"
        
        if contract_file.exists() and meta_file.exists():
            merge_futures_metadata(contract_file, meta_file, output_file)
        else:
            print(f"Error: Required files not found in {data_dir}")
            print(f"  Contract file: {contract_file.exists()}")
            print(f"  Meta file: {meta_file.exists()}")


if __name__ == "__main__":
    main()