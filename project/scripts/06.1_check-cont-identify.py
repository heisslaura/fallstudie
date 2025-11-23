#!/usr/bin/env python3
"""
Script 06: Contamination Identification
Identifies potential contaminant sequences using negative control samples.

Task 6: Checking for contamination
- Uses decontam prevalence method to identify contaminants
- Compares feature prevalence in negative controls vs. true samples
- Applies to both DADA2 (ASVs) and vsearch (OTUs) outputs
"""

import os
from qiime2 import Artifact, Metadata
from qiime2.plugins import quality_control

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

# Output directory for contamination analysis
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '06_check-cont')

# DADA2 inputs
DADA2_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.1_dada2')
DADA2_TABLE = os.path.join(DADA2_INPUT_DIR, 'table.qza')

# vsearch inputs
VSEARCH_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '04.2_vsearch')
VSEARCH_TABLE = os.path.join(VSEARCH_INPUT_DIR, 'table-clustered-97.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Decontam parameters
METHOD = 'prevalence'
PREV_CONTROL_COLUMN = 'sample-type'
PREV_CONTROL_INDICATOR = 'Negative-Control'


def identify_contaminants(table_path, output_dir, prefix, approach_name):
    """Identify contaminant features using decontam."""
    
    print("="*60)
    print(f"CONTAMINATION IDENTIFICATION: {approach_name}")
    print("="*60)
    
    print(f"\nLoading:")
    print(f"  Table: {table_path}")
    print(f"  Metadata: {METADATA_FILE}")
    
    # Load inputs
    table = Artifact.load(table_path)
    metadata = Metadata.load(METADATA_FILE)
    
    print(f"\nDecontam parameters:")
    print(f"  Method: {METHOD}")
    print(f"  Control column: {PREV_CONTROL_COLUMN}")
    print(f"  Control indicator: {PREV_CONTROL_INDICATOR}")
    
    # Identify contaminants
    print(f"\nRunning decontam-identify...")
    
    decontam_result = quality_control.methods.decontam_identify(
        table=table,
        metadata=metadata,
        method=METHOD,
        prev_control_column=PREV_CONTROL_COLUMN,
        prev_control_indicator=PREV_CONTROL_INDICATOR
    )
    
    # Save decontam scores
    scores_path = os.path.join(output_dir, f'{prefix}-decontam-scores.qza')
    decontam_result.decontam_scores.save(scores_path)
    print(f"✓ Saved: {scores_path}")
    
    print(f"\n✓ {approach_name} COMPLETE")
    
    return scores_path


def main():
    """Main workflow for Task 6: Contamination Identification."""
    
    print("\n" + "="*60)
    print("TASK 6: CHECKING FOR CONTAMINATION")
    print("="*60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    all_outputs = []
    
    # Process DADA2 features (ASVs)
    if os.path.exists(DADA2_TABLE):
        print("\n" + "─"*60)
        print("Processing DADA2 outputs (ASVs)...")
        print("─"*60)
        
        dada2_scores = identify_contaminants(
            DADA2_TABLE,
            OUTPUT_DIR,
            'dada2-asv',
            'DADA2 (ASVs)'
        )
        all_outputs.append(dada2_scores)
    else:
        print(f"\n⚠️  DADA2 table not found, skipping...")
    
    # Process vsearch features (OTUs)
    if os.path.exists(VSEARCH_TABLE):
        print("\n" + "─"*60)
        print("Processing vsearch outputs (OTUs)...")
        print("─"*60)
        
        vsearch_scores = identify_contaminants(
            VSEARCH_TABLE,
            OUTPUT_DIR,
            'vsearch-otu',
            'vsearch (OTUs)'
        )
        all_outputs.append(vsearch_scores)
    else:
        print(f"\n⚠️  vsearch table not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK6: Identification complete")
    print("="*60)
    print(f"\nGenerated files ({len(all_outputs)}):")
    for output in all_outputs:
        print(f"  - {os.path.basename(output)}")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    main()