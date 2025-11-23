#!/usr/bin/env python3
"""
Script 01: Sample Metadata Preparation and Exploration
Converts Excel metadata to QIIME2-compatible TSV format and creates visualization.

Task 1: Sample Metadata
- Reads Excel metadata file
- Converts to QIIME2-compatible TSV format
- Anonymizes horse names to protect identity
- Creates QIIME2 visualization using metadata tabulate
"""

import os
import pandas as pd
from qiime2 import Metadata

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
EXCEL_FILE = os.path.join(DATA_RAW_DIR, 'EOTRH-MetadatenProben-WS2025.xlsx')
METADATA_TSV = os.path.join(DATA_PROCESSED_DIR, 'sample-metadata.tsv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '01_metadata')

# Create directories
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def convert_excel_to_qiime_metadata():
    """Convert Excel metadata file to QIIME2-compatible TSV format."""
    
    print("Reading Excel metadata file...")
    print(f"Input: {EXCEL_FILE}")
    
    # Read Excel file
    df = pd.read_excel(EXCEL_FILE)
    
    # The actual headers are in the first row
    new_columns = df.iloc[0].tolist()
    df = df[1:].reset_index(drop=True)
    df.columns = new_columns
    
    print(f"Original shape: {df.shape}")
    print(f"Original columns: {list(df.columns)}")
    
    # Rename columns to QIIME2-compatible format (no spaces, lowercase with hyphens)
    column_mapping = {
        'Seq Pos': 'seq-pos',
        'Abbr': 'sample-id',
        'Horse': 'subject',        # Changed from 'horse' to 'subject'
        'Type': 'sample-type',
        'Tooth #': 'tooth-number',
        'Tooth location': 'tooth-location',
        'Replicate': 'replicate',
        'Gender': 'gender',
        'Age': 'age',
        'disease state': 'disease-state',
        'DIN': 'din'
    }
    
    df = df.rename(columns=column_mapping)
    
    print(f"\nOriginal subject names: {df['subject'].unique()}")
    
    # Anonymize horse names and ensure QIIME2-compatible naming (no spaces)
    subject_mapping = {
        'Kommi': 'Horse-1',
        'Threnna': 'Horse-2',
        'Eydis': 'Horse-3',
        'E. coli': 'E-coli',   # Positive control
        'H2O': 'H2O'           # Negative control
    }
    
    df['subject'] = df['subject'].map(subject_mapping)
    
# Set 'sample-type' for controls 
    # For positive control (E-coli)
    df.loc[df['subject'] == 'E-coli', 'sample-type'] = 'Positive-Control'
    
    # For negative control (H2O)
    df.loc[df['subject'] == 'H2O', 'sample-type'] = 'Negative-Control'


    print(f"Anonymized subject names: {df['subject'].unique()}")
    
    # Set sample-id as index
    df = df.set_index('sample-id')
    
    print(f"\nProcessed metadata:")
    print(f"Number of samples: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample breakdown:")
    print(f"  Subjects: {df['subject'].unique()}")
    print(f"  Disease states: {df['disease-state'].unique()}")
    print(f"  Sample types: {df['sample-type'].unique()}")
    
    # Convert numeric columns to appropriate types
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df['din'] = pd.to_numeric(df['din'], errors='coerce')
    df['seq-pos'] = pd.to_numeric(df['seq-pos'], errors='coerce')
    df['tooth-number'] = pd.to_numeric(df['tooth-number'], errors='coerce')
    df['replicate'] = pd.to_numeric(df['replicate'], errors='coerce')
    
    # Define column types for QIIME2
    column_types = []
    for col in df.columns:
        # Check for column type based on potential usage in QIIME 2
        # 'sample-type' is now explicitly categorical for control/real samples
        if col in ['age', 'din', 'seq-pos', 'tooth-number', 'replicate']:
            column_types.append('numeric')
        else:
            column_types.append('categorical')
    
    # Write metadata file with QIIME2 header
    with open(METADATA_TSV, 'w') as f:
        # Write header with sample-id
        f.write('sample-id\t' + '\t'.join(df.columns) + '\n')
        # Write column types (required by QIIME2)
        f.write('#q2:types\t' + '\t'.join(column_types) + '\n')
    
    # Append data
    df.to_csv(METADATA_TSV, sep='\t', mode='a', header=False)
    
    print(f"\n✓ Metadata TSV file created: {METADATA_TSV}")
    
    return METADATA_TSV

def create_metadata_visualization(metadata_file):
    """Generate QIIME2 metadata visualization using tabulate."""
    
    print("\n" + "="*60)
    print("Creating QIIME2 metadata visualization...")
    print("="*60)
    
    # Load metadata
    print(f"Loading metadata from: {metadata_file}")
    metadata = Metadata.load(metadata_file)
    
    print(f"\nLoaded metadata:")
    print(f"  Number of samples: {len(metadata.ids)}")
    print(f"  Sample IDs (first 10): {list(metadata.ids)[:10]}")
    print(f"  Metadata columns: {list(metadata.columns.keys())}")
    
    # Create visualization using QIIME2's metadata tabulate
    print("\nGenerating tabulate visualization...")
    from qiime2.plugins import metadata as metadata_plugin
    
    visualization = metadata_plugin.actions.tabulate(
        input=metadata
    )
    
    # Save visualization
    output_path = os.path.join(OUTPUT_DIR, 'sample-metadata.qzv')
    visualization.visualization.save(output_path)
    
    print(f"\n✓ Metadata visualization saved to: {output_path}")
    
    return output_path

def main():
    """Main workflow for Task 1: Sample Metadata."""
    
    print("="*60)
    print("TASK 1: SAMPLE METADATA PREPARATION")
    print("="*60)
    print(f"\nProject structure:")
    print(f"  Base directory: {BASE_DIR}")
    print(f"  Raw data: {DATA_RAW_DIR}")
    print(f"  Processed data: {DATA_PROCESSED_DIR}")
    print(f"  Outputs: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    # Step 1: Convert Excel to QIIME2-compatible TSV
    metadata_file = convert_excel_to_qiime_metadata()
    
    # Step 2: Create QIIME2 visualization
    viz_path = create_metadata_visualization(metadata_file)
    
    # Summary
    print("\n" + "="*60)
    print("✓ TASK 1 COMPLETE: Sample Metadata")
    print("="*60)

if __name__ == "__main__":
    main()