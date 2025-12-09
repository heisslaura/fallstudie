#!/usr/bin/env python3
"""
Phylum-Level Taxonomic Analysis Script for EOTRH Microbiome Study
Calculates phylum-level (Level 2) relative abundances and compares across disease states and sample types
Processes both ASV and OTU datasets
"""

import os
import pandas as pd
import sys

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAX_DIR = os.path.join(BASE_DIR, 'data', 'taxonomy')
ASV_L2_FILE = os.path.join(TAX_DIR, 'asv-level-2.csv')
OTU_L2_FILE = os.path.join(TAX_DIR, 'otu-level-2.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '99_tax-analysis')

# Create directories
os.makedirs(TAX_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_phylum_name(taxonomy_string):
    """Extract clean phylum name from full taxonomy string"""
    if pd.isna(taxonomy_string):
        return "Unknown"
    
    # Check if unclassified at phylum level (ends with ;__)
    if taxonomy_string.endswith(';__'):
        return "Unclassified*"
    
    # Extract phylum name (p__)
    if ';p__' in taxonomy_string:
        phylum = taxonomy_string.split(';p__')[1]
        return phylum if phylum else "Unclassified*"
    
    return "Unclassified*"

def load_and_process_data(filepath, dataset_type):
    """Load level-2 CSV file and identify taxonomy columns"""
    print("=" * 90)
    print(f"LOADING {dataset_type} DATA - PHYLUM LEVEL")
    print("=" * 90)
    
    df = pd.read_csv(filepath)
    
    # Identify columns
    metadata_cols = ['index', 'seq-pos', 'subject', 'sample-type', 
                     'tooth-number', 'tooth-location', 'replicate', 'gender', 
                     'age', 'disease-state', 'din']
    
    # Find taxonomy columns (phylum level - start with d__Bacteria;p__)
    taxa_cols = [col for col in df.columns if col.startswith('d__Bacteria')]
    
    # Filter out calculation rows at the bottom (if any)
    df_clean = df[df['disease-state'].isin(['healthy', 'onset', 'diseased'])].copy()
    
    print(f"\nLoaded {len(df_clean)} samples")
    print(f"Found {len(taxa_cols)} phyla")
    print(f"\nSample distribution:")
    print(f"  Healthy:  {len(df_clean[df_clean['disease-state']=='healthy'])}")
    print(f"  Onset:    {len(df_clean[df_clean['disease-state']=='onset'])}")
    print(f"  Diseased: {len(df_clean[df_clean['disease-state']=='diseased'])}")
    print(f"\nSample type distribution:")
    print(f"  Gum:    {len(df_clean[df_clean['sample-type']=='Gum'])}")
    print(f"  Plaque: {len(df_clean[df_clean['sample-type']=='Plaque'])}")
    
    return df_clean, taxa_cols, metadata_cols

def calculate_relative_abundances(df, taxa_cols):
    """Calculate relative abundance (%) for each phylum in each sample"""
    print("\n" + "=" * 90)
    print("CALCULATING RELATIVE ABUNDANCES")
    print("=" * 90)
    
    # Create a copy for calculations
    df_rel = df.copy()
    
    # Calculate sum-reads (total reads per sample)
    print("\nCalculating total reads per sample...")
    df_rel['sum-reads'] = df_rel[taxa_cols].sum(axis=1)
    print(f"✓ Sum-reads calculated (range: {df_rel['sum-reads'].min():.0f} - {df_rel['sum-reads'].max():.0f})")
    
    # Calculate relative abundances
    for taxa_col in taxa_cols:
        new_col = taxa_col + '_rel_abundance'
        df_rel[new_col] = (df_rel[taxa_col] / df_rel['sum-reads']) * 100
    
    print("\n✓ Calculated relative abundances for all samples")
    
    return df_rel

def summarize_by_disease_state(df_rel, taxa_cols):
    """Calculate mean relative abundance for each phylum by disease state"""
    print("\n" + "=" * 90)
    print("SUMMARY BY DISEASE STATE")
    print("=" * 90)
    
    results = []
    
    for taxa_col in taxa_cols:
        phylum_name = clean_phylum_name(taxa_col)
        rel_col = taxa_col + '_rel_abundance'
        
        for disease in ['healthy', 'onset', 'diseased']:
            subset = df_rel[df_rel['disease-state'] == disease]
            if len(subset) > 0:
                mean_abundance = subset[rel_col].mean()
                
                results.append({
                    'Phylum': phylum_name,
                    'Taxonomy': taxa_col,
                    'Disease State': disease,
                    'Mean Relative Abundance (%)': mean_abundance,
                    'n_samples': len(subset)
                })
    
    results_df = pd.DataFrame(results)
    
    # Pivot for easier viewing - ORDER COLUMNS: healthy, onset, diseased (gradient)
    pivot_df = results_df.pivot_table(
        index=['Phylum', 'Taxonomy'],
        columns='Disease State',
        values='Mean Relative Abundance (%)',
        aggfunc='first'
    ).reset_index()
    
    # Calculate Mean Overall and add as column
    pivot_df['Mean Overall'] = pivot_df[['healthy', 'onset', 'diseased']].mean(axis=1)
    
    # Reorder columns to show gradient: healthy -> onset -> diseased -> Mean Overall
    column_order = ['Phylum', 'Taxonomy', 'healthy', 'onset', 'diseased', 'Mean Overall']
    pivot_df = pivot_df[column_order]
    
    # Sort by Mean Overall abundance
    pivot_df = pivot_df.sort_values('Mean Overall', ascending=False)
    
    return pivot_df

def summarize_by_sample_type(df_rel, taxa_cols):
    """Calculate mean relative abundance for each phylum by sample type"""
    print("\n" + "=" * 90)
    print("SUMMARY BY SAMPLE TYPE (GUM vs PLAQUE)")
    print("=" * 90)
    
    results = []
    
    for taxa_col in taxa_cols:
        phylum_name = clean_phylum_name(taxa_col)
        rel_col = taxa_col + '_rel_abundance'
        
        for sample_type in ['Gum', 'Plaque']:
            subset = df_rel[df_rel['sample-type'] == sample_type]
            if len(subset) > 0:
                mean_abundance = subset[rel_col].mean()
                
                results.append({
                    'Phylum': phylum_name,
                    'Taxonomy': taxa_col,
                    'Sample Type': sample_type,
                    'Mean Relative Abundance (%)': mean_abundance,
                    'n_samples': len(subset)
                })
    
    results_df = pd.DataFrame(results)
    
    # Pivot for easier viewing
    pivot_df = results_df.pivot_table(
        index=['Phylum', 'Taxonomy'],
        columns='Sample Type',
        values='Mean Relative Abundance (%)',
        aggfunc='first'
    ).reset_index()
    
    # Calculate Mean Overall and add as column
    pivot_df['Mean Overall'] = pivot_df[['Gum', 'Plaque']].mean(axis=1)
    
    # Sort by Mean Overall abundance
    pivot_df = pivot_df.sort_values('Mean Overall', ascending=False)
    
    return pivot_df

def print_phyla_by_disease(pivot_df):
    """Print formatted table of phyla by disease state"""
    print("\n" + "=" * 90)
    print("PHYLA BY DISEASE STATE")
    print("=" * 90)
    
    print(f"\n{'Phylum':<30} {'Healthy':>12} {'Onset':>12} {'Diseased':>12} {'Mean':>12}")
    print("-" * 90)
    
    for idx, row in pivot_df.iterrows():
        phylum = row['Phylum'][:28]
        healthy = row['healthy']
        onset = row['onset']
        diseased = row['diseased']
        mean = row['Mean Overall']
        
        print(f"{phylum:<30} {healthy:>11.1f}% {onset:>11.1f}% {diseased:>11.1f}% {mean:>11.1f}%")

def print_gum_vs_plaque(pivot_df):
    """Print formatted table of gum vs plaque comparison"""
    print("\n" + "=" * 90)
    print("PHYLA - GUM vs PLAQUE COMPARISON")
    print("=" * 90)
    
    print(f"\n{'Phylum':<30} {'Gum':>12} {'Plaque':>12} {'Mean':>12}")
    print("-" * 90)
    
    for idx, row in pivot_df.iterrows():
        phylum = row['Phylum'][:28]
        gum = row['Gum']
        plaque = row['Plaque']
        mean = row['Mean Overall']
        
        print(f"{phylum:<30} {gum:>11.1f}% {plaque:>11.1f}% {mean:>11.1f}%")

def calculate_unclassified_proportion(disease_summary):
    """Calculate proportion of reads unclassified at phylum level"""
    print("\n" + "=" * 90)
    print("PHYLUM-LEVEL CLASSIFICATION COMPLETENESS")
    print("=" * 90)
    
    # Identify unclassified taxa
    unclassified_mask = disease_summary['Phylum'].str.contains(r'\*', regex=True)
    
    classified_df = disease_summary[~unclassified_mask]
    unclassified_df = disease_summary[unclassified_mask]
    
    # Calculate totals
    total_abundance = disease_summary['Mean Overall'].sum()
    classified_abundance = classified_df['Mean Overall'].sum()
    unclassified_abundance = unclassified_df['Mean Overall'].sum()
    
    classified_pct = (classified_abundance / total_abundance) * 100 if total_abundance > 0 else 0
    unclassified_pct = (unclassified_abundance / total_abundance) * 100 if total_abundance > 0 else 0
    
    n_total = len(disease_summary)
    n_classified = len(classified_df)
    n_unclassified = len(unclassified_df)
    
    print(f"\nOverall Classification Summary:")
    print(f"  Total phyla:              {n_total}")
    print(f"  Classified to phylum:     {n_classified} ({n_classified/n_total*100:.1f}%)")
    print(f"  Unclassified at phylum:   {n_unclassified} ({n_unclassified/n_total*100:.1f}%)")
    print(f"\nAbundance-weighted Classification:")
    print(f"  Classified to phylum:     {classified_pct:.1f}%")
    print(f"  Unclassified at phylum:   {unclassified_pct:.1f}%")
    
    # Create summary dictionary to return
    summary = {
        'n_total': n_total,
        'n_classified': n_classified,
        'n_unclassified': n_unclassified,
        'classified_pct': classified_pct,
        'unclassified_pct': unclassified_pct
    }
    
    return summary

def process_dataset(filepath, dataset_type, output_prefix):
    """Process a single dataset (ASV or OTU)"""
    
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print(f"║{dataset_type.center(90)}║")
    print("╚" + "=" * 88 + "╝")
    
    if not os.path.exists(filepath):
        print(f"⚠ Warning: Could not find file at {filepath}")
        print(f"Skipping {dataset_type} analysis...")
        return
    
    print(f"\nUsing file: {filepath}")
    
    # Load data
    df, taxa_cols, metadata_cols = load_and_process_data(filepath, dataset_type)
    
    # Calculate relative abundances
    df_rel = calculate_relative_abundances(df, taxa_cols)
    
    # Summarize by disease state
    disease_summary = summarize_by_disease_state(df_rel, taxa_cols)
    print_phyla_by_disease(disease_summary)
    
    # Summarize by sample type
    sample_type_summary = summarize_by_sample_type(df_rel, taxa_cols)
    print_gum_vs_plaque(sample_type_summary)
    
    # Calculate unclassified proportion
    unclassified_summary = calculate_unclassified_proportion(disease_summary)
    
    # Save results to CSV
    print("\n" + "=" * 90)
    print("SAVING RESULTS")
    print("=" * 90)
    
    output_file1 = os.path.join(OUTPUT_DIR, f'{output_prefix}_phylum_abundance_by_disease.csv')
    output_file2 = os.path.join(OUTPUT_DIR, f'{output_prefix}_phylum_abundance_by_sample_type.csv')
    output_file3 = os.path.join(OUTPUT_DIR, f'{output_prefix}_phylum_classification_summary.txt')
    
    disease_summary.to_csv(output_file1, index=False)
    print(f"\n✓ Saved: {output_file1}")
    
    sample_type_summary.to_csv(output_file2, index=False)
    print(f"✓ Saved: {output_file2}")
    
    # Save classification summary to text file
    with open(output_file3, 'w') as f:
        f.write(f"PHYLUM-LEVEL CLASSIFICATION SUMMARY - {dataset_type}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total phyla:              {unclassified_summary['n_total']}\n")
        f.write(f"Classified to phylum:     {unclassified_summary['n_classified']} ")
        f.write(f"({unclassified_summary['n_classified']/unclassified_summary['n_total']*100:.1f}%)\n")
        f.write(f"Unclassified at phylum:   {unclassified_summary['n_unclassified']} ")
        f.write(f"({unclassified_summary['n_unclassified']/unclassified_summary['n_total']*100:.1f}%)\n\n")
        f.write("Abundance-weighted Classification:\n")
        f.write(f"  Classified to phylum:   {unclassified_summary['classified_pct']:.1f}%\n")
        f.write(f"  Unclassified at phylum: {unclassified_summary['unclassified_pct']:.1f}%\n")
    
    print(f"✓ Saved: {output_file3}")
    
    return output_file1, output_file2, output_file3

def main():
    """Main analysis pipeline"""
    
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 18 + "EOTRH MICROBIOME - PHYLUM-LEVEL ANALYSIS" + " " * 30 + "║")
    print("║" + " " * 28 + "ASV and OTU Comparison" + " " * 40 + "║")
    print("╚" + "=" * 88 + "╝")
    
    all_outputs = []
    
    # Process ASV dataset
    print("\n" + "🔬" * 45)
    asv_outputs = process_dataset(ASV_L2_FILE, "ASV ANALYSIS - PHYLUM LEVEL", "asv")
    if asv_outputs:
        all_outputs.extend(asv_outputs)
    
    # Process OTU dataset
    print("\n" + "🔬" * 45)
    otu_outputs = process_dataset(OTU_L2_FILE, "OTU ANALYSIS - PHYLUM LEVEL", "otu")
    if otu_outputs:
        all_outputs.extend(otu_outputs)
    
    # Final summary
    print("\n" + "=" * 90)
    print("ANALYSIS COMPLETE!")
    print("=" * 90)
    print("\nGenerated files:")
    for i, filepath in enumerate(all_outputs, 1):
        print(f"  {i}. {filepath}")
    
    print("\n" + "=" * 90)

if __name__ == "__main__":
    main()