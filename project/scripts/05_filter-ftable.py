#!/usr/bin/env python3
"""
Script 05: Filter Features from Feature Table
Filters out spurious sequences observed in low counts and/or few samples.

Task 5: Filtering features from the feature table
- Removes features (ASVs/OTUs) present in fewer than 2 samples
- Filters corresponding sequences to match filtered table
- Applies to both DADA2 and vsearch outputs
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import feature_table

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# Output directory for filtered features
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '05_filter-ftable')

# DADA2 inputs
DADA2_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.1_dada2')
DADA2_TABLE = os.path.join(DADA2_INPUT_DIR, 'table.qza')
DADA2_SEQS = os.path.join(DADA2_INPUT_DIR, 'rep-seqs.qza')

# vsearch inputs
VSEARCH_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.2_vsearch')
VSEARCH_TABLE = os.path.join(VSEARCH_INPUT_DIR, 'table-clustered-97.qza')
VSEARCH_SEQS = os.path.join(VSEARCH_INPUT_DIR, 'rep-seqs-clustered-97.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Filtering parameters
MIN_SAMPLES = 2  # Minimum number of samples a feature must be present in


def filter_features(table_path, seqs_path, output_dir, prefix, approach_name):
    """Filter features present in fewer than min_samples samples."""
    
    print("="*60)
    print(f"FILTERING FEATURES: {approach_name}")
    print("="*60)
    
    print(f"\nLoading:")
    print(f"  Table: {table_path}")
    print(f"  Sequences: {seqs_path}")
    
    table = Artifact.load(table_path)
    sequences = Artifact.load(seqs_path)
    
    print(f"\nFiltering parameters:")
    print(f"  --min-samples {MIN_SAMPLES}")
    print(f"  (Removes features present in < {MIN_SAMPLES} samples)")
    
    # Step 1: Filter feature table
    print(f"\n1. Filtering feature table...")
    filtered_table_result = feature_table.methods.filter_features(
        table=table,
        min_samples=MIN_SAMPLES
    )
    
    filtered_table_path = os.path.join(output_dir, f'{prefix}-table-ms{MIN_SAMPLES}.qza')
    filtered_table_result.filtered_table.save(filtered_table_path)
    print(f"   ✓ Saved: {filtered_table_path}")
    
    # Step 2: Filter sequences to match filtered table
    print(f"\n2. Filtering sequences to match filtered table...")
    filtered_seqs_result = feature_table.methods.filter_seqs(
        data=sequences,
        table=filtered_table_result.filtered_table
    )
    
    filtered_seqs_path = os.path.join(output_dir, f'{prefix}-rep-seqs-ms{MIN_SAMPLES}.qza')
    filtered_seqs_result.filtered_data.save(filtered_seqs_path)
    print(f"   ✓ Saved: {filtered_seqs_path}")
    
    # Generate summary visualizations
    print(f"\n3. Generating summary visualizations...")
    metadata = Metadata.load(METADATA_FILE)
    
    # Table summary
    table_viz = feature_table.visualizers.summarize(
        table=filtered_table_result.filtered_table,
        sample_metadata=metadata
    )
    table_viz_path = os.path.join(output_dir, f'{prefix}-table-ms{MIN_SAMPLES}.qzv')
    table_viz.visualization.save(table_viz_path)
    print(f"   ✓ Table summary: {table_viz_path}")
    
    # Sequences summary
    seqs_viz = feature_table.visualizers.tabulate_seqs(
        data=filtered_seqs_result.filtered_data
    )
    seqs_viz_path = os.path.join(output_dir, f'{prefix}-rep-seqs-ms{MIN_SAMPLES}.qzv')
    seqs_viz.visualization.save(seqs_viz_path)
    print(f"   ✓ Sequences summary: {seqs_viz_path}")
    
    print(f"\n✓ {approach_name} FILTERING COMPLETE")
    
    return filtered_table_path, filtered_seqs_path, table_viz_path, seqs_viz_path


def main():
    """Main workflow for Task 5: Filter Features."""
    
    print("\n" + "="*60)
    print("TASK 5: FILTERING FEATURES FROM FEATURE TABLE")
    print("="*60)
    print(f"\nFiltering criterion: Features must be present in ≥ {MIN_SAMPLES} samples")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    all_outputs = []
    
    # Filter DADA2 features
    if os.path.exists(DADA2_TABLE) and os.path.exists(DADA2_SEQS):
        print("\n" + "─"*60)
        print("Processing DADA2 outputs (ASVs)...")
        print("─"*60)
        
        dada2_outputs = filter_features(
            DADA2_TABLE,
            DADA2_SEQS,
            OUTPUT_DIR,
            'dada2-asv',
            'DADA2 (ASVs)'
        )
        all_outputs.extend(dada2_outputs)
    else:
        print(f"\n⚠️  DADA2 outputs not found, skipping...")
    
    # Filter vsearch features
    if os.path.exists(VSEARCH_TABLE) and os.path.exists(VSEARCH_SEQS):
        print("\n" + "─"*60)
        print("Processing vsearch outputs (OTUs)...")
        print("─"*60)
        
        vsearch_outputs = filter_features(
            VSEARCH_TABLE,
            VSEARCH_SEQS,
            OUTPUT_DIR,
            'vsearch-otu',
            'vsearch (OTUs)'
        )
        all_outputs.extend(vsearch_outputs)
    else:
        print(f"\n⚠️  vsearch outputs not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 5 COMPLETE: Feature Filtering")
    print("="*60)
    print(f"\nGenerated files ({len(all_outputs)}):")
    for output in all_outputs:
        print(f"  - {os.path.basename(output)}")
    print(f"\nNote: '_ms{MIN_SAMPLES}' indicates minimum {MIN_SAMPLES} samples filter")
    print("\nView .qzv files at: https://view.qiime2.org")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    main()