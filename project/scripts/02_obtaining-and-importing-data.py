#!/usr/bin/env python3
"""
Script 02: Import Sequencing Data into QIIME2
Imports paired-end demultiplexed FASTQ files into QIIME2 artifact format.

Task 2: Data Import
- Creates manifest file mapping sample IDs to FASTQ file paths
- Imports paired-end sequences using Artifact.import_data()
- Outputs: paired-end-sequences.qza artifact
"""

import os
import pandas as pd
from qiime2 import Artifact

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw', '20241209-raw_data')
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
METADATA_FILE = os.path.join(DATA_PROCESSED_DIR, 'sample-metadata.tsv')
MANIFEST_FILE = os.path.join(DATA_PROCESSED_DIR, 'manifest.tsv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '02_import')

# Create directories
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_manifest():
    """Create manifest file for QIIME2 import of paired-end reads."""
    
    print("Creating manifest file for paired-end FASTQ files...")
    print(f"Scanning directory: {DATA_RAW_DIR}")
    
    # Read metadata to get sample IDs
    metadata = pd.read_csv(METADATA_FILE, sep='\t', comment='#', index_col=0)
    sample_ids = metadata.index.tolist()
    
    print(f"Found {len(sample_ids)} samples in metadata")
    
    # Create manifest entries
    manifest_data = []
    missing_files = []
    
    for sample_id in sample_ids:
        # Expected file names: SAMPLEID_1.fastq.gz and SAMPLEID_2.fastq.gz
        forward_file = os.path.join(DATA_RAW_DIR, f"{sample_id}_1.fastq.gz")
        reverse_file = os.path.join(DATA_RAW_DIR, f"{sample_id}_2.fastq.gz")
        
        # Check if files exist
        if os.path.exists(forward_file) and os.path.exists(reverse_file):
            manifest_data.append({
                'sample-id': sample_id,
                'forward-absolute-filepath': forward_file,
                'reverse-absolute-filepath': reverse_file
            })
        else:
            missing_files.append(sample_id)
            if not os.path.exists(forward_file):
                print(f"  WARNING: Missing forward read: {forward_file}")
            if not os.path.exists(reverse_file):
                print(f"  WARNING: Missing reverse read: {reverse_file}")
    
    if missing_files:
        print(f"\n⚠️  Missing FASTQ files for {len(missing_files)} samples: {missing_files}")
        raise FileNotFoundError(f"Missing files for samples: {missing_files}")
    
    # Create DataFrame and save manifest
    manifest_df = pd.DataFrame(manifest_data)
    manifest_df.to_csv(MANIFEST_FILE, sep='\t', index=False)
    
    print(f"\n✓ Manifest file created: {MANIFEST_FILE}")
    print(f"  Total samples: {len(manifest_data)}")
    
    return MANIFEST_FILE

def import_sequences(manifest_file):
    """Import paired-end sequences into QIIME2 artifact."""
    
    print("\n" + "="*60)
    print("Importing sequences into QIIME2 artifact...")
    print("="*60)
    
    output_path = os.path.join(OUTPUT_DIR, 'paired-end-sequences.qza')
    
    print("Reading manifest and importing FASTQ files...")
    
    # Import using Artifact.import_data()
    sequences = Artifact.import_data(
        'SampleData[PairedEndSequencesWithQuality]',
        manifest_file,
        view_type='PairedEndFastqManifestPhred33V2'
    )
    
    # Save the artifact
    sequences.save(output_path)
    
    print(f"\n✓ Sequences imported successfully!")
    print(f"  Artifact saved: {output_path}")
    print(f"  Artifact type: SampleData[PairedEndSequencesWithQuality]")
    
    return output_path

def main():
    """Main workflow for Task 2: Import Data."""
    
    print("="*60)
    print("TASK 2: IMPORT SEQUENCING DATA")
    print("="*60)
    print(f"\nProject structure:")
    print(f"  Raw FASTQ directory: {DATA_RAW_DIR}")
    print(f"  Metadata file: {METADATA_FILE}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    # Step 1: Create manifest file
    manifest_file = create_manifest()
    
    # Step 2: Import sequences into QIIME2 artifact
    artifact_path = import_sequences(manifest_file)
    
    # Summary
    print("\n" + "="*60)
    print("✓ TASK 2 COMPLETE: Import Sequencing Data")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  1. Manifest: {MANIFEST_FILE}")
    print(f"  2. Artifact: {artifact_path}")
    
if __name__ == "__main__":
    main()