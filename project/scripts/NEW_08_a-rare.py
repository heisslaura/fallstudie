#!/usr/bin/env python3
"""
Script 07.2: Alpha Rarefaction Plotting
Generate alpha rarefaction curves to assess sampling depth adequacy.

Task 7.2: Alpha rarefaction plotting
- Computes alpha diversity metrics at multiple sampling depths
- Generates rarefaction curves to assess if sampling depth is adequate
- Shows if richness plateaus (full observation) or continues increasing
- Displays sample retention at each rarefaction depth
- Processes both ASV and OTU datasets
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import diversity

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '08_alpha-rarefaction')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# ASV inputs
ASV_TABLE = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'asv-table-bio.qza')
ASV_TREE = os.path.join(BASE_DIR, 'outputs', '07_phylo-trees', 'asv-rooted-tree.qza')

# OTU inputs
OTU_TABLE = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'otu-table-bio.qza')
OTU_TREE = os.path.join(BASE_DIR, 'outputs', '07_phylo-trees', 'otu-rooted-tree.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_alpha_rarefaction(table_path, tree_path, output_prefix, approach_name, max_depth):
    """
    Generate alpha rarefaction curves.
    
    Parameters:
    -----------
    max_depth : int
        Maximum rarefaction depth (use median frequency from table.qzv)
        Based on previous rarefaction at 2700, use ~4000 for exploration
    """
    print("="*60)
    print(f"ALPHA RAREFACTION: {approach_name}")
    print("="*60)
    
    # Load inputs
    table = Artifact.load(table_path)
    tree = Artifact.load(tree_path)
    metadata = Metadata.load(METADATA_FILE)
    
    print(f"\nTable: {os.path.basename(table_path)}")
    print(f"Tree: {os.path.basename(tree_path)}")
    print(f"Max depth: {max_depth}")
    print(f"Metadata: {os.path.basename(METADATA_FILE)}")
    
    # Generate alpha rarefaction curves
    print(f"\nGenerating alpha rarefaction curves...")
    rarefaction_viz = diversity.visualizers.alpha_rarefaction(
        table=table,
        phylogeny=tree,
        max_depth=max_depth,
        metadata=metadata
    )
    
    # Save visualization
    output_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-alpha-rarefaction.qzv')
    rarefaction_viz.visualization.save(output_path)
    print(f"  ✓ Saved: {output_prefix}-alpha-rarefaction.qzv")
    
    print(f"\n✓ {approach_name} ALPHA RAREFACTION COMPLETE")
    
    return output_path


def main():
    """Main workflow for Task 7.2: Alpha Rarefaction Plotting."""
    
    print("\n" + "="*60)
    print("TASK 7.2: ALPHA RAREFACTION PLOTTING")
    print("="*60)
    print(f"\nAssess sampling depth adequacy through rarefaction curves")
    print(f"- Top plot: Alpha rarefaction curves (should plateau)")
    print(f"- Bottom plot: Sample retention at each depth")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    completed_analyses = []
    
    # Process ASV data
    if os.path.exists(ASV_TABLE) and os.path.exists(ASV_TREE):
        print("─"*60)
        print("Processing ASV data...")
        print("─"*60)
        
        asv_output = run_alpha_rarefaction(
            table_path=ASV_TABLE,
            tree_path=ASV_TREE,
            output_prefix='asv',
            approach_name='ASV (DADA2)',
            max_depth=4000
        )
        completed_analyses.append(('ASV', asv_output))
    else:
        print(f"\n⚠️  ASV data not found, skipping...")
    
    # Process OTU data
    if os.path.exists(OTU_TABLE) and os.path.exists(OTU_TREE):
        print("\n" + "─"*60)
        print("Processing OTU data...")
        print("─"*60)
        
        otu_output = run_alpha_rarefaction(
            table_path=OTU_TABLE,
            tree_path=OTU_TREE,
            output_prefix='otu',
            approach_name='OTU (vsearch)',
            max_depth=4000
        )
        completed_analyses.append(('OTU', otu_output))
    else:
        print(f"\n⚠️  OTU data not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 7.2 COMPLETE: Alpha Rarefaction Plotting")
    print("="*60)
    
    if completed_analyses:
        print(f"\nCompleted analyses:")
        for approach, output_path in completed_analyses:
            print(f"  {approach}: {os.path.basename(output_path)}")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    if not os.path.exists(ASV_TABLE) and not os.path.exists(OTU_TABLE):
        raise FileNotFoundError(
            "No filtered tables found. Run Task 7.0 (filter-for-div) first."
        )
    
    main()