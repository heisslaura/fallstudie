#!/usr/bin/env python3
"""
Script 07.1: Generate Phylogenetic Trees
Builds phylogenetic trees using MAFFT alignment and FastTree for phylogenetic diversity analyses.

Task 7.1: Generate a tree for phylogenetic diversity analyses
- Multiple sequence alignment with MAFFT
- Masking of highly variable positions
- Phylogenetic tree construction with FastTree
- Midpoint rooting
- Processes both ASV and OTU sequences for comparison
"""

import os
from qiime2 import Artifact
from qiime2.plugins import phylogeny

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07_phylo-trees')

# Input files (biological samples only)
ASV_SEQS = os.path.join(INPUT_DIR, 'asv-rep-seqs-bio.qza')
OTU_SEQS = os.path.join(INPUT_DIR, 'otu-rep-seqs-bio.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Thread parameter
N_THREADS = 'auto'


def build_phylogeny(sequences_path, output_prefix, approach_name):
    """Build phylogenetic tree using MAFFT-FastTree pipeline."""
    
    print("="*60)
    print(f"BUILDING PHYLOGENETIC TREE: {approach_name}")
    print("="*60)
    
    print(f"\nLoading sequences:")
    print(f"  {sequences_path}")
    
    sequences = Artifact.load(sequences_path)
    
    print(f"\nRunning align-to-tree-mafft-fasttree pipeline...")
    print(f"  Parameters: n_threads='{N_THREADS}'")
    print(f"\nThis will:")
    print(f"  1. Align sequences with MAFFT")
    print(f"  2. Mask highly variable positions")
    print(f"  3. Build tree with FastTree")
    print(f"  4. Root tree at midpoint")
    
    # Run pipeline
    tree_results = phylogeny.pipelines.align_to_tree_mafft_fasttree(
        sequences=sequences,
        n_threads=N_THREADS
    )
    
    # Save all outputs
    print(f"\nSaving outputs...")
    
    alignment_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-alignment.qza')
    tree_results.alignment.save(alignment_path)
    print(f"  ✓ Alignment: {alignment_path}")
    
    masked_alignment_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-masked-alignment.qza')
    tree_results.masked_alignment.save(masked_alignment_path)
    print(f"  ✓ Masked alignment: {masked_alignment_path}")
    
    tree_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-tree.qza')
    tree_results.tree.save(tree_path)
    print(f"  ✓ Unrooted tree: {tree_path}")
    
    rooted_tree_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-rooted-tree.qza')
    tree_results.rooted_tree.save(rooted_tree_path)
    print(f"  ✓ Rooted tree: {rooted_tree_path}")
    
    print(f"\n✓ {approach_name} PHYLOGENY COMPLETE")
    
    return alignment_path, masked_alignment_path, tree_path, rooted_tree_path


def main():
    """Main workflow for Task 7.1: Phylogenetic Tree Generation."""
    
    print("\n" + "="*60)
    print("TASK 7.1: PHYLOGENETIC TREE GENERATION")
    print("="*60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    all_outputs = []
    
    # Build ASV tree
    if os.path.exists(ASV_SEQS):
        print("\n" + "─"*60)
        print("Processing ASV sequences...")
        print("─"*60)
        
        asv_outputs = build_phylogeny(
            ASV_SEQS,
            'asv',
            'ASV (DADA2)'
        )
        all_outputs.extend(asv_outputs)
    else:
        print(f"\n⚠️  ASV sequences not found, skipping...")
    
    # Build OTU tree
    if os.path.exists(OTU_SEQS):
        print("\n" + "─"*60)
        print("Processing OTU sequences...")
        print("─"*60)
        
        otu_outputs = build_phylogeny(
            OTU_SEQS,
            'otu',
            'OTU (vsearch)'
        )
        all_outputs.extend(otu_outputs)
    else:
        print(f"\n⚠️  OTU sequences not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 7.1 COMPLETE: Phylogenetic Trees")
    print("="*60)
    print(f"\nGenerated files ({len(all_outputs)}):")
    for output in all_outputs:
        print(f"  - {os.path.basename(output)}")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(ASV_SEQS) and not os.path.exists(OTU_SEQS):
        raise FileNotFoundError(
            "No biological-only sequences found. Run Task 7.0 (filter-for-div) first."
        )
    
    main()