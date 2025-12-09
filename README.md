# Fallstudie: 16S rRNA Microbiome Data Analysis using QIIME 2

This repository contains the workflow and scripts for the 16S rRNA gene sequencing data analysis for the "Fallstudie" project. The analysis is structured into multiple, sequential steps, primarily utilizing the QIIME 2 bioinformatics platform.

## Data availability

Raw sequencing data and metadata is available upon request. Upon receiving data, metadata should be saved in project/data/raw and sequencing files in project/data/raw/20241209-raw_data. 

## Setup 

This project uses a Conda environment to manage all necessary software and dependencies.

1.  **Install Environment:** Navigate to the main project directory and create the environment using the provided specification file: `conda env create -f environment.yml`
2.  **Activate Environment:** Activate the newly created environment before executing any analysis scripts: `conda activate eotrh-analysis`

**Note on script execution and visualization**

All primary analysis scripts (`.py` files) are designed to be executable from the `project/scripts` directory and can be run individually. Before running any script, ensure it has executable permissions (if needed):`chmod +x [file_name].py`. However, if you prefer to run all in one go, please use the master script `00_run-all.py` using the command: `./00_run-all.py` - this can be run from anywhere. 

All .qzv files can be viewed at [QIIME2view](https://view.qiime2.org)

# Analysis Workflow

The workflow includes both Amplicon Sequence Variant (ASV)-based (using DADA2) and Operational Taxonomic Unit (OTU)-based (using vsearch at 97% similarity) approaches. We aim to compare the results of both.

## 1 Sample Metadata

Prepare sample metadata into a QIIME 2-compatible format and perform initial data review.

* Command: `./01_sample-metadata.py`
* Input: project/data/raw/EOTRH-MetadatenProben-WS2025.xlsx
* Output: 
    - project/data/processed/sample-metadata.tsv
    - project/outputs/01_metadata/metadata.qzv
* Note: metadata.qzv can be evaluated in GoogleSheets with the Keemei plugin to check whether the metadata fulfills QIIME2 standards. Our report of Keemei is saved in project/reports. 

## 2 Obtaining and importing data

Create manifest file and import FASTQ reads into QIIME 2.

* Command: `./02_obtaining-and-importing-data.py`
* Input: 
    - project/data/raw/20241209-raw_data/*.fastq.gz
    - project/data/processed/sample-metadata.tsv
* Output: 
    - project/data/processed/manifest.tsv
    - project/outputs/02_import/paired-end-sequences.qza

## 3 Demultiplexing sequences

Generate quality plots (samples already demultiplexed)

* Command: `./03_demultiplexing-sequences.py`
* Input: 
    - project/outputs/02_import/paired-end-sequences.qza
* Output: 
   - project/outputs/03_quality/demux-summary.qzv
* Note:
    - review output to determine trimming and truncation parameters for DADA2 denoising in Task 4 

## 4 Sequence quality control and feature table construction

### Choosing trim values

Review of interactive quality plot (demux-summary.qzv)

* Check Sequence Coverage
    * Were all samples imported successfully?
    * What is the range of seq per sample?
    * What is the median? 
    * Is the coverage good enough for the analysis? 
* Sequence Length
    * What is the sequence length?
* Quality Scores 
    * How is the quality of the reads?
    * At what point does quality decline?
    * Are primer sequences maintained through demultiplexing? 

Based on the findings, choose appropriate cutoff values. 

### 4.1 qiime dada2 

Generate ASVs using DADA2.

* Command: `./04.1_dada2.py`
* Input: 
    - project/outputs/02_import/paired-end-sequences.qza
* Output: 
    - project/outputs/04.1_dada2/table.qza
    - project/outputs/04.1_dada2/rep-seqs.qza
    - project/outputs/04.1_dada2/denoising-stats.qza
* Note: This script may take very long, if you would like to run it overnight, you can use following command instead: `nohup ./04.1_dada2.py > ~/dada2.log 2>&1`

#### Generate visualization of denoising file

* Command: `./04.1_dada2-metadata.py`
* Input: 
    - denoising-stats.qza
* Output: 
    - project/outputs/04.1_dada2/denoising-stats.qzv 

### 4.2 qiime vsearch

Cluster ASVs into OTUs at 97% similarity.

* Command: `./04.2_vsearch.py`
* Input: 
    - project/outputs/04.1_dada2/table.qza
    - project/outputs/04.1_dada2/rep-seqs.qza
* Output: 
    - project/outputs/04.1_vsearch/table-clustered-97.qza
    - project/outputs/04.1_vsearch/rep-seqs-clustered-97.qza
    - project/outputs/04.1_vsearch/table-clustered-97.qzv
    - project/outputs/04.1_vsearch/rep-seqs-clustered-97.qzv

### 4.3 FeatureTable and FeatureData summaries

Create visual summaries (feature counts, sequence lengths, BLAST links) for both ASV and OTU datasets. 

* Command: `./04.3_ftable-fdata.py`
* Input: 
    - project/outputs/04.1_dada2/table.qza
    - project/outputs/04.1_dada2/rep-seqs.qza
    - project/outputs/04.1_vsearch/table-clustered-97.qza
    - project/outputs/04.1_vsearch/rep-seqs-clustered-97.qza
* Output: 
   - project/outputs/04.3_ftable-fdata/dada2-asv-table-summary.qzv
   - project/outputs/04.3_ftable-fdata/dada2-asv-rep-seqs-summary.qzv
   - project/outputs/04.3_ftable-fdata/vsearch-otu-table-summary.qzv
   - project/outputs/04.3_ftable-fdata/vsearch-otu-rep-seqs-summary.qzv

## 5 Filtering features from the feature table

Remove rare features (present in <2 samples)

* Command: `./05_filter-ftable.py`
* Input: 
    - project/outputs/04.1_dada2/table.qza
    - project/outputs/04.1_dada2/rep-seqs.qza
    - project/outputs/04.2_vsearch/table-clustered-97.qza
    - project/outputs/04.2_vsearch/rep-seqs-clustered-97.qza
* Output: (project/outputs/05_filter-ftable/)
    - dada2-asv-table-ms2.qza  
    - dada2-asv-rep-seqs-ms2.qza 
    - vsearch-otu-table-ms2.qza 
    - vsearch-otu-rep-seqs-ms2.qza 
    - Corresponding .qzv visualization files for quality checking

## 6 Checking for contamination 

* Command: `./06.1_check-cont-identify.py`
* Input: 
    - project/outputs/04.1_dada2/table.qza
    - project/outputs/04.2_vsearch/table-clustered-97.qza
    - project/data/processedsample-metadata.tsv
* Output: (project/outputs/06_check-cont/)
    - dada2-asv-decontam-scores.qza
    - vsearch-otu-decontam-scores.qza
* Note: The negative control contained zero sequences after DADA2 chimera removal confirming negligible contamination during sample processing. Formal decontamination workflows using prevalence-based or frequency-based filtering methods were attempted but could not be executed, as these require either a negative control with retained sequences or DNA concentration metadata. Since the negative control contained zero sequences after chimera removal and DNA concentrations were not available, neither decontamination approach was applicable. Nevertheless, the negative control's elimination through routine quality filtering provided strong evidence that contamination was absent.

## 7 Generate a tree for phylogenetic diversity analyses

Before starting the generation of trees for phylogenetic diversity, the control samples need to be filtered. To do this, perform following steps: 

* Command: `./07.0_filter-for-div.py`
* Input: 
    - project/outputs/05_filter-ftable/dada2-asv-table-ms2.qza 
    - project/outputs/05_filter-ftable/dada2-asv-rep-seqs-ms2.qza 
    - project/outputs/05_filter-ftable/vsearch-otu-table-ms2.qza 
    - project/outputs/05_filter-ftable/vsearch-otu-rep-seqs-ms2.qza 
    - project/data/processed/sample-metadata.tsv
* Output: (project/outputs/07.0_filter-for-div/)
    - asv-rep-seqs-bio.qza
    - asv-table-bio.qza
    - otu-rep-seqs-bio.qza
    - otu-table-bio.qza
    - corresponding .qzv files 

Now, the phylogenetic trees can be created. 

* Command: `./07_phylo-trees.py`
* Input: (project/outputs/07.0_filter-for-div/)
    - asv-rep-seqs-bio.qza
    - otu-rep-seqs-bio.qza
* Output: (project/outputs/07_phylo-trees/)
    - asv-rooted-tree.qza
    - otu-rooted-tree.qza
    - Alignment and unrooted tree files for both

### 7.1 Alpha and beta diversity analysis

Before starting this task, it is essential to choose a value for `--p-sampling-depth` which is the even sampling (i.e. refraction) depth. To do this, review of two files is necessary. Choose a value that is as high as possible (so you retain more sequences per sample) while excluding as few samples as possible.
* asv-table-bio.qza
* otu-table-bio.qza

Then, compute diversity metrics to compare microbial community composition within and between samples.

* Command: `./07.1_a-b-div.py`
* Input: 
    - project/outputs/07.0_filter-for-div/asv-table-bio.qza
    - project/outputs/07.0_filter-for-div/otu-table-bio.qza
    - project/outputs/07_phylo-treesasv-rooted-tree.qza
    - project/outputs/07_phylo-treesotu-rooted-tree.qza
    - project/data/processed/sample-metadata.tsv
* Output: (project/outputs/07.1_a-b-div/)
    - asv-core-metrics
    - otu-core-metrics

#### Test associations between categorical metadata columns and alpha diversity data 

* Command: `./07.1.1_a-sig.py`
* Input: 
    - project/outputs/07.1_a-b-div/asv-core-metricsfaith_pd_vector
    - project/outputs/07.1_a-b-div/asv-core-metricsevenness_vector
    - project/outputs/07.1_a-b-div/otu-core-metrics/faith_pd_vector
    - project/outputs/07.1_a-b-div/otu-core-metrics/evenness_vector
    - project/data/processed/sample-metadata.tsv
* Output: 
    - project/outputs/07.1.1_a-sig/asv/faith-pd-group-significance.qzv
    - project/outputs/07.1.1_a-sig/asv/ evenness-group-significance.qzv
    - project/outputs/07.1.1_a-sig/otu/faith-pd-group-significance.qzv
    - project/outputs/07.1.1_a-sig/otu/evenness-group-significance.qzv

#### Test associations between categorical metadata columns and beta diversity data 

* Command: `./07.1.2_b-sig.py`
* Input:
    - project/outputs/07.1_a-b-div/asv-core-metrics/unweighted_unifrac_distance_matrix
    - project/outputs/07.1_a-b-div/otu-core-metrics/ unweighted_unifrac_distance_matrix
    - project/data/processed/sample-metadata.tsv
* Output:
    - project/outputs/07.1.2_b-sig/asv/unweighted-unifrac-[metadata-column]- group-significance.qzv
    - project/outputs/07.1.1_a-sig/otu/unweighted-unifrac-[metadata-column]- group-significance.qzv
 
## 8 Alpha rarefaction plotting

Explore alpha diversity as a function of sequencing depth using the `qiime diversity alpha-rarefaction` visualizer. The goal is to assess whether sample richness has been fully captured and to determine a suitable rarefaction depth for downstream analyses.

Before running this script, review the **"Frequency per sample"** summaries of:

- asv-table-bio.qza
- otu-table-bio.qza

Choose a `--p-max-depth` value that is:

- high enough to keep as many reads per sample as possible,
- but low enough that few samples are lost at that depth

The alpha rarefaction visualizer repeatedly rarefies the feature table across a range of depths. At each depth, multiple rarefied tables are generated (`--p-iterations`, default 10), diversity metrics are computed, and the average values are plotted.

* Command: `./08_a-rare.py`
* Input:
    - project/outputs/07.0_filter-for-div/asv-table-bio.qza  
    - project/outputs/07.0_filter-for-div/otu-table-bio.qza 
    - project/outputs/07_phylo-trees/asv-rooted-tree.qza  
    - project/outputs/07_phylo-trees/otu-rooted-tree.qza  
    - project/data/processed/sample-metadata.tsv
* Output: (project/outputs/08_alpha-rarefaction/)
    - asv-alpha-rarefaction.qzv  
    - otu-alpha-rarefaction.qzv

## 9 Taxonomic analysis

Assign taxonomy to representative sequences using Greengenes2 Naive Bayes classifier.

* Command: `./09_taxonomy.py`
* Input: 
    - project/outputs/07.0_filter-for-div/asv-rep-seqs-bio.qza
    - project/outputs/07.0_filter-for-div/asv-table-bio.qza
    - project/outputs/07.0_filter-for-div/otu-rep-seqs-bio.qza
    - project/outputs/07.0_filter-for-div/otu-table-bio.qza
    - project/data/processed/sample-metadata.tsv
    - Greengenes2 2022.10 backbone V4 classifier (downloaded automatically if not present)
* Output: (project/outputs/09_taxonomy/)
    - asv-taxonomy.qza
    - asv-taxonomy.qzv
    - asv-taxa-barplot.qzv
    - otu-taxonomy.qza
    - otu-taxonomy.qzv
    - otu-taxa-barplot.qzv
* Notes: 
    - Uses Greengenes2 2022.10 backbone Naive Bayes classifier trained on V4 region
    - Classifier is compatible with sklearn 1.4.2

## 10 Differential abundance testing with ANCOM-BC

Identify microbial features that differ significantly in abundance between disease states, analyzed separately for gum and plaque samples.

### 10.1 Filter feature tables by sample type

Separate samples into gum and plaque groups for independent differential abundance analysis.

* Command: `./10.1_ancombc-filter.py`
* Input: 
    - project/outputs/07.0_filter-for-div/asv-table-bio.qza
    - project/outputs/07.0_filter-for-div/otu-table-bio.qza
    - project/outputs/09_taxonomy/asv-taxonomy.qza
    - project/outputs/09_taxonomy/otu-taxonomy.qza
    - project/data/processed/sample-metadata.tsv
* Output: (project/outputs/10_ancombc_asv/ and project/outputs/10_ancombc_otu/)
    - asv_gum_table.qza
    - asv_plaque_table.qza
    - otu_gum_table.qza
    - otu_plaque_table.qza
* Note: Tables are filtered by sample type to allow separate differential abundance testing for each tissue type

### 10.2 ANCOM-BC differential abundance analysis

Run ANCOM-BC to identify features differentially abundant between disease states within each sample type.

* Command: `./10.2_ancom-bc-diff.py`
* Input: 
    - project/outputs/10_ancombc_asv/asv_gum_table.qza
    - project/outputs/10_ancombc_asv/asv_plaque_table.qza
    - project/outputs/10_ancombc_otu/otu_gum_table.qza
    - project/outputs/10_ancombc_otu/otu_plaque_table.qza
    - project/data/processed/sample-metadata.tsv
* Output: (project/outputs/10_ancombc_asv/ and project/outputs/10_ancombc_otu/)
    - ancombc_asv_gum.qza / da_barplot_asv_gum.qzv
    - ancombc_asv_plaque.qza / da_barplot_asv_plaque.qzv
    - ancombc_otu_gum.qza / da_barplot_otu_gum.qzv
    - ancombc_otu_plaque.qza / da_barplot_otu_plaque.qzv
* Note: 
    - Significance threshold set to p < 0.001
    - Bar plots show log fold change (LFC) of enriched (blue) and depleted (orange) features

### 10.3 Genus-level differential abundance analysis

Collapse feature tables to genus level (taxonomic level 6) and re-run ANCOM-BC for higher-level taxonomic insights.

* Command: `./10.3_ancom-bc-genus.py`
* Input: 
    - project/outputs/10_ancombc_asv/asv_gum_table.qza
    - project/outputs/10_ancombc_asv/asv_plaque_table.qza
    - project/outputs/10_ancombc_otu/otu_gum_table.qza
    - project/outputs/10_ancombc_otu/otu_plaque_table.qza
    - project/outputs/09_taxonomy/asv-taxonomy.qza
    - project/outputs/09_taxonomy/otu-taxonomy.qza
    - project/data/processed/sample-metadata.tsv
* Output: (project/outputs/10_ancombc_asv/ and project/outputs/10_ancombc_otu/)
    - asv_gum_table_l6.qza / l6_ancombc_asv_gum.qza / l6_da_barplot_asv_gum.qzv
    - asv_plaque_table_l6.qza / l6_ancombc_asv_plaque.qza / l6_da_barplot_asv_plaque.qzv
    - otu_gum_table_l6.qza / l6_ancombc_otu_gum.qza / l6_da_barplot_otu_gum.qzv
    - otu_plaque_table_l6.qza / l6_ancombc_otu_plaque.qza / l6_da_barplot_otu_plaque.qzv

# Acknowledgements
This analysis was conducted as part of the Fallstudie-ILV course at the University of Applied Sciences Wiener Neustadt. The workflow was primarily based on the [QIIME 2 Moving Pictures Tutorial](https://amplicon-docs.qiime2.org/en/latest/tutorials/moving-pictures.html) and the [QIIME 2 Amplicon Documentation](https://amplicon-docs.qiime2.org/en/latest/). Additional guidance was obtained from the [DADA2 Tutorial](https://benjjneb.github.io/dada2/tutorial.html) for denoising parameters and the [Q2 Decontam Tutorial](https://jordenrabasco.github.io/Q2_Decontam_Tutorial.html) for contamination analysis. We acknowledge the QIIME 2 development team for providing this comprehensive microbiome analysis platform.

# Additional analysis

Besides the comprehensive workflow, we provide additional scripts that analyze taxonomic results to obtain quantitative values. Required input data can be downloaded using output from step 9 (taxonomic analysis) 
* otu-taxa-barplot.qzv
* asv-taxa-barplot.qzv

Open files in [QIIME2view](https://view.qiime2.org) and select respective taxonomic level. Under "Download", click on CSV and save files in folder project/data/taxonomy.  

## Taxonomic Analysis on Phylum Level (L2)

* Command: `./99_tax-analysis-L2.py`
* Input: 
    - project/data/taxonomy/asv-level-2.csv
    - project/data/taxonomy/otu-level-2.csv
* Output: (project/outputs/99_tax-analysis)
    - asv_phylum_classification_summary.txt
    - asv_phylum_abundance_by_disease.csv
    - asv_phylum_abundance_by_sample_type.csv
    - otu_phylum_classification_summary.txt
    - otu_phylum_abundance_by_disease.csv
    - otu_phylum_abundance_by_sample_type.csv

## Taxonomic Analysis on Genus Level (L6)

* Command: `./99_tax-analysis-L6.py`
* Input: 
    - project/data/taxonomy/asv-level-6.csv
    - project/data/taxonomy/otu-level-6.csv
* Output: (project/outputs/99_tax-analysis)
    - asv_classification_summary.txt
    - asv_genus_abundance_by_disease.csv
    - asv_genus_abundance_by_sample_type.csv
    - otu_classification_summary.txt
    - otu_genus_abundance_by_disease.csv
    - otu_genus_abundance_by_sample_type.csv
