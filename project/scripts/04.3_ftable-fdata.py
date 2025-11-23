#!/usr/bin/env python3
"""
Script 04.3: Feature Table Summaries
Creates visual summaries of feature tables and sequences for both approaches.

Task 4.3: FeatureTable and FeatureData summaries
- Feature table summary with sample/feature statistics
- Representative sequences with BLAST links
- Generates summaries for both DADA2 (ASVs) and vsearch (OTUs)
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import feature_table

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.3_ftable-fdata')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# DADA2 inputs
DADA2_DIR = os.path.join(BASE_DIR, 'outputs', '04.1_dada2')
DADA2_TABLE = os.path.join(DADA2_DIR, 'table.qza')
DADA2_SEQS = os.path.join(DADA2_DIR, 'rep-seqs.qza')

# vsearch inputs
VSEARCH_DIR = os.path.join(BASE_DIR, 'outputs', '04.2_vsearch')
VSEARCH_TABLE = os.path.join(VSEARCH_DIR, 'table-clustered-97.qza')
VSEARCH_SEQS = os.path.join(VSEARCH_DIR, 'rep-seqs-clustered-97.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_summaries(table_path, sequences_path, metadata_path, prefix, approach_name):
    """Create visual summaries of feature table and sequences."""
    
    print("="*60)
    print(f"FEATURE TABLE SUMMARIES: {approach_name}")
    print("="*60)
    
    print(f"\nLoading:")
    print(f"  Table: {table_path}")
    print(f"  Sequences: {sequences_path}")
    print(f"  Metadata: {metadata_path}")
    
    table = Artifact.load(table_path)
    sequences = Artifact.load(sequences_path)
    metadata = Metadata.load(metadata_path)
    
    print(f"\nGenerating feature-table summaries...")
    
    # 1. Feature table summary
    print(f"\n1. Creating {approach_name} feature-table summary...")
    table_viz = feature_table.visualizers.summarize(
        table=table,
        sample_metadata=metadata
    )
    table_viz_path = os.path.join(OUTPUT_DIR, f'{prefix}-table-summary.qzv')
    table_viz.visualization.save(table_viz_path)
    print(f"   ✓ Saved: {table_viz_path}")
    
    # 2. Representative sequences tabulation
    print(f"\n2. Creating {approach_name} representative sequences tabulation...")
    seqs_viz = feature_table.visualizers.tabulate_seqs(
        data=sequences
    )
    seqs_viz_path = os.path.join(OUTPUT_DIR, f'{prefix}-rep-seqs-summary.qzv')
    seqs_viz.visualization.save(seqs_viz_path)
    print(f"   ✓ Saved: {seqs_viz_path}")
    
    print(f"\n✓ {approach_name} SUMMARIES COMPLETE")
    print(f"  {table_viz_path}")
    print(f"  {seqs_viz_path}")
    
    return table_viz_path, seqs_viz_path


def main():
    """Main workflow for Task 4.3: Feature Table Summaries."""
    
    print("\n" + "="*60)
    print("TASK 4.3: FEATURE TABLE AND FEATURE DATA SUMMARIES")
    print("="*60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    metadata = Metadata.load(METADATA_FILE)
    all_outputs = []
    
    # Generate DADA2 summaries
    if os.path.exists(DADA2_TABLE) and os.path.exists(DADA2_SEQS):
        print("\n" + "─"*60)
        print("Processing DADA2 outputs (ASVs)...")
        print("─"*60)
        dada2_outputs = create_summaries(
            DADA2_TABLE, 
            DADA2_SEQS, 
            METADATA_FILE,
            'dada2-asv',
            'DADA2 (ASVs)'
        )
        all_outputs.extend(dada2_outputs)
    else:
        print(f"\n⚠️  DADA2 outputs not found, skipping...")
    
    # Generate vsearch summaries
    if os.path.exists(VSEARCH_TABLE) and os.path.exists(VSEARCH_SEQS):
        print("\n" + "─"*60)
        print("Processing vsearch outputs (OTUs)...")
        print("─"*60)
        vsearch_outputs = create_summaries(
            VSEARCH_TABLE,
            VSEARCH_SEQS,
            METADATA_FILE,
            'vsearch-otu',
            'vsearch (OTUs)'
        )
        all_outputs.extend(vsearch_outputs)
    else:
        print(f"\n⚠️  vsearch outputs not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 4.3 COMPLETE: Feature Table Summaries")
    print("="*60)
    print(f"\nGenerated visualizations ({len(all_outputs)}):")
    for viz in all_outputs:
        print(f"  - {os.path.basename(viz)}")
    print(f"\nView these files at: https://view.qiime2.org")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    main()