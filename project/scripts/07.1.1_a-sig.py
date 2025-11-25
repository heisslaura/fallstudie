#!/usr/bin/env python3
"""
Script 07.1.1: Alpha Diversity Group Significance
Tests for associations between categorical metadata and alpha diversity metrics.

Task 7.1.1: Alpha diversity group significance testing
- Tests Faith PD, Evenness
- Compares groups by disease state, tissue type, and horse
- Uses Kruskal-Wallis test for significance
- Processes both ASV and OTU datasets
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import diversity

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIVERSITY_DIR = os.path.join(BASE_DIR, 'outputs', '07.1_a-b-div')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07.1.1_a-sig')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_alpha_significance(diversity_subdir, output_prefix, approach_name):
    """Test alpha diversity metrics for group significance."""
    
    print("="*60)
    print(f"ALPHA DIVERSITY SIGNIFICANCE: {approach_name}")
    print("="*60)
    
    diversity_path = os.path.join(DIVERSITY_DIR, diversity_subdir)
    
    # Load alpha diversity vectors
    faith_pd = Artifact.load(os.path.join(diversity_path, 'faith-pd-vector.qza'))
    evenness = Artifact.load(os.path.join(diversity_path, 'evenness-vector.qza'))
    
    metadata = Metadata.load(METADATA_FILE)
    
    print(f"\nTesting alpha diversity metrics:")
    print(f"  - Faith PD (phylogenetic diversity)")
    print(f"  - Evenness (distribution)")
    
    print(f"\nGrouping by categorical metadata columns")
    
    # Create output subdirectory
    output_subdir = os.path.join(OUTPUT_DIR, output_prefix)
    os.makedirs(output_subdir, exist_ok=True)
    
    # Test Faith PD
    print(f"\n1. Testing Faith PD...")
    faith_pd_viz = diversity.visualizers.alpha_group_significance(
        alpha_diversity=faith_pd,
        metadata=metadata
    )
    faith_pd_path = os.path.join(output_subdir, 'faith-pd-group-significance.qzv')
    faith_pd_viz.visualization.save(faith_pd_path)
    print(f"   ✓ Saved: faith-pd-group-significance.qzv")
    
    # Test Evenness
    print(f"\n4. Testing Evenness...")
    evenness_viz = diversity.visualizers.alpha_group_significance(
        alpha_diversity=evenness,
        metadata=metadata
    )
    evenness_path = os.path.join(output_subdir, 'evenness-group-significance.qzv')
    evenness_viz.visualization.save(evenness_path)
    print(f"   ✓ Saved: evenness-group-significance.qzv")
    
    print(f"\n✓ {approach_name} ALPHA SIGNIFICANCE TESTING COMPLETE")
    
    return output_subdir


def main():
    """Main workflow for Task 7.1.1: Alpha Diversity Group Significance."""
    
    print("\n" + "="*60)
    print("TASK 7.1.1: ALPHA DIVERSITY GROUP SIGNIFICANCE")
    print("="*60)
    print(f"\nTests associations between categorical metadata and alpha diversity")
    print(f"Statistical test: Kruskal-Wallis (non-parametric)")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    completed_tests = []
    
    # Test ASV alpha diversity
    asv_diversity_dir = os.path.join(DIVERSITY_DIR, 'asv-core-metrics')
    if os.path.exists(asv_diversity_dir):
        print("\n" + "─"*60)
        print("Processing ASV data...")
        print("─"*60)
        
        asv_output = test_alpha_significance(
            'asv-core-metrics',
            'asv',
            'ASV (DADA2)'
        )
        completed_tests.append(('ASV', asv_output))
    else:
        print(f"\n⚠️  ASV diversity data not found, skipping...")
    
    # Test OTU alpha diversity
    otu_diversity_dir = os.path.join(DIVERSITY_DIR, 'otu-core-metrics')
    if os.path.exists(otu_diversity_dir):
        print("\n" + "─"*60)
        print("Processing OTU data...")
        print("─"*60)
        
        otu_output = test_alpha_significance(
            'otu-core-metrics',
            'otu',
            'OTU (vsearch)'
        )
        completed_tests.append(('OTU', otu_output))
    else:
        print(f"\n⚠️  OTU diversity data not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 7.1.1 COMPLETE: Alpha Diversity Significance")
    print("="*60)
    
    if completed_tests:
        print(f"\nCompleted tests:")
        for approach, output_dir in completed_tests:
            print(f"\n{approach} outputs in: {os.path.basename(output_dir)}/")
            print(f"  - faith-pd-group-significance.qzv")
            print(f"  - evenness-group-significance.qzv")
    
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    if not os.path.exists(DIVERSITY_DIR):
        raise FileNotFoundError(
            "Diversity results not found. Run Task 7.1 (diversity) first."
        )
    
    main()