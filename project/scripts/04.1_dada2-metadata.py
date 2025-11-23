#!/usr/bin/env python3
"""
Script 04.1: Visualize DADA2 Results
Creates visualizations of denoising statistics.
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins.metadata import actions as metadata_actions

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04_denoising')
OUTPUT_DIR = INPUT_DIR
STATS_FILE = os.path.join(INPUT_DIR, 'denoising-stats.qza')

def visualize_stats():
    """Create visualization of DADA2 denoising statistics."""
    
    print("="*60)
    print("Visualizing DADA2 Denoising Stats")
    print("="*60)
    
    # Load the denoising-stats.qza artifact
    denoising_stats = Artifact.load(STATS_FILE)
    
    # Convert to metadata
    stats_md = denoising_stats.view(Metadata)
    
    # Create visualization
    stats_viz, = metadata_actions.tabulate(input=stats_md)
    
    # Save
    viz_path = os.path.join(OUTPUT_DIR, 'denoising-stats.qzv')
    stats_viz.save(viz_path)
    
    print(f"\n✓ Saved: {viz_path}")

if __name__ == "__main__":
    visualize_stats()