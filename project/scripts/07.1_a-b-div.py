#!/usr/bin/env python3
"""
Script 07.1: Core Metrics Phylogenetic (ASV and OTU)
Computes alpha and beta diversity metrics with rarefaction.
"""

import os
from qiime2 import Artifact, Metadata
import qiime2.plugins.diversity.actions as diversity_actions

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DADA2_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.1_dada2')
VSEARCH_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.2_vsearch')
PHYLOGENY_DIR = os.path.join(BASE_DIR, 'outputs', '07_phylogeny')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# ASV inputs
ASV_TABLE = os.path.join(DADA2_INPUT_DIR, 'table.qza')
ASV_TREE = os.path.join(PHYLOGENY_DIR, 'dada2-rooted-tree.qza')

# OTU inputs
OTU_TABLE = os.path.join(VSEARCH_INPUT_DIR, 'table-clustered-97.qza')
OTU_TREE = os.path.join(PHYLOGENY_DIR, 'vsearch-rooted-tree.qza')

# Output directories
ASV_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07.1_diversity_asv')
OTU_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07.1_diversity_otu')

# Sampling depth: 2839 retains 22 samples (excludes only NK with 0 reads)
SAMPLING_DEPTH = 2839


def run_core_metrics(table_path, tree_path, output_dir, label):
    """Run core-metrics-phylogenetic for a given table and tree."""
    
    print("\n" + "="*70)
    print(f"Processing {label}")
    print("="*70)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading inputs...")
    table = Artifact.load(table_path)
    rooted_tree = Artifact.load(tree_path)
    sample_metadata_md = Metadata.load(METADATA_FILE)
    
    print(f"Running core-metrics-phylogenetic (sampling depth: {SAMPLING_DEPTH})...")
    
    action_results = diversity_actions.core_metrics_phylogenetic(
        phylogeny=rooted_tree,
        table=table,
        sampling_depth=SAMPLING_DEPTH,
        metadata=sample_metadata_md,
    )
    
    rarefied_table = action_results.rarefied_table
    faith_pd_vector = action_results.faith_pd_vector
    observed_features_vector = action_results.observed_features_vector
    shannon_vector = action_results.shannon_vector
    evenness_vector = action_results.evenness_vector
    unweighted_unifrac_distance_matrix = action_results.unweighted_unifrac_distance_matrix
    weighted_unifrac_distance_matrix = action_results.weighted_unifrac_distance_matrix
    jaccard_distance_matrix = action_results.jaccard_distance_matrix
    bray_curtis_distance_matrix = action_results.bray_curtis_distance_matrix
    unweighted_unifrac_pcoa_results = action_results.unweighted_unifrac_pcoa_results
    weighted_unifrac_pcoa_results = action_results.weighted_unifrac_pcoa_results
    jaccard_pcoa_results = action_results.jaccard_pcoa_results
    bray_curtis_pcoa_results = action_results.bray_curtis_pcoa_results
    unweighted_unifrac_emperor_viz = action_results.unweighted_unifrac_emperor
    weighted_unifrac_emperor_viz = action_results.weighted_unifrac_emperor
    jaccard_emperor_viz = action_results.jaccard_emperor
    bray_curtis_emperor_viz = action_results.bray_curtis_emperor
    
    print("Saving outputs...")
    
    rarefied_table.save(os.path.join(output_dir, 'rarefied_table.qza'))
    faith_pd_vector.save(os.path.join(output_dir, 'faith_pd_vector.qza'))
    observed_features_vector.save(os.path.join(output_dir, 'observed_features_vector.qza'))
    shannon_vector.save(os.path.join(output_dir, 'shannon_vector.qza'))
    evenness_vector.save(os.path.join(output_dir, 'evenness_vector.qza'))
    unweighted_unifrac_distance_matrix.save(os.path.join(output_dir, 'unweighted_unifrac_distance_matrix.qza'))
    weighted_unifrac_distance_matrix.save(os.path.join(output_dir, 'weighted_unifrac_distance_matrix.qza'))
    jaccard_distance_matrix.save(os.path.join(output_dir, 'jaccard_distance_matrix.qza'))
    bray_curtis_distance_matrix.save(os.path.join(output_dir, 'bray_curtis_distance_matrix.qza'))
    unweighted_unifrac_pcoa_results.save(os.path.join(output_dir, 'unweighted_unifrac_pcoa_results.qza'))
    weighted_unifrac_pcoa_results.save(os.path.join(output_dir, 'weighted_unifrac_pcoa_results.qza'))
    jaccard_pcoa_results.save(os.path.join(output_dir, 'jaccard_pcoa_results.qza'))
    bray_curtis_pcoa_results.save(os.path.join(output_dir, 'bray_curtis_pcoa_results.qza'))
    unweighted_unifrac_emperor_viz.save(os.path.join(output_dir, 'unweighted_unifrac_emperor.qzv'))
    weighted_unifrac_emperor_viz.save(os.path.join(output_dir, 'weighted_unifrac_emperor.qzv'))
    jaccard_emperor_viz.save(os.path.join(output_dir, 'jaccard_emperor.qzv'))
    bray_curtis_emperor_viz.save(os.path.join(output_dir, 'bray_curtis_emperor.qzv'))
    
    print(f"✓ {label} complete: {output_dir}")


def main():
    print("\n" + "="*70)
    print("TASK 7.1: CORE METRICS PHYLOGENETIC")
    print("="*70)
    print(f"Sampling depth: {SAMPLING_DEPTH} (retains 22 samples, excludes NK)")
    print("="*70)
    
    # Process ASV (DADA2)
    run_core_metrics(ASV_TABLE, ASV_TREE, ASV_OUTPUT_DIR, "ASV (DADA2)")
    
    # Process OTU (vsearch)
    run_core_metrics(OTU_TABLE, OTU_TREE, OTU_OUTPUT_DIR, "OTU (vsearch)")
    
    print("\n" + "="*70)
    print("✓ ALL COMPLETE")
    print("="*70)
    print(f"ASV outputs: {ASV_OUTPUT_DIR}")
    print(f"OTU outputs: {OTU_OUTPUT_DIR}")
    print("="*70)


if __name__ == "__main__":
    main()