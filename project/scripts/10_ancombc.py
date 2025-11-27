#!/usr/bin/env python

"""
10_ancombc.py

Task 10: Differential abundance testing with ANCOM-BC (ASV + OTU)
=================================================================

This script runs ANCOM-BC on:

1. ASV-level tables
2. ASV collapsed at genus level (L6)
3. OTU-level tables
4. OTU collapsed at genus level (L6)

using the q2-composition (ANCOM-BC) and q2-taxa plugins.

Inputs (relative to project root):
- outputs/07.0_filter-for-div/asv-table-bio.qza
- outputs/07.0_filter-for-div/otu-table-bio.qza
- outputs/09_taxonomy/asv-taxonomy.qza
- outputs/09_taxonomy/otu-taxonomy.qza
- data/processed/sample-metadata.tsv

Outputs (relative to project root):
- outputs/10_ancombc/asv/ancombc-<formula>.qza
- outputs/10_ancombc/asv/da-barplot-<formula>.qzv
- outputs/10_ancombc/asv/table-l6.qza
- outputs/10_ancombc/asv/l6-ancombc-<formula>.qza
- outputs/10_ancombc/asv/l6-da-barplot-<formula>.qzv

- outputs/10_ancombc/otu/ancombc-<formula>.qza
- outputs/10_ancombc/otu/da-barplot-<formula>.qzv
- outputs/10_ancombc/otu/table-l6.qza
- outputs/10_ancombc/otu/l6-ancombc-<formula>.qza
- outputs/10_ancombc/otu/l6-da-barplot-<formula>.qzv
"""

from pathlib import Path

import pandas as pd
from qiime2 import Artifact, Metadata
from qiime2.plugins import composition, taxa


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Tables (already filtered to biological samples in step 07.0)
ASV_TABLE = PROJECT_ROOT / "outputs/07.0_filter-for-div/asv-table-bio.qza"
OTU_TABLE = PROJECT_ROOT / "outputs/07.0_filter-for-div/otu-table-bio.qza"

# Taxonomy from step 09 (Greengenes2 classification)
ASV_TAXONOMY = PROJECT_ROOT / "outputs/09_taxonomy/asv-taxonomy.qza"
OTU_TAXONOMY = PROJECT_ROOT / "outputs/09_taxonomy/otu-taxonomy.qza"

# Metadata
METADATA_TSV = PROJECT_ROOT / "data/processed/sample-metadata.tsv"

# Differential abundance outputs
OUTPUT_DIR = PROJECT_ROOT / "outputs/10_ancombc"
ASV_DIR = OUTPUT_DIR / "asv"
OTU_DIR = OUTPUT_DIR / "otu"

# Metadata column used in ANCOM-BC formula (EDIT HERE if needed)
# Available columns (from your metadata): 
# 'seq-pos', 'subject', 'sample-type', 'tooth-number', 'tooth-location',
# 'replicate', 'gender', 'age', 'disease-state', 'din'
FORMULA = "subject"
ALPHA = 0.001              # significance threshold for da-barplot
GENUS_LEVEL = 6            # Greengenes / GG2 genus level


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def check_inputs():
    required = [
        ASV_TABLE,
        OTU_TABLE,
        ASV_TAXONOMY,
        OTU_TAXONOMY,
        METADATA_TSV,
    ]
    missing = [p for p in required if not p.exists()]

    if missing:
        print("ERROR: The following required input files are missing:")
        for p in missing:
            print(f"  - {p}")
        raise SystemExit(1)


def validate_formula_column(meta: Metadata, formula: str):
    cols = set(meta.to_dataframe().columns)
    if formula not in cols:
        print(f"ERROR: Formula column '{formula}' not found in metadata.")
        print("Available columns:")
        for c in sorted(cols):
            print(f"  - {c}")
        raise SystemExit(1)


def filter_metadata_to_table(meta: Metadata, table: Artifact) -> Metadata:
    """
    Restrict metadata to sample IDs that are present in the feature table.
    Automatically detects whether sample IDs are in the table's index or columns.
    """
    df = table.view(pd.DataFrame)        # orientation can vary
    meta_df = meta.to_dataframe()

    table_idx = set(df.index)
    table_cols = set(df.columns)
    meta_ids = set(meta_df.index)

    overlap_cols = meta_ids & table_cols
    overlap_idx = meta_ids & table_idx

    if overlap_cols:
        sample_ids = sorted(overlap_cols)
        loc_axis = "columns"
    elif overlap_idx:
        sample_ids = sorted(overlap_idx)
        loc_axis = "index"
    else:
        print("ERROR: No overlapping sample IDs between table and metadata.")
        print("Example metadata IDs:", sorted(list(meta_ids))[:10])
        print("Example table index IDs:", sorted(list(table_idx))[:10])
        print("Example table column IDs:", sorted(list(table_cols))[:10])
        raise SystemExit(1)

    dropped_meta = meta_ids - set(sample_ids)
    if dropped_meta:
        print(f"Note: using table {loc_axis} as sample IDs.")
        print("The following metadata samples are not in the table and "
              "will be dropped before ANCOM-BC:")
        for s in sorted(dropped_meta):
            print(f"  - {s}")
        print()

    filtered_meta_df = meta_df.loc[sample_ids]
    return Metadata(filtered_meta_df)


