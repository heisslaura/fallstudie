#!/usr/bin/env python3
"""
Script 10.1: ANCOM-BC Differential Abundance Analysis
Run ANCOM-BC to identify differentially abundant features across disease states.
"""

import os
import pandas as pd
from qiime2 import Artifact, Metadata
import qiime2.plugins.composition.actions as composition_actions

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')

ASV_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '10_ancombc_asv')
OTU_INPUT_DIR = os.path.join(BASE_DIR, 'outputs', '10_ancombc_otu')

# Load metadata and rename columns to replace hyphens with underscores
sample_metadata_original = Metadata.load(METADATA_FILE)
sample_metadata_df = sample_metadata_original.to_dataframe()
sample_metadata_df.columns = sample_metadata_df.columns.str.replace('-', '_')
sample_metadata_md = Metadata(sample_metadata_df)

print("="*60)
print("Running ANCOM-BC on disease_state for ASV data")
print("="*60)

# ASV - Gum samples
print("\nLoading ASV Gum table...")
asv_gum_table = Artifact.load(os.path.join(ASV_INPUT_DIR, 'asv_gum_table.qza'))

print("Running ANCOM-BC for disease_state (ASV Gum samples)...")
asv_ancombc_disease_gum, = composition_actions.ancombc(
    table=asv_gum_table,
    metadata=sample_metadata_md,
    formula='disease_state',
)
asv_ancombc_disease_gum.save(os.path.join(ASV_INPUT_DIR, 'asv_ancombc_disease_gum.qza'))

asv_da_barplot_disease_gum_viz, = composition_actions.da_barplot(
    data=asv_ancombc_disease_gum,
    significance_threshold=0.001,
)
asv_da_barplot_disease_gum_viz.save(os.path.join(ASV_INPUT_DIR, 'asv_da_barplot_disease_gum.qzv'))
print(f"Saved: {ASV_INPUT_DIR}/asv_ancombc_disease_gum.qza")
print(f"Saved: {ASV_INPUT_DIR}/asv_da_barplot_disease_gum.qzv")

# ASV - Plaque samples
print("\nLoading ASV Plaque table...")
asv_plaque_table = Artifact.load(os.path.join(ASV_INPUT_DIR, 'asv_plaque_table.qza'))

print("Running ANCOM-BC for disease_state (ASV Plaque samples)...")
asv_ancombc_disease_plaque, = composition_actions.ancombc(
    table=asv_plaque_table,
    metadata=sample_metadata_md,
    formula='disease_state',
)
asv_ancombc_disease_plaque.save(os.path.join(ASV_INPUT_DIR, 'asv_ancombc_disease_plaque.qza'))

asv_da_barplot_disease_plaque_viz, = composition_actions.da_barplot(
    data=asv_ancombc_disease_plaque,
    significance_threshold=0.001,
)
asv_da_barplot_disease_plaque_viz.save(os.path.join(ASV_INPUT_DIR, 'asv_da_barplot_disease_plaque.qzv'))
print(f"Saved: {ASV_INPUT_DIR}/asv_ancombc_disease_plaque.qza")
print(f"Saved: {ASV_INPUT_DIR}/asv_da_barplot_disease_plaque.qzv")

print("\n" + "="*60)
print("Running ANCOM-BC on disease_state for OTU data")
print("="*60)

# OTU - Gum samples
print("\nLoading OTU Gum table...")
otu_gum_table = Artifact.load(os.path.join(OTU_INPUT_DIR, 'otu_gum_table.qza'))

print("Running ANCOM-BC for disease_state (OTU Gum samples)...")
otu_ancombc_disease_gum, = composition_actions.ancombc(
    table=otu_gum_table,
    metadata=sample_metadata_md,
    formula='disease_state',
)
otu_ancombc_disease_gum.save(os.path.join(OTU_INPUT_DIR, 'otu_ancombc_disease_gum.qza'))

otu_da_barplot_disease_gum_viz, = composition_actions.da_barplot(
    data=otu_ancombc_disease_gum,
    significance_threshold=0.001,
)
otu_da_barplot_disease_gum_viz.save(os.path.join(OTU_INPUT_DIR, 'otu_da_barplot_disease_gum.qzv'))
print(f"Saved: {OTU_INPUT_DIR}/otu_ancombc_disease_gum.qza")
print(f"Saved: {OTU_INPUT_DIR}/otu_da_barplot_disease_gum.qzv")

# OTU - Plaque samples
print("\nLoading OTU Plaque table...")
otu_plaque_table = Artifact.load(os.path.join(OTU_INPUT_DIR, 'otu_plaque_table.qza'))

print("Running ANCOM-BC for disease_state (OTU Plaque samples)...")
otu_ancombc_disease_plaque, = composition_actions.ancombc(
    table=otu_plaque_table,
    metadata=sample_metadata_md,
    formula='disease_state',
)
otu_ancombc_disease_plaque.save(os.path.join(OTU_INPUT_DIR, 'otu_ancombc_disease_plaque.qza'))

otu_da_barplot_disease_plaque_viz, = composition_actions.da_barplot(
    data=otu_ancombc_disease_plaque,
    significance_threshold=0.001,
)
otu_da_barplot_disease_plaque_viz.save(os.path.join(OTU_INPUT_DIR, 'otu_da_barplot_disease_plaque.qzv'))
print(f"Saved: {OTU_INPUT_DIR}/otu_ancombc_disease_plaque.qza")
print(f"Saved: {OTU_INPUT_DIR}/otu_da_barplot_disease_plaque.qzv")

print("\n" + "="*60)
print("All ANCOM-BC analyses complete!")
print("="*60)