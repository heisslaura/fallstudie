#!/usr/bin/env python3
"""
Script 03: Sequence Quality Assessment
Creates quality visualization of imported sequences.

Task 3: Demultiplexing sequences (skipped - already demultiplexed)
- Sequences are already demultiplexed by sequencing facility
- Generate quality summary using qiime demux summarize
- Assess sequence quality and read counts per sample
- Use visualization to determine denoising parameters for Task 4
"""

import os
from qiime2 import Artifact
from qiime2.plugins import demux

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '02_import')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '03_quality')
SEQUENCES_ARTIFACT = os.path.join(INPUT_DIR, 'paired-end-sequences.qza')

# Create directories
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_quality_visualization(sequences_path):
    """
    Create quality visualization of demultiplexed sequences.
    
    This visualization shows:
    - Number of sequences per sample
    - Interactive quality score plots for forward and reverse reads
    - Quality distribution across read positions
    
    Use this to determine trim/truncation parameters for denoising.
    """
    
    print("\n" + "="*60)
    print("Creating sequence quality visualization...")
    print("="*60)
    
    print(f"Loading sequences from: {sequences_path}")
    
    # Load the paired-end sequences artifact
    sequences = Artifact.load(sequences_path)
    
    print(f"Artifact type: {sequences.type}")
    print(f"Generating quality plots (sampling 10,000 sequences)...")
    
    # Create visualization using demux summarize
    # This samples n sequences randomly for quality score plots
    viz_result = demux.visualizers.summarize(
        data=sequences,
        n=10000  # Number of sequences to sample for quality plots
    )
    
    # Save visualization
    viz_path = os.path.join(OUTPUT_DIR, 'demux-summary.qzv')
    viz_result.visualization.save(viz_path)
    
    print(f"\n✓ Quality visualization created: {viz_path}")
    
    return viz_path

def main():
    """Main workflow for Task 3: Quality Assessment."""
    
    print("="*60)
    print("TASK 3: SEQUENCE QUALITY ASSESSMENT")
    print("="*60)
    print(f"\nNote: Sequences are already demultiplexed")
    print(f"      Skipping demultiplexing step")
    print(f"\nInput: {SEQUENCES_ARTIFACT}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    # Check if input artifact exists
    if not os.path.exists(SEQUENCES_ARTIFACT):
        raise FileNotFoundError(
            f"Sequences artifact not found: {SEQUENCES_ARTIFACT}\n"
            f"Please run Task 2 (02_obtaining-and-importing-data.py) first."
        )
    
    # Create quality visualization
    viz_path = create_quality_visualization(SEQUENCES_ARTIFACT)
    
    # Summary
    print("\n" + "="*60)
    print("✓ TASK 3 COMPLETE: Sequence Quality Assessment")
    print("="*60)
    print(f"\nGenerated visualization:")
    print(f"  {viz_path}")
    print("="*60)

if __name__ == "__main__":
    main()