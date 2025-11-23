#!/usr/bin/env python3
"""
Script 05: OTU Clustering with vsearch
Clusters features into OTUs using de novo clustering.

Task 4.2: qiime vsearch
- De novo clustering at 97% identity
- Traditional OTU approach for quality control
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import vsearch, feature_table

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.1_dada2')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.2_vsearch')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

TABLE_ARTIFACT = os.path.join(INPUT_DIR, 'table.qza')
REP_SEQS_ARTIFACT = os.path.join(INPUT_DIR, 'rep-seqs.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Clustering parameters
PERC_IDENTITY = 0.97
STRAND = 'plus'

def cluster_features(table_path, sequences_path, metadata_path):
    """Cluster features de novo using vsearch."""
    
    print("="*60)
    print("TASK 4.2: VSEARCH OTU CLUSTERING")
    print("="*60)
    
    print(f"\nLoading inputs:")
    print(f"  Table: {table_path}")
    print(f"  Sequences: {sequences_path}")
    
    table = Artifact.load(table_path)
    sequences = Artifact.load(sequences_path)
    metadata = Metadata.load(metadata_path)
    
    print(f"\nParameters:")
    print(f"  --p-perc-identity {PERC_IDENTITY}")
    
    print(f"\nRunning vsearch cluster-features-de-novo...\n")
    
    # Run clustering
    clustering_results = vsearch.methods.cluster_features_de_novo(
        table=table,
        sequences=sequences,
        perc_identity=PERC_IDENTITY,
        strand=STRAND,
        threads = 1
    )
    
    # Save outputs
    clustered_table_path = os.path.join(OUTPUT_DIR, 'table-clustered-97.qza')
    clustered_seqs_path = os.path.join(OUTPUT_DIR, 'rep-seqs-clustered-97.qza')
    
    clustering_results.clustered_table.save(clustered_table_path)
    clustering_results.clustered_sequences.save(clustered_seqs_path)
    
    print(f"\n" + "="*60)
    print("✓ CLUSTERING COMPLETE")
    print("="*60)
    print(f"\nOutputs:")
    print(f"  {clustered_table_path}")
    print(f"  {clustered_seqs_path}")
    
    # Generate visualizations
    print(f"\nGenerating visualizations...")
    
    table_viz = feature_table.visualizers.summarize(
        table=clustering_results.clustered_table,
        sample_metadata=metadata
    )
    table_viz_path = os.path.join(OUTPUT_DIR, 'table-clustered-97.qzv')
    table_viz.visualization.save(table_viz_path)
    
    seqs_viz = feature_table.visualizers.tabulate_seqs(
        data=clustering_results.clustered_sequences
    )
    seqs_viz_path = os.path.join(OUTPUT_DIR, 'rep-seqs-clustered-97.qzv')
    seqs_viz.visualization.save(seqs_viz_path)
    
    print(f"\nVisualizations:")
    print(f"  {table_viz_path}")
    print(f"  {seqs_viz_path}")
    print("="*60)

if __name__ == "__main__":
    if not os.path.exists(TABLE_ARTIFACT):
        raise FileNotFoundError(f"Run Task 4.1 (DADA2) first: {TABLE_ARTIFACT}")
    if not os.path.exists(REP_SEQS_ARTIFACT):
        raise FileNotFoundError(f"Run Task 4.1 (DADA2) first: {REP_SEQS_ARTIFACT}")
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    cluster_features(TABLE_ARTIFACT, REP_SEQS_ARTIFACT, METADATA_FILE)