def run_ancombc_for_table(label: str,
                          table_path: Path,
                          taxonomy_path: Path,
                          out_dir: Path):
    """
    Run ANCOM-BC on:
      - original feature table
      - table collapsed at genus level (L6)
    """
    print("------------------------------------------------------------------")
    print(f"Running ANCOM-BC for {label}")
    print(f"Table:    {table_path}")
    print(f"Taxonomy: {taxonomy_path}")
    print(f"Formula:  {FORMULA}")
    print("------------------------------------------------------------------")

    out_dir.mkdir(parents=True, exist_ok=True)

    table = Artifact.load(str(table_path))
    taxonomy = Artifact.load(str(taxonomy_path))
    meta = Metadata.load(str(METADATA_TSV))

    # Validate column exists
    validate_formula_column(meta, FORMULA)

    # Filter metadata down to samples present in the table (robust to orientation)
    meta_filtered = filter_metadata_to_table(meta, table)

    # --------------------------
    # 1) Feature-level ANCOM-BC
    # --------------------------
    print(f"[{label}] Running ANCOM-BC at feature (ASV/OTU) level...")

    ancom_res = composition.methods.ancombc(
        table=table,
        metadata=meta_filtered,
        formula=FORMULA
    )
    diff = ancom_res.differentials
    diff_path = out_dir / f"ancombc-{FORMULA}.qza"
    diff.save(str(diff_path))

    print(f"[{label}] Creating DA barplot (feature-level)...")
    da_viz = composition.visualizers.da_barplot(
        data=diff,
        significance_threshold=ALPHA
    )
    da_viz_path = out_dir / f"da-barplot-{FORMULA}.qzv"
    da_viz.visualization.save(str(da_viz_path))

    print(f"[{label}] Feature-level outputs:")
    print(f"  Differentials : {diff_path}")
    print(f"  DA barplot    : {da_viz_path}")
    print()

    # -------------------------------------------
    # 2) Collapse to genus level (L6) and rerun
    # -------------------------------------------
    print(f"[{label}] Collapsing table at genus level (L{GENUS_LEVEL})...")

    collapsed_res = taxa.methods.collapse(
        table=table,
        taxonomy=taxonomy,
        level=GENUS_LEVEL
    )
    collapsed_table = collapsed_res.collapsed_table
    collapsed_table_path = out_dir / f"table-l{GENUS_LEVEL}.qza"
    collapsed_table.save(str(collapsed_table_path))

    print(f"[{label}] Running ANCOM-BC at genus level (L{GENUS_LEVEL})...")

    ancom_l_res = composition.methods.ancombc(
        table=collapsed_table,
        metadata=meta_filtered,
        formula=FORMULA
    )
    diff_l = ancom_l_res.differentials
    diff_l_path = out_dir / f"l{GENUS_LEVEL}-ancombc-{FORMULA}.qza"
    diff_l.save(str(diff_l_path))

    print(f"[{label}] Creating DA barplot (genus-level)...")
    da_l_viz = composition.visualizers.da_barplot(
        data=diff_l,
        significance_threshold=ALPHA
    )
    da_l_viz_path = out_dir / f"l{GENUS_LEVEL}-da-barplot-{FORMULA}.qzv"
    da_l_viz.visualization.save(str(da_l_viz_path))

    print(f"[{label}] Genus-level outputs:")
    print(f"  Collapsed table : {collapsed_table_path}")
    print(f"  Differentials   : {diff_l_path}")
    print(f"  DA barplot      : {da_l_viz_path}")
    print()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("======================================================================")
    print("TASK 10: DIFFERENTIAL ABUNDANCE TESTING WITH ANCOM-BC (ASV + OTU)")
    print("======================================================================\n")

    check_inputs()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Using metadata file: {METADATA_TSV}")
    print(f"Using formula (ANCOM-BC): {FORMULA}")
    print(f"Significance threshold (da-barplot): {ALPHA}\n")

    # ASV-level + genus-level
    run_ancombc_for_table(
        label="ASV (DADA2)",
        table_path=ASV_TABLE,
        taxonomy_path=ASV_TAXONOMY,
        out_dir=ASV_DIR
    )

    # OTU-level + genus-level
    run_ancombc_for_table(
        label="OTU (vsearch 97%)",
        table_path=OTU_TABLE,
        taxonomy_path=OTU_TAXONOMY,
        out_dir=OTU_DIR
    )

    print("======================================================================")
    print("ANCOM-BC differential abundance testing completed.")
    print("You can view the .qzv files at https://view.qiime2.org")
    print("======================================================================")


if __name__ == "__main__":
    main()