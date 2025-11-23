#!/usr/bin/env python3
"""
Script 04: DADA2 Denoising
Denoises sequences using DADA2.

Task 4.1: DADA2
- Quality filtering and trimming
- Error rate learning
- Paired-end read merging
- Chimera removal
"""

import os
from qiime2 import Artifact
from qiime2.plugins import dada2

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '02_import')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04_1_dada2')
SEQUENCES_ARTIFACT = os.path.join(INPUT_DIR, 'paired-end-sequences.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# DADA2 parameters
TRUNC_LEN_F = 270
TRUNC_LEN_R = 240
TRIM_LEFT_F = 0
TRIM_LEFT_R = 0

def denoise_with_dada2(sequences_path):
    """Denoise sequences using DADA2."""
    
    print("="*60)
    print("TASK 4.1: DADA2 DENOISING")
    print("="*60)
    
    print(f"\nLoading: {sequences_path}")
    sequences = Artifact.load(sequences_path)
    
    print(f"\nParameters:")
    print(f"  --p-trunc-len-f {TRUNC_LEN_F}")
    print(f"  --p-trunc-len-r {TRUNC_LEN_R}")
    print(f"  --p-trim-left-f {TRIM_LEFT_F}")
    print(f"  --p-trim-left-r {TRIM_LEFT_R}")
    print(f"\nRunning DADA2...\n")
    
    # Run DADA2
    dada2_results = dada2.methods.denoise_paired(
        demultiplexed_seqs=sequences,
        trunc_len_f=TRUNC_LEN_F,
        trunc_len_r=TRUNC_LEN_R,
        trim_left_f=TRIM_LEFT_F,
        trim_left_r=TRIM_LEFT_R,
    )
    
    # Save outputs
    table_path = os.path.join(OUTPUT_DIR, 'table.qza')
    rep_seqs_path = os.path.join(OUTPUT_DIR, 'rep-seqs.qza')
    stats_path = os.path.join(OUTPUT_DIR, 'denoising-stats.qza')
    
    dada2_results.table.save(table_path)
    dada2_results.representative_sequences.save(rep_seqs_path)
    dada2_results.denoising_stats.save(stats_path)
    
    print(f"\n" + "="*60)
    print("✓ DADA2 COMPLETE")
    print("="*60)
    print(f"\nOutputs:")
    print(f"  {table_path}")
    print(f"  {rep_seqs_path}")
    print(f"  {stats_path}")

if __name__ == "__main__":
    if not os.path.exists(SEQUENCES_ARTIFACT):
        raise FileNotFoundError(f"Run Task 2 first: {SEQUENCES_ARTIFACT}")
    
    denoise_with_dada2(SEQUENCES_ARTIFACT)