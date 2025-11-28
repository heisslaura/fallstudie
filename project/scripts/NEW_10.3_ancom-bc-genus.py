#!/usr/bin/env python3
"""
Script 12: ANCOM-BC Differential Abundance Analysis at Genus Level
Collapse feature tables to genus level and run ANCOM-BC.
"""
import os
import pandas as pd
from qiime2 import Artifact, Metadata
import qiime2.plugins.taxa.actions as taxa_actions
import qiime2.plugins.composition.actions as composition_actions

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'sample-metadata.tsv')
ASV_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '10_ancombc_asv')
OTU_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '10_ancombc_otu')
ASV_TAXONOMY = os.path.join(BASE_DIR, 'outputs', '09_taxonomy', 'asv-taxonomy.qza')
OTU_TAXONOMY = os.path.join(BASE_DIR, 'outputs', '09_taxonomy', 'otu-taxonomy.qza')

# Load taxonomy
asv_taxonomy = Artifact.load(ASV_TAXONOMY)
otu_taxonomy = Artifact.load(OTU_TAXONOMY)

# Load metadata and rename columns
sample_metadata_original = Metadata.load(METADATA_FILE)
sample_metadata_df = sample_metadata_original.to_dataframe()
sample_metadata_df.columns = sample_metadata_df.columns.str.replace('-', '_')

print("\n" + "="*60)
print("Collapsing ASV Gum table to genus level")
print("="*60)

asv_gum_table = Artifact.load(os.path.join(ASV_OUTPUT_DIR, 'asv_gum_table.qza'))
gum_sample_ids = asv_gum_table.view(pd.DataFrame).index.tolist()
gum_metadata_df = sample_metadata_df.loc[sample_metadata_df.index.isin(gum_sample_ids)]
gum_metadata_md = Metadata(gum_metadata_df)

asv_gum_table_l6, = taxa_actions.collapse(
    table=asv_gum_table,
    taxonomy=asv_taxonomy,
    level=6,
)
asv_gum_table_l6.save(os.path.join(ASV_OUTPUT_DIR, 'asv_gum_table_l6.qza'))
print(f"Saved: {ASV_OUTPUT_DIR}/asv_gum_table_l6.qza")

l6_ancombc_asv_gum, = composition_actions.ancombc(
    table=asv_gum_table_l6,
    metadata=gum_metadata_md,
    formula='disease_state',
)
l6_ancombc_asv_gum.save(os.path.join(ASV_OUTPUT_DIR, 'l6_ancombc_asv_gum.qza'))
print(f"Saved: {ASV_OUTPUT_DIR}/l6_ancombc_asv_gum.qza")

l6_da_barplot_asv_gum_viz, = composition_actions.da_barplot(
    data=l6_ancombc_asv_gum,
    significance_threshold=0.001,
)
l6_da_barplot_asv_gum_viz.save(os.path.join(ASV_OUTPUT_DIR, 'l6_da_barplot_asv_gum.qzv'))
print(f"Saved: {ASV_OUTPUT_DIR}/l6_da_barplot_asv_gum.qzv")

print("\n" + "="*60)
print("Collapsing ASV Plaque table to genus level")
print("="*60)

asv_plaque_table = Artifact.load(os.path.join(ASV_OUTPUT_DIR, 'asv_plaque_table.qza'))
plaque_sample_ids = asv_plaque_table.view(pd.DataFrame).index.tolist()
plaque_metadata_df = sample_metadata_df.loc[sample_metadata_df.index.isin(plaque_sample_ids)]
plaque_metadata_md = Metadata(plaque_metadata_df)

asv_plaque_table_l6, = taxa_actions.collapse(
    table=asv_plaque_table,
    taxonomy=asv_taxonomy,
    level=6,
)
asv_plaque_table_l6.save(os.path.join(ASV_OUTPUT_DIR, 'asv_plaque_table_l6.qza'))
print(f"Saved: {ASV_OUTPUT_DIR}/asv_plaque_table_l6.qza")

