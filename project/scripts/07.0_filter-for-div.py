#!/usr/bin/env python3
"""
Script 07.0: Filter Feature Tables for Diversity Analyses
Removes control samples (PK, NK) to create biological-samples-only datasets for phylogenetic and diversity analyses.

Task 7.0: Filter for diversity analyses
- Excludes positive control (PK) and negative control (NK)
- Retains only biological samples (gum and plaque from horses)
- Filters both feature tables and representative sequences
- Processes both ASV and OTU data
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import feature_table

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '05_filter-ftable')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# Input files (filtered features from Task 5)
ASV_TABLE = os.path.join(INPUT_DIR, 'dada2-asv-table-ms2.qza')
ASV_SEQS = os.path.join(INPUT_DIR, 'dada2-asv-rep-seqs-ms2.qza')
OTU_TABLE = os.path.join(INPUT_DIR, 'vsearch-otu-table-ms2.qza')
OTU_SEQS = os.path.join(INPUT_DIR, 'vsearch-otu-rep-seqs-ms2.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Metadata query to exclude controls - note the quotes around column name
EXCLUDE_CONTROLS_QUERY = "[sample-id] NOT IN ('PK', 'NK')"


def filter_controls(table_path, seqs_path, output_prefix, approach_name):
    """Filter out control samples, keeping only biological samples."""
    
    print("="*60)
    print(f"FILTERING CONTROLS: {approach_name}")
    print("="*60)
    
    print(f"\nLoading:")
    print(f"  Table: {table_path}")
    print(f"  Sequences: {seqs_path}")
    
    table = Artifact.load(table_path)
    sequences = Artifact.load(seqs_path)
    metadata = Metadata.load(METADATA_FILE)
    
    print(f"\nFiltering criteria:")
    print(f"  Exclude: PK (positive control), NK (negative control)")
    print(f"  Retain: Only biological samples")
    print(f"  Query: {EXCLUDE_CONTROLS_QUERY}")
    
    # Step 1: Filter samples from feature table
    print(f"\n1. Filtering control samples from feature table...")
    filtered_table_result = feature_table.methods.filter_samples(
        table=table,
        metadata=metadata,
        where=EXCLUDE_CONTROLS_QUERY
    )
    
    bio_table_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-table-bio.qza')
    filtered_table_result.filtered_table.save(bio_table_path)
    print(f"   ✓ Saved: {bio_table_path}")
    
    # Step 2: Filter sequences to match biological-only table
    print(f"\n2. Filtering sequences to match biological samples...")
    filtered_seqs_result = feature_table.methods.filter_seqs(
        data=sequences,
        table=filtered_table_result.filtered_table
    )
    
    bio_seqs_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-rep-seqs-bio.qza')
    filtered_seqs_result.filtered_data.save(bio_seqs_path)
    print(f"   ✓ Saved: {bio_seqs_path}")
    
    # Step 3: Generate summary visualizations
    print(f"\n3. Generating summary visualizations...")
    
    # Table summary
    table_viz = feature_table.visualizers.summarize(
        table=filtered_table_result.filtered_table,
        sample_metadata=metadata
    )
    table_viz_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-table-bio.qzv')
    table_viz.visualization.save(table_viz_path)
    print(f"   ✓ Table summary: {table_viz_path}")
    
    # Sequences summary
    seqs_viz = feature_table.visualizers.tabulate_seqs(
        data=filtered_seqs_result.filtered_data
    )
    seqs_viz_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-rep-seqs-bio.qzv')
    seqs_viz.visualization.save(seqs_viz_path)
    print(f"   ✓ Sequences summary: {seqs_viz_path}")
    
    print(f"\n✓ {approach_name} CONTROL FILTERING COMPLETE")
    
    return bio_table_path, bio_seqs_path, table_viz_path, seqs_viz_path


def main():
    """Main workflow for Task 7.0: Filter for Diversity Analyses."""
    
    print("\n" + "="*60)
    print("TASK 7.0: FILTER FOR DIVERSITY ANALYSES")
    print("="*60)
    print(f"\nRemoving control samples to prepare for phylogenetic and diversity analyses")
    print(f"Controls to exclude: PK (positive), NK (negative)")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    all_outputs = []
    
    # Filter ASV data
    if os.path.exists(ASV_TABLE) and os.path.exists(ASV_SEQS):
        print("\n" + "─"*60)
        print("Processing ASV data...")
        print("─"*60)
        
        asv_outputs = filter_controls(
            ASV_TABLE,
            ASV_SEQS,
            'asv',
            'ASV (DADA2)'
        )
        all_outputs.extend(asv_outputs)
    else:
        print(f"\n⚠️  ASV data not found, skipping...")
    
    # Filter OTU data
    if os.path.exists(OTU_TABLE) and os.path.exists(OTU_SEQS):
        print("\n" + "─"*60)
        print("Processing OTU data...")
        print("─"*60)
        
        otu_outputs = filter_controls(
            OTU_TABLE,
            OTU_SEQS,
            'otu',
            'OTU (vsearch)'
        )
        all_outputs.extend(otu_outputs)
    else:
        print(f"\n⚠️  OTU data not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 7.0 COMPLETE: Control Filtering")
    print("="*60)
    print(f"\nGenerated files ({len(all_outputs)}):")
    for output in all_outputs:
        print(f"  - {os.path.basename(output)}")
    print(f"\nNote: '_bio' indicates biological samples only (controls excluded)")
    print("\nThese filtered datasets are ready for:")
    print("  - Phylogenetic tree generation (Task 7.1)")
    print("  - Alpha/beta diversity analyses (Task 7.2)")
    print("\nView .qzv files at: https://view.qiime2.org")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    if not os.path.exists(ASV_TABLE) and not os.path.exists(OTU_TABLE):
        raise FileNotFoundError(
            "No filtered feature tables found. Run Task 5 (filter-ftable) first."
        )
    
    main()