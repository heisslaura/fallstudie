#!/usr/bin/env python3
"""
Script 07.1.2: Beta Diversity Group Significance
Tests for associations between categorical metadata and beta diversity using PERMANOVA.

Task 7.1.2: Beta diversity group significance testing
- Tests unweighted UniFrac against categorical metadata
- Uses PERMANOVA (permutational multivariate analysis of variance)
- Performs pairwise comparisons between groups
- Tests sample-type, disease-state, and subject groupings
- Processes both ASV and OTU datasets
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import diversity

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIVERSITY_DIR = os.path.join(BASE_DIR, 'outputs', '07.1_a-b-div')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07.1.2_b-sig')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Metadata columns to test
METADATA_COLUMNS = ['sample-type', 'disease-state', 'subject']


def test_beta_significance(diversity_subdir, output_prefix, approach_name):
    """Test beta diversity for group significance using PERMANOVA."""
    
    print("="*60)
    print(f"BETA DIVERSITY SIGNIFICANCE: {approach_name}")
    print("="*60)
    
    diversity_path = os.path.join(DIVERSITY_DIR, diversity_subdir)
    
    # Load unweighted UniFrac distance matrix
    unweighted_unifrac_dm = Artifact.load(
        os.path.join(diversity_path, 'unweighted-unifrac-distance-matrix.qza')
    )
    
    metadata = Metadata.load(METADATA_FILE)
    
    print(f"\nTesting: Unweighted UniFrac distances")
    print(f"Metadata columns: {', '.join(METADATA_COLUMNS)}")
    print(f"Statistical test: PERMANOVA with pairwise comparisons")
    
    # Create output subdirectory
    output_subdir = os.path.join(OUTPUT_DIR, output_prefix)
    os.makedirs(output_subdir, exist_ok=True)
    
    # Test each metadata column
    for column in METADATA_COLUMNS:
        print(f"\nTesting: {column}")
        
        # Get metadata column
        metadata_column = metadata.get_column(column)
        
        # Test Unweighted UniFrac
        unifrac_viz = diversity.visualizers.beta_group_significance(
            distance_matrix=unweighted_unifrac_dm,
            metadata=metadata_column,
            pairwise=True
        )
        
        unifrac_path = os.path.join(
            output_subdir, 
            f'unweighted-unifrac-{column}-significance.qzv'
        )
        unifrac_viz.visualization.save(unifrac_path)
        print(f"  ✓ Saved: unweighted-unifrac-{column}-significance.qzv")
    
    print(f"\n✓ {approach_name} BETA SIGNIFICANCE TESTING COMPLETE")
    
    return output_subdir


def main():
    """Main workflow for Task 7.1.2: Beta Diversity Group Significance."""
    
    print("\n" + "="*60)
    print("TASK 7.1.2: BETA DIVERSITY GROUP SIGNIFICANCE")
    print("="*60)
    print(f"\nTests whether sample groups have significantly different microbiome compositions")
    print(f"Statistical test: PERMANOVA with pairwise comparisons")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    completed_tests = []
    
    # Test ASV beta diversity
    asv_diversity_dir = os.path.join(DIVERSITY_DIR, 'asv-core-metrics')
    if os.path.exists(asv_diversity_dir):
        print("\n" + "─"*60)
        print("Processing ASV data...")
        print("─"*60)
        
        asv_output = test_beta_significance(
            'asv-core-metrics',
            'asv',
            'ASV (DADA2)'
        )
        completed_tests.append(('ASV', asv_output))
    else:
        print(f"\n⚠️  ASV diversity data not found, skipping...")
    
    # Test OTU beta diversity
    otu_diversity_dir = os.path.join(DIVERSITY_DIR, 'otu-core-metrics')
    if os.path.exists(otu_diversity_dir):
        print("\n" + "─"*60)
        print("Processing OTU data...")
        print("─"*60)
        
        otu_output = test_beta_significance(
            'otu-core-metrics',
            'otu',
            'OTU (vsearch)'
        )
        completed_tests.append(('OTU', otu_output))
    else:
        print(f"\n⚠️  OTU diversity data not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 7.1.2 COMPLETE: Beta Diversity Significance")
    print("="*60)
    
    if completed_tests:
        print(f"\nCompleted tests:")
        for approach, output_dir in completed_tests:
            print(f"\n{approach} outputs in: {os.path.basename(output_dir)}/")
            for column in METADATA_COLUMNS:
                print(f"  - unweighted-unifrac-{column}-significance.qzv")
    
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    if not os.path.exists(DIVERSITY_DIR):
        raise FileNotFoundError(
            "Diversity results not found. Run Task 7.1 (diversity) first."
        )
    
    main()