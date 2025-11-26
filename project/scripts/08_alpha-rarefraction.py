#!/usr/bin/env python

"""
08_alpha-rarefaction.py

Task 8: Alpha rarefaction plotting for ASV (DADA2) and OTU (vsearch 97%)
=======================================================================

This script runs `qiime diversity alpha-rarefaction` for:

- ASV table + ASV rooted tree
- OTU table + OTU rooted tree

Inputs (relative to project root):
- project/outputs/07.0_filter-for-div/asv-table-bio.qza
- project/outputs/07.0_filter-for-div/otu-table-bio.qza
- project/outputs/07_phylo-trees/asv-rooted-tree.qza
- project/outputs/07_phylo-trees/otu-rooted-tree.qza
- project/data/processed/sample-metadata.tsv

Outputs:
- project/outputs/08_alpha-rarefaction/asv-alpha-rarefaction.qzv
- project/outputs/08_alpha-rarefaction/otu-alpha-rarefaction.qzv

Notes:
- `--p-max-depth` should be chosen based on the "frequency per sample"
  in your filtered tables (asv-table-bio.qza / otu-table-bio.qza).
- The constants ASV_MAX_DEPTH and OTU_MAX_DEPTH below can be adjusted
  as needed after inspecting those summaries.
"""

from pathlib import Path

from qiime2 import Artifact, Metadata
from qiime2.plugins import diversity


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

# Project root = one level above this script (project/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input paths
ASV_TABLE = PROJECT_ROOT / "outputs/07.0_filter-for-div/asv-table-bio.qza"
OTU_TABLE = PROJECT_ROOT / "outputs/07.0_filter-for-div/otu-table-bio.qza"
ASV_TREE = PROJECT_ROOT / "outputs/07_phylo-trees/asv-rooted-tree.qza"
OTU_TREE = PROJECT_ROOT / "outputs/07_phylo-trees/otu-rooted-tree.qza"
METADATA_TSV = PROJECT_ROOT / "data/processed/sample-metadata.tsv"

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "outputs/08_alpha-rarefaction"

ASV_OUTPUT_VIZ = OUTPUT_DIR / "asv-alpha-rarefaction.qzv"
OTU_OUTPUT_VIZ = OUTPUT_DIR / "otu-alpha-rarefaction.qzv"

# Alpha rarefaction parameters
# Adjust these values after checking the "frequency per sample" summaries.
# For example, you might choose values near the median sample frequency.
ASV_MAX_DEPTH = 2839  # example value (even sampling depth from step 7.1)
OTU_MAX_DEPTH = 2839  # can be set independently if desired

MIN_DEPTH = 1          # default in QIIME2
STEPS = 10             # number of evenly spaced depths between min and max
ITERATIONS = 10        # rarefactions per depth (as in README text)


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def check_inputs():
    """Ensure that all required input files exist."""
    missing = [
        p for p in [
            ASV_TABLE,
            OTU_TABLE,
            ASV_TREE,
            OTU_TREE,
            METADATA_TSV,
        ] if not p.exists()
    ]

    if missing:
        print("ERROR: The following required input files are missing:")
        for p in missing:
            print(f"  - {p}")
        raise SystemExit(1)


def run_alpha_rarefaction(table_path: Path,
                          tree_path: Path,
                          metadata_path: Path,
                          max_depth: int,
                          output_viz_path: Path,
                          label: str):
    """Run qiime diversity alpha-rarefaction for one table/tree pair."""
    print("------------------------------------------------------------------")
    print(f"Running alpha rarefaction for {label}")
    print(f"Table:    {table_path}")
    print(f"Tree:     {tree_path}")
    print(f"Metadata: {metadata_path}")
    print(f"Max depth: {max_depth}")
    print(f"Output:   {output_viz_path}")
    print("------------------------------------------------------------------")

    # Load inputs as QIIME2 artifacts / metadata
    table = Artifact.load(str(table_path))
    tree = Artifact.load(str(tree_path))
    metadata = Metadata.load(str(metadata_path))

    # Run alpha-rarefaction visualizer
    result = diversity.visualizers.alpha_rarefaction(
        table=table,
        phylogeny=tree,
        max_depth=max_depth,
        min_depth=MIN_DEPTH,
        steps=STEPS,
        iterations=ITERATIONS,
        metadata=metadata,
        # metrics=None  # use defaults; can be customized if needed
    )

    # Save visualization
    result.visualization.save(str(output_viz_path))

    print(f"Done: {label} alpha rarefaction written to {output_viz_path}")
    print()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("======================================================================")
    print("TASK 8: ALPHA RAREFACTION PLOTTING")
    print("======================================================================")

    check_inputs()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Input files found. Starting alpha rarefaction analyses...\n")

    # ASV-based alpha rarefaction
    run_alpha_rarefaction(
        table_path=ASV_TABLE,
        tree_path=ASV_TREE,
        metadata_path=METADATA_TSV,
        max_depth=ASV_MAX_DEPTH,
        output_viz_path=ASV_OUTPUT_VIZ,
        label="ASV (DADA2)"
    )

    # OTU-based alpha rarefaction
    run_alpha_rarefaction(
        table_path=OTU_TABLE,
        tree_path=OTU_TREE,
        metadata_path=METADATA_TSV,
        max_depth=OTU_MAX_DEPTH,
        output_viz_path=OTU_OUTPUT_VIZ,
        label="OTU (vsearch 97%)"
    )

    print("======================================================================")
    print("Alpha rarefaction completed.")
    print("You can view the .qzv files at https://view.qiime2.org")
    print("======================================================================")


if __name__ == "__main__":
    main()
