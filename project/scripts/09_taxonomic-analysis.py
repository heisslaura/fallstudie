#!/usr/bin/env python

"""
09_taxonomic-analysis.py

Task 9: Taxonomic analysis with Greengenes2 (ASV + OTU)
=======================================================

This script:

1. Assigns taxonomy to ASV and OTU representative sequences using the
   Greengenes2 2022.10 V4 Naive Bayes classifier:

   $ qiime feature-classifier classify-sklearn \
       --i-classifier gg2-2022.10-backbone-v4-nb.qza \
       --i-reads rep-seqs.qza \
       --o-classification taxonomy.qza

2. Creates tabular summaries of taxonomy assignments.

3. Generates interactive taxa barplots for ASV and OTU tables.
"""

from pathlib import Path

from qiime2 import Artifact, Metadata
from qiime2.plugins import feature_classifier, metadata as q2_metadata, taxa


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Inputs from previous steps
ASV_REP_SEQS = PROJECT_ROOT / "outputs/07.0_filter-for-div/asv-rep-seqs-bio.qza"
OTU_REP_SEQS = PROJECT_ROOT / "outputs/07.0_filter-for-div/otu-rep-seqs-bio.qza"
ASV_TABLE = PROJECT_ROOT / "outputs/07.0_filter-for-div/asv-table-bio.qza"
OTU_TABLE = PROJECT_ROOT / "outputs/07.0_filter-for-div/otu-table-bio.qza"
METADATA_TSV = PROJECT_ROOT / "data/processed/sample-metadata.tsv"

# Greengenes2 V4 Naive Bayes classifier (sklearn 1.4.2 compatible)
CLASSIFIER = PROJECT_ROOT / "data/processed/gg2-2022.10-backbone-v4-nb.qza"

# Outputs
OUTPUT_DIR = PROJECT_ROOT / "outputs/09_taxonomy"

ASV_TAXONOMY = OUTPUT_DIR / "asv-taxonomy.qza"
ASV_TAXONOMY_VIZ = OUTPUT_DIR / "asv-taxonomy.qzv"
ASV_TAXA_BAR = OUTPUT_DIR / "asv-taxa-bar-plots.qzv"

OTU_TAXONOMY = OUTPUT_DIR / "otu-taxonomy.qza"
OTU_TAXONOMY_VIZ = OUTPUT_DIR / "otu-taxonomy.qzv"
OTU_TAXA_BAR = OUTPUT_DIR / "otu-taxa-bar-plots.qzv"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def check_inputs():
    required = [
        ASV_REP_SEQS,
        OTU_REP_SEQS,
        ASV_TABLE,
        OTU_TABLE,
        METADATA_TSV,
        CLASSIFIER,
    ]
    missing = [p for p in required if not p.exists()]

    if missing:
        print("ERROR: The following required input files are missing:")
        for p in missing:
            print(f"  - {p}")
        raise SystemExit(1)


def run_taxonomy_pipeline(label: str,
                          rep_seqs_path: Path,
                          table_path: Path,
                          taxonomy_artifact_path: Path,
                          taxonomy_viz_path: Path,
                          barplot_path: Path):
    """Run classify_sklearn + tabulate + barplot for one dataset."""
    print("------------------------------------------------------------------")
    print(f"Running Greengenes2 taxonomic analysis for {label}")
    print(f"Rep-seqs: {rep_seqs_path}")
    print(f"Table:    {table_path}")
    print(f"Classifier: {CLASSIFIER}")
    print("------------------------------------------------------------------")

    rep_seqs = Artifact.load(str(rep_seqs_path))
    classifier = Artifact.load(str(CLASSIFIER))
    table = Artifact.load(str(table_path))
    sample_metadata = Metadata.load(str(METADATA_TSV))

    # 1) classify_sklearn
    print(f"[{label}] Classifying sequences with Greengenes2 NB classifier...")
    taxonomy_res = feature_classifier.methods.classify_sklearn(
        reads=rep_seqs,
        classifier=classifier
    )
    taxonomy = taxonomy_res.classification
    taxonomy.save(str(taxonomy_artifact_path))

    # 2) Tabulate taxonomy
    print(f"[{label}] Creating taxonomy summary table...")

    # Convert FeatureData[Taxonomy] artifact to Metadata for tabulation
    tax_meta = taxonomy.view(Metadata)

    taxonomy_viz = q2_metadata.visualizers.tabulate(
        input=tax_meta
    )
    taxonomy_viz.visualization.save(str(taxonomy_viz_path))




    # 3) Taxa barplots
    print(f"[{label}] Generating taxa barplots...")
    barplot = taxa.visualizers.barplot(
        table=table,
        taxonomy=taxonomy,
        metadata=sample_metadata
    )
    barplot.visualization.save(str(barplot_path))

    print(f"[{label}] DONE.")
    print(f"  Taxonomy artifact: {taxonomy_artifact_path}")
    print(f"  Taxonomy summary : {taxonomy_viz_path}")
    print(f"  Taxa barplots    : {barplot_path}")
    print()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("======================================================================")
    print("TASK 9: TAXONOMIC ANALYSIS WITH GREENGENES2 (ASV + OTU)")
    print("======================================================================")

    check_inputs()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Input files found. Starting taxonomic classification and barplot generation...\n")

    # ASV
    run_taxonomy_pipeline(
        label="ASV (DADA2)",
        rep_seqs_path=ASV_REP_SEQS,
        table_path=ASV_TABLE,
        taxonomy_artifact_path=ASV_TAXONOMY,
        taxonomy_viz_path=ASV_TAXONOMY_VIZ,
        barplot_path=ASV_TAXA_BAR
    )

    # OTU
    run_taxonomy_pipeline(
        label="OTU (vsearch 97%)",
        rep_seqs_path=OTU_REP_SEQS,
        table_path=OTU_TABLE,
        taxonomy_artifact_path=OTU_TAXONOMY,
        taxonomy_viz_path=OTU_TAXONOMY_VIZ,
        barplot_path=OTU_TAXA_BAR
    )

    print("======================================================================")
    print("Taxonomic analysis with Greengenes2 completed.")
    print("You can view the .qzv files at https://view.qiime2.org")
    print("======================================================================")


if __name__ == "__main__":
    main()