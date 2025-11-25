# Fallstudie: 16S rRNA Microbiome Data Analysis using QIIME 2

This repository contains the workflow and scripts for the 16S rRNA gene sequencing data analysis for the "Fallstudie" project. The analysis is structured into multiple, sequential steps, primarily utilizing the QIIME 2 bioinformatics platform.

## Setup 

This project uses a Conda environment to manage all necessary software and dependencies.

1.  **Install Environment:** Navigate to the main project directory and create the environment using the provided specification file: `conda env create -f environment.yml`
2.  **Activate Environment:** Activate the newly created environment before executing any analysis scripts: `conda activate eotrh-analysis`

**Note on script execution**

All primary analysis scripts (`.py` files) are designed to be executable from the `project/scripts` directory. Before running any script, ensure it has executable permissions (if needed):`chmod +x [file_name].py`

# Analysis Workflow

The workflow includes both Amplicon Sequence Variant (ASV)-based (using DADA2) and Operational Taxonomic Unit (OTU)-based (using vsearch at 97% similarity) approaches. We aim to compare the results of both.

## 1 Sample Metadata

This step prepares the sample metadata into a QIIME 2-compatible format and performs initial data review.

* Command: `./01_sample-metadata.py`
* Input: project/data/raw/EOTRH-MetadatenProben-WS2025.xlsx
* Output: 
    - project/data/processed/sample-metadata.tsv
    - project/outputs/01_metadata/metadata.qzv
* Note: metadata.qzv can be evaluated in GoogleSheets with the Keemei plugin to check whether the metadata fulfills QIIME2 standards. The report of Keemei is saved in project/reports. 

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
* Note: demux-summary.qzv can be viewed at https://view.qiime2.org 
    - used to determine the trimming and truncation parameters for DADA2 denoising in Task 4 (specifically the --p-trunc-len-f and --p-trunc-len-r parameters)
    - Report saved in project/reports

## 4 Sequence quality control and feature table construction

### Choosing trim values

Review of interactive quality plot (demux-summary.qzv)

* Sequence Coverage
    * all 23 samples imported successfully
    * Range: 4012 to 79,184 sequences per sample
    * Median: ~65,675 sequences per sample
    * good coverage for analysis
* Sequence Length
    * all sequences are 301 bp (both fw and rv)
* Quality Scores 
    * Forward Reads
        * Quality stays high (Q35-48) until position 270-280
        * by position 280-300, quality drops to Q10-15
    * Reverse Reads
        * Quality stays high (Q35-38) until around position 230-240
        * after position 250, quality drops even more drastic than fw

Optimal cutoffs for feature table construction
* --p-trim-left m (trims off the first m bases of each sequence)
    * FW: 0
    * RV: 0 
* --p-trunc-len n (truncates each sequence at position n)
    * FW: 270 
    * RV: 240 

### 4.1 qiime dada2 

Generate ASVs using DADA2.

* Command: `./04.1_dada2.py`
* Input: 
    - project/outputs/02_import/paired-end-sequences.qza
* Output: 
    - project/outputs/04.1_dada2/table.qza
    - project/outputs/04.1_dada2/rep-seqs.qza
    - project/outputs/04.1_dada2/denoising-stats.qza
* Note: This script may take very long (9+ hours in my case), if you would like to run it overnight, you can use following command instead: `nohup ./04.1_dada2.py > ~/dada2.log 2>&1`

#### Generate visualization of denoising file

* Command: `./04.1_dada2-metadata.py`
* Input: 
    - denoising-stats.qza
* Output: 
    - project/outputs/04.1_dada2/denoising-stats.qzv 
* Note: Report saved in project/reports

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
* Note: Reports saved in project/reports

## 5 Filtering features from the feature table

Remove rare features (present in <2 samples)

* Command: `./05_filter-ftable.py`
* Input: (project/outputs/04.1_dada2/ & project/outputs/04.2_vsearch/)
    - table.qza
    - rep-seqs.qza
    - table-clustered-97.qza
    - rep-seqs-clustered-97.qza
* Output: (project/outputs/05_filter-ftable/)
    - dada2-asv-table-ms2.qza / 
    - dada2-asv-rep-seqs-ms2.qza 
    - vsearch-otu-table-ms2.qza 
    - vsearch-otu-rep-seqs-ms2.qza 
    - Corresponding .qzv visualization files for quality checking
* Note: Reports saved in project/reports

## 6 Checking for contamination 

* Command: `./06.1_check-cont-identify.py`
* Input: (project/outputs/04.1_dada2/ & project/outputs/04.2_vsearch/ & project/data/processed)
    - table.qza
    - table-clustered-97.qza
    - sample-metadata.tsv
* Output: (project/outputs/06_check-cont/)
    - dada2-asv-decontam-scores.qza
    - vsearch-otu-decontam-scores.qza
* Note: After running dada2 denoising (step 4.1), the negative control was filtered out because it contained only low quality reads and chimeric articts. As the scripts in code 6 either requires a) negative control (prevalence method) or b) DNA concentrations and neither of them were given, we were not able to perform the decontamination step. Anyways, the filtered-out negative sample indicates neglibile contamination in the sequencing process. 

## 7 Generate a tree for phylogenetic diversity analyses

Before starting the generation of trees for phylogenetic diversity, the control samples need to be filtered. To do this, perform following steps: 

* Command: `./07.0_filter-for-div.py`
* Input: (project/outputs/05_filter-ftable/ & project/data/processed)
    - dada2-asv-table-ms2.qza / 
    - dada2-asv-rep-seqs-ms2.qza 
    - vsearch-otu-table-ms2.qza 
    - vsearch-otu-rep-seqs-ms2.qza 
    - sample-metadata.tsv
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

Before starting this task, it is essential to choose a value for `--p-sampling-depth` which is the even sampling (i.e. refraction) depth. To do this, review of two files is necessary. 
* asv-table-bio.qza
* otu-table-bio.qza

Choose a value that is as high as possible (so you retain more sequences per sample) while excluding as few samples as possible.

The purpose of this script is to compute diversity metrics to compare microbial community composition within and between samples.

* Command: `./07.1_a-b-div.py`
* Input: (project/outputs/07.0_filter-for-div/ & project/outputs/07_phylo-trees/ & project/data/processed)
    - asv-table-bio.qza
    - otu-table-bio.qza
    - asv-rooted-tree.qza
    - otu-rooted-tree.qza
    - sample-metadata.tsv
* Output: (project/outputs/07.1_a-b-div/)
    - asv-core-metrics
    - otu-core-metrics

#### Test associations between categorical metadata columns and alpha diversity data 

* Command: `./07.1.1_a-sig.py`
* Input: (project/outputs/07.1_a-b-div/asv-core-metrics & project/outputs/07.1_a-b-div/otu-core-metrics & project/data/processed)
    - faith_pd_vector
    - evenness_vector
    - sample-metadata.tsv
* Output: (project/outputs/07.1.1_a-sig/asv & project/outputs/07.1.1_a-sig/otu)
    - faith-pd-group-significance.qzv
    - evenness-group-significance.qzv

#### Test associations between categorical metadata columns and beta diversity data 

* Command: `./07.1.2_b-sig.py`
* Input: (project/outputs/07.1_a-b-div/asv-core-metrics & project/outputs/07.1_a-b-div/otu-core-metrics & project/data/processed)
    - unweighted_unifrac_distance_matrix
    - sample-metadata.tsv
* Output: (project/outputs/07.1.2_b-sig/asv & project/outputs/07.1.1_a-sig/otu)
    - unweighted-unifrac-[metadata-column]- group-significance.qzv






