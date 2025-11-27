# Fallstudie: 16S rRNA Microbiome Data Analysis using QIIME 2

This repository contains the workflow and scripts for the 16S rRNA gene sequencing data analysis for the "Fallstudie" project. The analysis is structured into multiple, sequential steps, primarily utilizing the QIIME 2 bioinformatics platform.

## Data availability

The raw sequencing data is available at NCBI Sequence Read Archive (SRA) under BioProject accession [PRJNA1370082](https://www.ncbi.nlm.nih.gov/sra/PRJNA1370082). 

All sequencing reads and metadata are also available in this GitHub repository (project/data/raw).

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
 
## 8 Alpha rarefaction plotting

This step explores **alpha diversity as a function of sequencing depth** using the  
`qiime diversity alpha-rarefaction` visualizer. The goal is to assess whether sample
richness has been fully captured and to determine a suitable rarefaction depth for
downstream analyses.

Before running this script, review the **"Frequency per sample"** summaries of:

- asv-table-bio.qza
- otu-table-bio.qza

Choose a `--p-max-depth` value that is:

- high enough to keep as many reads per sample as possible,
- but low enough that few samples are lost at that depth.

The alpha rarefaction visualizer repeatedly rarefies the feature table across a range of
depths. At each depth, multiple rarefied tables are generated (`--p-iterations`, default 10),
diversity metrics are computed, and the average values are plotted.

* Command: `./08_alpha-rarefaction.py`


### Input  
(from `project/outputs/07.0_filter-for-div/`, `project/outputs/07_phylo-trees/`, and `project/data/processed/`)

- asv-table-bio.qza  
- otu-table-bio.qza 
- asv-rooted-tree.qza  
- otu-rooted-tree.qza  
- sample-metadata.tsv

### Output  
(saved in `project/outputs/08_alpha-rarefaction/`)

- asv-alpha-rarefaction.qzv  
- otu-alpha-rarefaction.qzv

### Interpretation of the visualization

**Top plot – Alpha rarefaction curve**  
Shows how alpha diversity changes with increasing sampling depth.
*  Note: `asv-alpha-rarefaction.qzv`and `otu-alpha-rarefaction.qzv` can be viewed at https://view.qiime2.org

- Curves that *level off* → sequencing depth likely sufficient.  
- Curves that *do not level off* → possible undersampling or sequencing noise.

**Bottom plot – Sample retention plot**  
Shows how many samples remain at each depth.  
If many samples drop out at high depths, group averages at those depths may be unreliable.

### Purpose  
This step ensures that sequencing depth is adequate and helps guide the choice of an
appropriate rarefaction depth for alpha and beta diversity analyses.


## 9 Taxonomic Analysis (Greengenes2)

Taxonomic analysis identifies who is present in the microbial community by assigning taxonomy to ASVs and OTUs.
For this project we use Greengenes2 (2022.10) — a modern, phylogenetically consistent taxonomy and reference database.

This workflow consists of:
- Installing and verifying Greengenes2 + classifier (09.1)
- Downloading the rooted Greengenes2 taxonomy tree (09.2)
- Running taxonomy assignment + barplots (09)

**Background**
**Greengenes2 integrates:**
- Whole-genome phylogeny from Web of Life
- Full-length 16S rRNA from Living Tree Project
- 16S operons extracted via uDance
- Placement of millions of V4 fragments using DEPP
- Taxonomy derived from GTDB + LTP and decorated using tax2tree

**Greengenes2 provides:**
- High-quality, phylogenetically coherent taxonomy
- Extracted V4 sequences (515F/806R)
- Pre-trained Naive Bayes classifiers

**Multiple naming schemes (ASV, MD5, ID)**
Important:

For standard QIIME2 16S V4 workflows, Greengenes2 should be used with:
feature-classifier classify-sklearn
(NOT greengenes2 taxonomy-from-features)
because only sequences already in the GG2 tree can be classified via taxonomy-from-features.

**9.1 Greengenes2 Setup**

Run the setup script:
`./09.1_greengenes2-setup.py`

This script:

Verifies that the q2-greengenes2 plugin is installed
Checks or downloads the correct Greengenes2 2022.10 V4 NB classifier, compatible with scikit-learn 1.4.2:
data/processed/gg2-2022.10-backbone-v4-nb.qza

**9.2 Download Greengenes2 Taxonomy Tree**

Run:
`./09.2_greengenes2-download-tree.py`

This script downloads the official ASV-keyed Greengenes2 taxonomy tree, type Phylogeny[Rooted]:
data/processed/gg2-taxonomy-asv-tree.qza

**Sanity check:**
`qiime tools peek data/processed/gg2-taxonomy-asv-tree.qza`

**Expected: Type: Phylogeny[Rooted]**
This tree is optional for classification, but useful for phylogenetic analysis and feature filtering.

***9.3 Taxonomic Classification (ASV + OTU)***

Run:
`./09_taxonomic-analysis.py`

This script performs:

1. ASV taxonomy assignment
Using the Greengenes2 2022.10 V4 NB classifier with:
`qiime feature-classifier classify-sklearn`

2. OTU taxonomy assignment
Using the same classifier for vsearch OTUs.

3. Generation of taxonomy tables (.qza) and summaries (.qzv)
4. Taxa barplots (taxa barplot)
Interactive stacked bar charts grouped by sample metadata.

**Output Files**
All results are stored in:
`project/outputs/09_taxonomy/`

You will find:
- asv-taxonomy.qza
- asv-taxonomy.qzv
- asv-taxa-bar-plots.qzv`

- otu-taxonomy.qza
- otu-taxonomy.qzv
- otu-taxa-bar-plots.qzv

Visualization is available at:

https://view.qiime2.org/


## 10 Differential Abundance Testing (ANCOM-BC)

This step identifies features (ASVs and OTUs) that differ significantly in abundance between sample groups.

We use ANCOM-BC, implemented in the QIIME 2 plugin q2-composition, which performs compositionally-aware differential abundance analysis with bias correction.

Script: `scripts/10_ancombc.py`

This script runs ANCOM-BC on both ASV and OTU feature tables using a selected metadata column (e.g. subject).

It performs:
- ANCOM-BC at feature level (ASVs, OTUs)
- Taxonomic collapse at level 6 (genus)
- ANCOM-BC at genus level
- Barplot generation of significant differential features

*Input*

(from project/outputs/07.0_filter-for-div/, project/outputs/09_taxonomy/, and project/data/processed/)

- asv-table-bio.qza
- otu-table-bio.qza
- asv-taxonomy.qza
- otu-taxonomy.qza
- sample-metadata.tsv

*Output*

(saved in project/outputs/10_ancombc/)

- asv-ancombc.qza
- asv-ancombc-barplot.qzv
- asv-l6-table.qza
- asv-l6-ancombc.qza
- asv-l6-barplot.qzv

(Equivalent files for OTU analysis)


*Run the script:*

`cd project/scripts`
`./10_ancombc.py`

The script will:

- Validate input files
- Run ANCOM-BC
- Collapse by taxonomy level
- Produce summary barplots for differentially abundant taxa

**Notes**

- ANCOM-BC requires that sample IDs in metadata match sample IDs in the feature tables.
- If the script reports missing sample IDs, check whether your metadata uses human-readable names but the table uses hashed DADA2 sample IDs.
- If needed, you can ask for an automated metadata ID-fixing helper script — I can generate it for you (10_fix-metadata.py), but it is not part of your current workflow.


# Acknowledgements
This analysis was conducted as part of the Fallstudie-ILV course at the University of Applied Sciences Wiener Neustadt. The workflow was primarily based on the [QIIME 2 Moving Pictures Tutorial](https://amplicon-docs.qiime2.org/en/latest/tutorials/moving-pictures.html) and the [QIIME 2 Amplicon Documentation](https://amplicon-docs.qiime2.org/en/latest/). Additional guidance was obtained from the [DADA2 Tutorial](https://benjjneb.github.io/dada2/tutorial.html) for denoising parameters and the [Q2 Decontam Tutorial](https://jordenrabasco.github.io/Q2_Decontam_Tutorial.html) for contamination analysis. We acknowledge the QIIME 2 development team (Bolyen et al., 2019, Nature Biotechnology) for providing this comprehensive microbiome analysis platform.

# Contributors
* Laura Heiß | 211567@fhwn.ac.at | [LinkedIn](www.linkedin.com/in/
laura-heiß-863077258)
* Isabella Pauser | 116914@fhwn.ac.at | 