l6_ancombc_asv_plaque, = composition_actions.ancombc(
    table=asv_plaque_table_l6,
    metadata=plaque_metadata_md,
    formula='disease_state',
)
l6_ancombc_asv_plaque.save(os.path.join(ASV_OUTPUT_DIR, 'l6_ancombc_asv_plaque.qza'))
print(f"Saved: {ASV_OUTPUT_DIR}/l6_ancombc_asv_plaque.qza")

l6_da_barplot_asv_plaque_viz, = composition_actions.da_barplot(
    data=l6_ancombc_asv_plaque,
    significance_threshold=0.001,
)
l6_da_barplot_asv_plaque_viz.save(os.path.join(ASV_OUTPUT_DIR, 'l6_da_barplot_asv_plaque.qzv'))
print(f"Saved: {ASV_OUTPUT_DIR}/l6_da_barplot_asv_plaque.qzv")

print("\n" + "="*60)
print("Collapsing OTU Gum table to genus level")
print("="*60)

otu_gum_table = Artifact.load(os.path.join(OTU_OUTPUT_DIR, 'otu_gum_table.qza'))

otu_gum_table_l6, = taxa_actions.collapse(
    table=otu_gum_table,
    taxonomy=otu_taxonomy,
    level=6,
)
otu_gum_table_l6.save(os.path.join(OTU_OUTPUT_DIR, 'otu_gum_table_l6.qza'))
print(f"Saved: {OTU_OUTPUT_DIR}/otu_gum_table_l6.qza")

l6_ancombc_otu_gum, = composition_actions.ancombc(
    table=otu_gum_table_l6,
    metadata=gum_metadata_md,
    formula='disease_state',
)
l6_ancombc_otu_gum.save(os.path.join(OTU_OUTPUT_DIR, 'l6_ancombc_otu_gum.qza'))
print(f"Saved: {OTU_OUTPUT_DIR}/l6_ancombc_otu_gum.qza")

l6_da_barplot_otu_gum_viz, = composition_actions.da_barplot(
    data=l6_ancombc_otu_gum,
    significance_threshold=0.001,
)
l6_da_barplot_otu_gum_viz.save(os.path.join(OTU_OUTPUT_DIR, 'l6_da_barplot_otu_gum.qzv'))
print(f"Saved: {OTU_OUTPUT_DIR}/l6_da_barplot_otu_gum.qzv")

print("\n" + "="*60)
print("Collapsing OTU Plaque table to genus level")
print("="*60)

otu_plaque_table = Artifact.load(os.path.join(OTU_OUTPUT_DIR, 'otu_plaque_table.qza'))

otu_plaque_table_l6, = taxa_actions.collapse(
    table=otu_plaque_table,
    taxonomy=otu_taxonomy,
    level=6,
)
otu_plaque_table_l6.save(os.path.join(OTU_OUTPUT_DIR, 'otu_plaque_table_l6.qza'))
print(f"Saved: {OTU_OUTPUT_DIR}/otu_plaque_table_l6.qza")

l6_ancombc_otu_plaque, = composition_actions.ancombc(
    table=otu_plaque_table_l6,
    metadata=plaque_metadata_md,
    formula='disease_state',
)
l6_ancombc_otu_plaque.save(os.path.join(OTU_OUTPUT_DIR, 'l6_ancombc_otu_plaque.qza'))
print(f"Saved: {OTU_OUTPUT_DIR}/l6_ancombc_otu_plaque.qza")

l6_da_barplot_otu_plaque_viz, = composition_actions.da_barplot(
    data=l6_ancombc_otu_plaque,
    significance_threshold=0.001,
)
l6_da_barplot_otu_plaque_viz.save(os.path.join(OTU_OUTPUT_DIR, 'l6_da_barplot_otu_plaque.qzv'))
print(f"Saved: {OTU_OUTPUT_DIR}/l6_da_barplot_otu_plaque.qzv")

print("\n" + "="*60)
print("All genus-level ANCOM-BC analyses completed successfully!")
print("="*60)