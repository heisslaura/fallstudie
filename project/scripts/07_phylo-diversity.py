#!/usr/bin/env python3
"""
Script 07: Phylogenetic Tree Generation
Generates phylogenetic tree for diversity analyses using MAFFT and FastTree.

Task 7: Generate phylogenetic tree
- Multiple sequence alignment with MAFFT
- Masking highly variable positions
- Tree building with FastTree
- Midpoint rooting
"""

import os
from qiime2 import Artifact
from qiime2.plugins import phylogeny

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input from DADA2
DADA2_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.1_dada2')
DADA2_REP_SEQS = os.path.join(DADA2_INPUT_DIR, 'rep-seqs.qza')

# Input for vsearch (OTUs) - NO LONGER OPTIONAL
VSEARCH_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.2_vsearch')
VSEARCH_REP_SEQS = os.path.join(VSEARCH_INPUT_DIR, 'rep-seqs-clustered-97.qza') 

# Output directory
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '07_phylogeny')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_phylogenetic_tree(rep_seqs_path, output_dir, prefix='dada2'):
    """
    Generate phylogenetic tree using MAFFT-FastTree pipeline.
    
    Pipeline steps:
    1. Multiple sequence alignment (MAFFT)
    2. Mask highly variable positions
    3. Build tree (FastTree)
    4. Root tree at midpoint
    """
    
    print("="*70)
    print(f"PHYLOGENETIC TREE GENERATION: {prefix.upper()}")
    print("="*70)
    
    print(f"\nLoading representative sequences:")
    print(f"  {rep_seqs_path}")
    
    # This will raise an error if the file doesn't exist, which is now intended 
    # for both DADA2 and VSEARCH sequences.
    rep_seqs = Artifact.load(rep_seqs_path) 
    
    print(f"\nRunning align-to-tree-mafft-fasttree pipeline...")
    print("  Step 1: Multiple sequence alignment (MAFFT)")
    print("  Step 2: Masking highly variable positions")
    print("  Step 3: Tree construction (FastTree)")
    print("  Step 4: Midpoint rooting")
    print("\nThis may take several minutes...\n")
    
    # Run the phylogeny pipeline
    phylogeny_results = phylogeny.pipelines.align_to_tree_mafft_fasttree(
        sequences=rep_seqs
    )
    
    # Save outputs
    alignment_path = os.path.join(output_dir, f'{prefix}-aligned-rep-seqs.qza')
    masked_alignment_path = os.path.join(output_dir, f'{prefix}-masked-aligned-rep-seqs.qza')
    unrooted_tree_path = os.path.join(output_dir, f'{prefix}-unrooted-tree.qza')
    rooted_tree_path = os.path.join(output_dir, f'{prefix}-rooted-tree.qza')
    
    phylogeny_results.alignment.save(alignment_path)
    phylogeny_results.masked_alignment.save(masked_alignment_path)
    phylogeny_results.tree.save(unrooted_tree_path)
    phylogeny_results.rooted_tree.save(rooted_tree_path)
    
    print(f"✓ Alignment: {alignment_path}")
    print(f"✓ Masked alignment: {masked_alignment_path}")
    print(f"✓ Unrooted tree: {unrooted_tree_path}")
    print(f"✓ Rooted tree: {rooted_tree_path}")
    
    print(f"\n✓ {prefix.upper()} PHYLOGENETIC TREE COMPLETE")
    
    return rooted_tree_path


def main():
    """Main workflow for Task 7: Phylogenetic Tree Generation."""
    
    print("\n" + "="*70)
    print("TASK 7: PHYLOGENETIC TREE GENERATION")
    print("="*70)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("="*70 + "\n")
    
    all_outputs = []
    
    # Process DADA2 sequences (ASVs)
    if os.path.exists(DADA2_REP_SEQS):
        print("─"*70)
        print("Processing DADA2 representative sequences (ASVs)...")
        print("─"*70)
        
        rooted_tree = generate_phylogenetic_tree(
            DADA2_REP_SEQS,
            OUTPUT_DIR,
            'dada2'
        )
        all_outputs.append(rooted_tree)
    else:
        # This error is now handled in the __main__ block
        pass
    
    # Mandatory: Process vsearch sequences (OTUs)
    # The 'if os.path.exists(...)' block has been removed to make this mandatory.
    print("\n" + "─"*70)
    print("Processing vsearch representative sequences (OTUs)...")
    print("─"*70)
    
    # Generate tree for vsearch OTUs
    rooted_tree = generate_phylogenetic_tree(
        VSEARCH_REP_SEQS,
        OUTPUT_DIR,
        'vsearch'
    )
    all_outputs.append(rooted_tree)
    
    
    # Final summary
    print("\n" + "="*70)
    print("✓ TASK 7: Phylogenetic tree generation complete")
    print("="*70)
    print(f"\nGenerated rooted trees ({len(all_outputs)}):")
    for output in all_outputs:
        print(f"  - {os.path.basename(output)}")
    print("="*70)


if __name__ == "__main__":
    
    # Check for DADA2 sequences 
    if not os.path.exists(DADA2_REP_SEQS):
        raise FileNotFoundError(
            f"Representative sequences not found: {DADA2_REP_SEQS}\n"
            f"Run Task 4.1 (DADA2) first"
        )
    
    # Check for VSEARCH sequences
    if not os.path.exists(VSEARCH_REP_SEQS):
        raise FileNotFoundError(
            f"Representative sequences not found: {VSEARCH_REP_SEQS}\n"
            f"Run Task 4.2 (vsearch) first"
        )
    
    main()