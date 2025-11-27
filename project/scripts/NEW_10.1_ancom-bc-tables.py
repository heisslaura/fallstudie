#!/usr/bin/env python3
"""
Script 10: Differential Abundance Testing with ANCOM-BC
Filter feature tables by sample type for differential abundance analysis.
"""

import os
import pandas as pd
from qiime2 import Artifact, Metadata
import qiime2.plugins.feature_table.actions as feature_table_actions
import qiime2.plugins.composition.actions as composition_actions
import qiime2.plugins.taxa.actions as taxa_actions

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASV_TABLE = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'asv-table-bio.qza')
OTU_TABLE = os.path.join(BASE_DIR, 'outputs', '07.0_filter-for-div', 'otu-table-bio.qza')
ASV_TAXONOMY = os.path.join(BASE_DIR, 'outputs', '09_taxonomy', 'asv-taxonomy.qza')
OTU_TAXONOMY = os.path.join(BASE_DIR, 'outputs', '09_taxonomy', 'otu-taxonomy.qza')
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

ASV_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '10_ancombc_asv')
OTU_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '10_ancombc_otu')

os.makedirs(ASV_OUTPUT_DIR, exist_ok=True)
os.makedirs(OTU_OUTPUT_DIR, exist_ok=True)

# Load artifacts
print("Loading artifacts...")
asv_table = Artifact.load(ASV_TABLE)
otu_table = Artifact.load(OTU_TABLE)
asv_taxonomy = Artifact.load(ASV_TAXONOMY)
otu_taxonomy = Artifact.load(OTU_TAXONOMY)

# Load metadata and rename columns to replace hyphens with underscores
sample_metadata_original = Metadata.load(METADATA_FILE)
sample_metadata_df = sample_metadata_original.to_dataframe()
sample_metadata_df.columns = sample_metadata_df.columns.str.replace('-', '_')
sample_metadata_md = Metadata(sample_metadata_df)

print("\n" + "="*60)
print("Creating filtered feature tables by sample type")
print("="*60)

# ASV - Filter for Gum samples
print("\nFiltering ASV table for Gum samples...")
asv_gum_table, = feature_table_actions.filter_samples(
    table=asv_table,
    metadata=sample_metadata_md,
    where='[sample_type]="Gum"',
)
asv_gum_table.save(os.path.join(ASV_OUTPUT_DIR, 'asv_gum_table.qza'))
print(f"Saved: {ASV_OUTPUT_DIR}/asv_gum_table.qza")

# ASV - Filter for Plaque samples
print("\nFiltering ASV table for Plaque samples...")
asv_plaque_table, = feature_table_actions.filter_samples(
    table=asv_table,
    metadata=sample_metadata_md,
    where='[sample_type]="Plaque"',
)
asv_plaque_table.save(os.path.join(ASV_OUTPUT_DIR, 'asv_plaque_table.qza'))
print(f"Saved: {ASV_OUTPUT_DIR}/asv_plaque_table.qza")

# OTU - Filter for Gum samples
print("\nFiltering OTU table for Gum samples...")
otu_gum_table, = feature_table_actions.filter_samples(
    table=otu_table,
    metadata=sample_metadata_md,
    where='[sample_type]="Gum"',
)
otu_gum_table.save(os.path.join(OTU_OUTPUT_DIR, 'otu_gum_table.qza'))
print(f"Saved: {OTU_OUTPUT_DIR}/otu_gum_table.qza")

# OTU - Filter for Plaque samples
print("\nFiltering OTU table for Plaque samples...")
otu_plaque_table, = feature_table_actions.filter_samples(
    table=otu_table,
    metadata=sample_metadata_md,
    where='[sample_type]="Plaque"',
)
otu_plaque_table.save(os.path.join(OTU_OUTPUT_DIR, 'otu_plaque_table.qza'))
print(f"Saved: {OTU_OUTPUT_DIR}/otu_plaque_table.qza")

print("\n" + "="*60)
print("All filtered tables created successfully!")
print("="*60)