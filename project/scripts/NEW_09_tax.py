#!/usr/bin/env python3
"""
Script 09: Taxonomic Analysis
Assign taxonomy to ASV/OTU sequences using Greengenes2 classifier.

Task 9: Taxonomic classification
- Uses Greengenes2 2022.10 backbone Naive Bayes classifier
- Classifier trained on V4 region, compatible with sklearn 1.4.2
- Assigns taxonomy to representative sequences
- Generates taxonomy bar plots for visualization
- Processes both ASV and OTU datasets
"""

import os
import subprocess
from qiime2 import Artifact, Metadata
import qiime2.plugins.feature_classifier.actions as feature_classifier_actions
import qiime2.plugins.metadata.actions as metadata_actions
import qiime2.plugins.taxa.actions as taxa_actions

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '09_taxonomy')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')
CLASSIFIER_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'gg2-2022.10-backbone-v4-nb.qza')

# ASV inputs
ASV_SEQS = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'asv-rep-seqs-bio.qza')
ASV_TABLE = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'asv-table-bio.qza')

# OTU inputs
OTU_SEQS = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'otu-rep-seqs-bio.qza')
OTU_TABLE = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'otu-table-bio.qza')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Greengenes2 classifier URL
CLASSIFIER_URL = (
    "https://ftp.microbio.me/greengenes_release/2022.10/"
    "sklearn-1.4.2-compatible-nb-classifiers/"
    "2022.10.backbone.v4.nb.sklearn-1.4.2.qza"
)


def download_classifier():
    """Download Greengenes2 V4 Naive Bayes classifier if not present."""
    if os.path.exists(CLASSIFIER_PATH):
        print(f"✓ Classifier found: {os.path.basename(CLASSIFIER_PATH)}")
        return
    
    print(f"Downloading Greengenes2 V4 classifier...")
    print(f"URL: {CLASSIFIER_URL}")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(CLASSIFIER_PATH), exist_ok=True)
    
    # Download
    subprocess.run(
        ['wget', '-O', CLASSIFIER_PATH, CLASSIFIER_URL],
        check=True
    )
    
    print(f"✓ Downloaded: {os.path.basename(CLASSIFIER_PATH)}")


def classify_taxonomy(rep_seqs_path, table_path, output_prefix, approach_name):
    """
    Assign taxonomy using Greengenes2 Naive Bayes classifier.
    
    Parameters:
    -----------
    rep_seqs_path : str
        Path to representative sequences artifact
    table_path : str
        Path to feature table artifact
    output_prefix : str
        Prefix for output files (e.g., 'asv' or 'otu')
    approach_name : str
        Display name for the approach
    """
    print("="*60)
    print(f"TAXONOMIC CLASSIFICATION: {approach_name}")
    print("="*60)
    
    # Load inputs
    rep_seqs = Artifact.load(rep_seqs_path)
    table = Artifact.load(table_path)
    classifier = Artifact.load(CLASSIFIER_PATH)
    sample_metadata = Metadata.load(METADATA_FILE)
    
    print(f"\nRep seqs: {os.path.basename(rep_seqs_path)}")
    print(f"Table: {os.path.basename(table_path)}")
    print(f"Classifier: Greengenes2 2022.10 V4 (sklearn 1.4.2)")
    
    # Classify sequences
    print(f"\nClassifying sequences...")
    taxonomy, = feature_classifier_actions.classify_sklearn(
        classifier=classifier,
        reads=rep_seqs
    )
    
    # Save taxonomy
    taxonomy_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-taxonomy.qza')
    taxonomy.save(taxonomy_path)
    print(f"  ✓ Saved: {output_prefix}-taxonomy.qza")
    
    # Generate taxonomy visualization
    print(f"\nGenerating taxonomy visualization...")
    taxonomy_as_md = taxonomy.view(Metadata)
    taxonomy_viz, = metadata_actions.tabulate(
        input=taxonomy_as_md
    )
    
    taxonomy_viz_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-taxonomy.qzv')
    taxonomy_viz.save(taxonomy_viz_path)
    print(f"  ✓ Saved: {output_prefix}-taxonomy.qzv")
    
    # Generate taxonomy bar plots
    print(f"\nGenerating taxonomy bar plots...")
    barplot_viz, = taxa_actions.barplot(
        table=table,
        taxonomy=taxonomy,
        metadata=sample_metadata
    )
    
    barplot_path = os.path.join(OUTPUT_DIR, f'{output_prefix}-taxa-barplot.qzv')
    barplot_viz.save(barplot_path)
    print(f"  ✓ Saved: {output_prefix}-taxa-barplot.qzv")
    
    print(f"\n✓ {approach_name} TAXONOMIC CLASSIFICATION COMPLETE")
    
    return taxonomy_path, taxonomy_viz_path, barplot_path


def main():
    """Main workflow for Task 9: Taxonomic Analysis."""
    
    print("\n" + "="*60)
    print("TASK 9: TAXONOMIC ANALYSIS")
    print("="*60)
    print(f"\nClassifier: Greengenes2 2022.10 backbone V4 region")
    print(f"Method: Naive Bayes (sklearn 1.4.2 compatible)")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60 + "\n")
    
    # Download classifier if needed
    print("─"*60)
    print("Checking classifier...")
    print("─"*60)
    download_classifier()
    
    completed_analyses = []
    
    # Process ASV data
    if os.path.exists(ASV_SEQS) and os.path.exists(ASV_TABLE):
        print("\n" + "─"*60)
        print("Processing ASV data...")
        print("─"*60)
        
        asv_outputs = classify_taxonomy(
            rep_seqs_path=ASV_SEQS,
            table_path=ASV_TABLE,
            output_prefix='asv',
            approach_name='ASV (DADA2)'
        )
        completed_analyses.append(('ASV', asv_outputs))
    else:
        print(f"\n⚠️  ASV data not found, skipping...")
    
    # Process OTU data
    if os.path.exists(OTU_SEQS) and os.path.exists(OTU_TABLE):
        print("\n" + "─"*60)
        print("Processing OTU data...")
        print("─"*60)
        
        otu_outputs = classify_taxonomy(
            rep_seqs_path=OTU_SEQS,
            table_path=OTU_TABLE,
            output_prefix='otu',
            approach_name='OTU (vsearch)'
        )
        completed_analyses.append(('OTU', otu_outputs))
    else:
        print(f"\n⚠️  OTU data not found, skipping...")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ TASK 9 COMPLETE: Taxonomic Analysis")
    print("="*60)
    
    if completed_analyses:
        print(f"\nCompleted analyses:")
        for approach, (tax_path, tax_viz, barplot) in completed_analyses:
            print(f"\n{approach}:")
            print(f"  - {os.path.basename(tax_path)}")
            print(f"  - {os.path.basename(tax_viz)}")
            print(f"  - {os.path.basename(barplot)}")
    print("="*60)


if __name__ == "__main__":
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
    
    if not os.path.exists(ASV_SEQS) and not os.path.exists(OTU_SEQS):
        raise FileNotFoundError(
            "No representative sequences found. Run Task 7.0 (filter-for-div) first."
        )
    
    main()