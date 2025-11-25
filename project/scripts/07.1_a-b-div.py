#!/usr/bin/env python3
"""
Script 07.1: Alpha and Beta Diversity Analysis
Computes core diversity metrics (phylogenetic and non-phylogenetic) for microbiome analysis.

Task 7.1: Alpha and beta diversity analysis
- Rarefies feature tables to even sampling depth
- Computes alpha diversity metrics (Shannon, Faith PD, Observed Features, Evenness)
- Computes beta diversity metrics (Jaccard, Bray-Curtis, Unweighted UniFrac, Weighted UniFrac)
- Generates PCoA plots with Emperor
- Processes both ASV and OTU datasets
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import diversity

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILTER_DIR = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div')
PHYLO_DIR = os.path.join(BASE_DIR, 'outputs', '07_phylo-trees')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07.1_a-b-div')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# Input files - biological samples only
ASV_TABLE = os.path.join(FILTER_DIR, 'asv-table-bio.qza')
ASV_TREE = os.path.join(PHYLO_DIR, 'asv-rooted-tree.qza')
OTU_TABLE = os.path.join(FILTER_DIR, 'otu-table-bio.qza')
OTU_TREE = os.path.join(PHYLO_DIR, 'otu-rooted-tree.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Diversity analysis parameters
SAMPLING_DEPTH = 2700
N_JOBS = 'auto'


def run_core_metrics(table_path, tree_path, output_subdir, approach_name):
    """Run core-metrics-phylogenetic pipeline for diversity analysis."""
    
    print("="*60)
    print(f"DIVERSITY ANALYSIS: {approach_name}")
    print("="*60)
    
    print(f"\nLoading:")
    print(f"  Table: {table_path}")
    print(f"  Tree: {tree_path}")
    print(f"  Metadata: {METADATA_FILE}")
    
    table = Artifact.load(table_path)
    tree = Artifact.load(tree_path)
    metadata = Metadata.load(METADATA_FILE)
    
    print(f"\nParameters:")
    print(f"  --p-sampling-depth {SAMPLING_DEPTH}")
    print(f"  --p-n-jobs-or-threads '{N_JOBS}'")
    
    print(f"\nRunning core-metrics-phylogenetic...")
    print(f"This will compute:")
    print(f"  Alpha diversity: Shannon, Observed Features, Faith PD, Evenness")
    print(f"  Beta diversity: Jaccard, Bray-Curtis, Unweighted UniFrac, Weighted UniFrac")
    print(f"  PCoA plots for each beta diversity metric")
    
    # Create output subdirectory
    diversity_output_dir = os.path.join(OUTPUT_DIR, output_subdir)
    os.makedirs(diversity_output_dir, exist_ok=True)
    
    # Run core-metrics-phylogenetic pipeline
    diversity_results = diversity.pipelines.core_metrics_phylogenetic(
        table=table,
        phylogeny=tree,
        sampling_depth=SAMPLING_DEPTH,
        metadata=metadata,
        n_jobs_or_threads=N_JOBS
    )
    
    # Save all outputs
    print(f"\nSaving outputs to: {diversity_output_dir}/")
    
    # Rarefied table
    rarefied_table_path = os.path.join(diversity_output_dir, 'rarefied-table.qza')
    diversity_results.rarefied_table.save(rarefied_table_path)
    print(f"  ✓ Rarefied table: rarefied-table.qza")
    
    # Alpha diversity vectors
    faith_pd_path = os.path.join(diversity_output_dir, 'faith-pd-vector.qza')
    diversity_results.faith_pd_vector.save(faith_pd_path)
    print(f"  ✓ Faith PD: faith-pd-vector.qza")
    
    observed_features_path = os.path.join(diversity_output_dir, 'observed-features-vector.qza')
    diversity_results.observed_features_vector.save(observed_features_path)
    print(f"  ✓ Observed features: observed-features-vector.qza")
    
    shannon_path = os.path.join(diversity_output_dir, 'shannon-vector.qza')
    diversity_results.shannon_vector.save(shannon_path)
    print(f"  ✓ Shannon: shannon-vector.qza")
    
    evenness_path = os.path.join(diversity_output_dir, 'evenness-vector.qza')
    diversity_results.evenness_vector.save(evenness_path)
    print(f"  ✓ Evenness: evenness-vector.qza")
    
    # Beta diversity distance matrices
    jaccard_dm_path = os.path.join(diversity_output_dir, 'jaccard-distance-matrix.qza')
    diversity_results.jaccard_distance_matrix.save(jaccard_dm_path)
    print(f"  ✓ Jaccard distance matrix: jaccard-distance-matrix.qza")
    
    bray_curtis_dm_path = os.path.join(diversity_output_dir, 'bray-curtis-distance-matrix.qza')
    diversity_results.bray_curtis_distance_matrix.save(bray_curtis_dm_path)
    print(f"  ✓ Bray-Curtis distance matrix: bray-curtis-distance-matrix.qza")
    
    unweighted_unifrac_dm_path = os.path.join(diversity_output_dir, 'unweighted-unifrac-distance-matrix.qza')
    diversity_results.unweighted_unifrac_distance_matrix.save(unweighted_unifrac_dm_path)
    print(f"  ✓ Unweighted UniFrac distance matrix: unweighted-unifrac-distance-matrix.qza")
    
    weighted_unifrac_dm_path = os.path.join(diversity_output_dir, 'weighted-unifrac-distance-matrix.qza')
    diversity_results.weighted_unifrac_distance_matrix.save(weighted_unifrac_dm_path)
    print(f"  ✓ Weighted UniFrac distance matrix: weighted-unifrac-distance-matrix.qza")
    
    # PCoA results
    jaccard_pcoa_path = os.path.join(diversity_output_dir, 'jaccard-pcoa-results.qza')
    diversity_results.jaccard_pcoa_results.save(jaccard_pcoa_path)
    print(f"  ✓ Jaccard PCoA: jaccard-pcoa-results.qza")
    
    bray_curtis_pcoa_path = os.path.join(diversity_output_dir, 'bray-curtis-pcoa-results.qza')
    diversity_results.bray_curtis_pcoa_results.save(bray_curtis_pcoa_path)
    print(f"  ✓ Bray-Curtis PCoA: bray-curtis-pcoa-results.qza")
    
    unweighted_unifrac_pcoa_path = os.path.join(diversity_output_dir, 'unweighted-unifrac-pcoa-results.qza')
    diversity_results.unweighted_unifrac_pcoa_results.save(unweighted_unifrac_pcoa_path)
    print(f"  ✓ Unweighted UniFrac PCoA: unweighted-unifrac-pcoa-results.qza")
    
    weighted_unifrac_pcoa_path = os.path.join(diversity_output_dir, 'weighted-unifrac-pcoa-results.qza')
    diversity_results.weighted_unifrac_pcoa_results.save(weighted_unifrac_pcoa_path)
    print(f"  ✓ Weighted UniFrac PCoA: weighted-unifrac-pcoa-results.qza")
    
    # Emperor visualizations
    jaccard_emperor_path = os.path.join(diversity_output_dir, 'jaccard-emperor.qzv')
    diversity_results.jaccard_emperor.save(jaccard_emperor_path)
    print(f"  ✓ Jaccard Emperor plot: jaccard-emperor.qzv")
    
    bray_curtis_emperor_path = os.path.join(diversity_output_dir, 'bray-curtis-emperor.qzv')
    diversity_results.bray_curtis_emperor.save(bray_curtis_emperor_path)
    print(f"  ✓ Bray-Curtis Emperor plot: bray-curtis-emperor.qzv")
    
    unweighted_unifrac_emperor_path = os.path.join(diversity_output_dir, 'unweighted-unifrac-emperor.qzv')
    diversity_results.unweighted_unifrac_emperor.save(unweighted_unifrac_emperor_path)
    print(f"  ✓ Unweighted UniFrac Emperor plot: unweighted-unifrac-emperor.qzv")
    
    weighted_unifrac_emperor_path = os.path.join(diversity_output_dir, 'weighted-unifrac-emperor.qzv')
    diversity_results.weighted_unifrac_emperor.save(weighted_unifrac_emperor_path)
    print(f"  ✓ Weighted UniFrac Emperor plot: weighted-unifrac-emperor.qzv")
    
    print(f"\n✓ {approach_name} DIVERSITY ANALYSIS COMPLETE")
    
    return diversity_output_dir


def main():
    """Main workflow for Task 7.1: Diversity Analysis."""
    
    print("\n" + "="*60)
    print("TASK 7.1: ALPHA AND BETA DIVERSITY ANALYSIS")
    print("="*60)
    print(f"\nSampling depth: {SAMPLING_DEPTH} sequences per sample")
    print(f"Note: Samples with fewer sequences will be excluded")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    completed_analyses = []
    
    # Run ASV diversity analysis
    if os.path.exists(ASV_TABLE) and os.path.exists(ASV_TREE):
        print("\n" + "─"*60)
        print("Processing ASV data...")
        print("─"*60)
        
        asv_dir = run_core_metrics(
            ASV_TABLE,
            ASV_TREE,
            'asv-core-metrics',
            'ASV (DADA2)'
        )
        completed_analyses.append(('ASV', asv_dir))
    else:
        print(f"\n⚠️  ASV data not found, skipping...")
    
    # Run OTU diversity analysis
    if os.path.exists(OTU_TABLE) and os.path.exists(OTU_TREE):
        print("\n" + "─"*60)
        print("Processing OTU data...")
        print("─"*60)
        
        otu_dir = run_core_metrics(
            OTU_TABLE,
            OTU_TREE,
            'otu-core-metrics',
            'OTU (vsearch)'
        )
        completed_analyses.append(('OTU', otu_dir))
    else:
        print(f"\n⚠️  OTU data not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 7.1 COMPLETE: Diversity Analysis")
    print("="*60)
    
    if completed_analyses:
        print(f"\nCompleted analyses:")
        for approach, output_dir in completed_analyses:
            print(f"\n{approach} outputs in: {os.path.basename(output_dir)}/")
            print(f"  - 1 rarefied table")
            print(f"  - 4 alpha diversity vectors")
            print(f"  - 4 beta diversity distance matrices")
            print(f"  - 4 PCoA results")
            print(f"  - 4 Emperor visualizations (.qzv)")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    if not os.path.exists(ASV_TABLE) and not os.path.exists(OTU_TABLE):
        raise FileNotFoundError(
            "No filtered biological tables found. Run Task 7.0 (filter-for-div) first."
        )
    
    if not os.path.exists(ASV_TREE) and not os.path.exists(OTU_TREE):
        raise FileNotFoundError(
            "No phylogenetic trees found. Run Task 7.1 (phylogeny) first."
        )
    
    main()