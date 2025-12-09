#!/usr/bin/env python3
"""
Genus-Level Taxonomic Analysis Script for EOTRH Microbiome Study
Calculates genus-level relative abundances and compares across disease states and sample types
Processes both ASV and OTU datasets
"""

import os
import pandas as pd
import sys

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAX_DIR = os.path.join(BASE_DIR, 'data', 'taxonomy')
ASV_L6_FILE = os.path.join(TAX_DIR, 'asv-level-6.csv')
OTU_L6_FILE = os.path.join(TAX_DIR, 'otu-level-6.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', '99_tax-analysis')

# Create directories
os.makedirs(TAX_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_genus_name(taxonomy_string):
    """Extract clean genus name from full taxonomy string"""
    if pd.isna(taxonomy_string):
        return "Unknown"
    
    # If it ends with ;__, it's unclassified at genus level
    if taxonomy_string.endswith(';__'):
        # Get the last classified level
        parts = taxonomy_string.split(';')
        for i in range(len(parts)-1, -1, -1):
            if parts[i] and parts[i] != '__':
                level_prefix = parts[i].split('__')[0]
                level_name = parts[i].split('__')[1] if '__' in parts[i] else parts[i]
                return f"{level_name}* ({level_prefix})"
        return "Unclassified"
    
    # If it has g__, extract genus name
    if ';g__' in taxonomy_string:
        genus = taxonomy_string.split(';g__')[1]
        return genus if genus else "Unclassified"
    
    return "Unclassified"

def load_and_process_data(filepath, dataset_type):
    """Load level-6 CSV file and identify taxonomy columns"""
    print("=" * 90)
    print(f"LOADING {dataset_type} DATA")
    print("=" * 90)
    
    df = pd.read_csv(filepath)
    
    # Identify columns
    metadata_cols = ['index', 'sum-reads', 'seq-pos', 'subject', 'sample-type', 
                     'tooth-number', 'tooth-location', 'replicate', 'gender', 
                     'age', 'disease-state', 'din']
    
    # Find taxonomy columns
    taxa_cols = [col for col in df.columns if col.startswith('d__Bacteria')]
    
    # Filter out calculation rows at the bottom (if any)
    df_clean = df[df['disease-state'].isin(['healthy', 'onset', 'diseased'])].copy()
    
    print(f"\nLoaded {len(df_clean)} samples")
    print(f"Found {len(taxa_cols)} taxonomic features (genera)")
    print(f"\nSample distribution:")
    print(f"  Healthy:  {len(df_clean[df_clean['disease-state']=='healthy'])}")
    print(f"  Onset:    {len(df_clean[df_clean['disease-state']=='onset'])}")
    print(f"  Diseased: {len(df_clean[df_clean['disease-state']=='diseased'])}")
    print(f"\nSample type distribution:")
    print(f"  Gum:    {len(df_clean[df_clean['sample-type']=='Gum'])}")
    print(f"  Plaque: {len(df_clean[df_clean['sample-type']=='Plaque'])}")
    
    return df_clean, taxa_cols, metadata_cols

def calculate_relative_abundances(df, taxa_cols):
    """Calculate relative abundance (%) for each genus in each sample"""
    print("\n" + "=" * 90)
    print("CALCULATING RELATIVE ABUNDANCES")
    print("=" * 90)
    
    # Create a copy for calculations
    df_rel = df.copy()
    
    # Calculate sum-reads if not present
    if 'sum-reads' not in df_rel.columns:
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
    """Calculate mean relative abundance for each genus by disease state"""
    print("\n" + "=" * 90)
    print("SUMMARY BY DISEASE STATE")
    print("=" * 90)
    
    results = []
    
    for taxa_col in taxa_cols:
        genus_name = clean_genus_name(taxa_col)
        rel_col = taxa_col + '_rel_abundance'
        
        for disease in ['healthy', 'onset', 'diseased']:
            subset = df_rel[df_rel['disease-state'] == disease]
            if len(subset) > 0:
                mean_abundance = subset[rel_col].mean()
                
                results.append({
                    'Genus': genus_name,
                    'Taxonomy': taxa_col,
                    'Disease State': disease,
                    'Mean Relative Abundance (%)': mean_abundance,
                    'n_samples': len(subset)
                })
    
    results_df = pd.DataFrame(results)
    
    # Pivot for easier viewing - ORDER COLUMNS: healthy, onset, diseased (gradient)
    pivot_df = results_df.pivot_table(
        index=['Genus', 'Taxonomy'],
        columns='Disease State',
        values='Mean Relative Abundance (%)',
        aggfunc='first'
    ).reset_index()
    
    # Calculate Mean Overall and add as column
    pivot_df['Mean Overall'] = pivot_df[['healthy', 'onset', 'diseased']].mean(axis=1)
    
    # Reorder columns to show gradient: healthy -> onset -> diseased -> Mean Overall
    column_order = ['Genus', 'Taxonomy', 'healthy', 'onset', 'diseased', 'Mean Overall']
    pivot_df = pivot_df[column_order]
    
    # Sort by Mean Overall abundance
    pivot_df = pivot_df.sort_values('Mean Overall', ascending=False)
    
    return pivot_df

def summarize_by_sample_type(df_rel, taxa_cols):
    """Calculate mean relative abundance for each genus by sample type"""
    print("\n" + "=" * 90)
    print("SUMMARY BY SAMPLE TYPE (GUM vs PLAQUE)")
    print("=" * 90)
    
    results = []
    
    for taxa_col in taxa_cols:
        genus_name = clean_genus_name(taxa_col)
        rel_col = taxa_col + '_rel_abundance'
        
        for sample_type in ['Gum', 'Plaque']:
            subset = df_rel[df_rel['sample-type'] == sample_type]
            if len(subset) > 0:
                mean_abundance = subset[rel_col].mean()
                
                results.append({
                    'Genus': genus_name,
                    'Taxonomy': taxa_col,
                    'Sample Type': sample_type,
                    'Mean Relative Abundance (%)': mean_abundance,
                    'n_samples': len(subset)
                })
    
    results_df = pd.DataFrame(results)
    
    # Pivot for easier viewing
    pivot_df = results_df.pivot_table(
        index=['Genus', 'Taxonomy'],
        columns='Sample Type',
        values='Mean Relative Abundance (%)',
        aggfunc='first'
    ).reset_index()
    
    # Calculate Mean Overall and add as column
    pivot_df['Mean Overall'] = pivot_df[['Gum', 'Plaque']].mean(axis=1)
    
    # Sort by Mean Overall abundance
    pivot_df = pivot_df.sort_values('Mean Overall', ascending=False)
    
    return pivot_df

def print_top_genera_by_disease(pivot_df, top_n=15):
    """Print formatted table of top genera by disease state"""
    print("\n" + "=" * 90)
    print(f"TOP {top_n} GENERA BY DISEASE STATE")
    print("=" * 90)
    
    print(f"\n{'Genus':<40} {'Healthy':>10} {'Onset':>10} {'Diseased':>10}")
    print("-" * 90)
    
    for idx, row in pivot_df.head(top_n).iterrows():
        genus = row['Genus'][:38]  # Truncate long names
        healthy = row['healthy']
        onset = row['onset']
        diseased = row['diseased']
        
        print(f"{genus:<40} {healthy:>9.1f}% {onset:>9.1f}% {diseased:>9.1f}%")

def print_gum_vs_plaque(pivot_df, top_n=15):
    """Print formatted table of gum vs plaque comparison"""
    print("\n" + "=" * 90)
    print(f"TOP {top_n} GENERA - GUM vs PLAQUE COMPARISON")
    print("=" * 90)
    
    print(f"\n{'Genus':<40} {'Gum':>10} {'Plaque':>10}")
    print("-" * 90)
    
    for idx, row in pivot_df.head(top_n).iterrows():
        genus = row['Genus'][:38]
        gum = row['Gum']
        plaque = row['Plaque']
        
        print(f"{genus:<40} {gum:>9.1f}% {plaque:>9.1f}%")

def analyze_specific_genera(df_rel, genera_of_interest):
    """Detailed analysis of specific genera of interest"""
    print("\n" + "=" * 90)
    print("DETAILED ANALYSIS OF KEY GENERA")
    print("=" * 90)
    
    for genus_search in genera_of_interest:
        print(f"\n{genus_search.upper()}:")
        print("-" * 90)
        
        # Find the column(s) matching this genus
        matching_cols = [col for col in df_rel.columns 
                        if genus_search.lower() in col.lower() 
                        and col.endswith('_rel_abundance')]
        
        if not matching_cols:
            print(f"  ⚠ Not found in dataset")
            continue
        
        # Use the first matching column
        col = matching_cols[0]
        
        # By disease state
        print("\n  By Disease State:")
        for disease in ['healthy', 'onset', 'diseased']:
            subset = df_rel[df_rel['disease-state'] == disease]
            mean_val = subset[col].mean()
            n = len(subset)
            print(f"    {disease.capitalize():10s} (n={n}): {mean_val:6.1f}%")
        
        # By sample type
        print("\n  By Sample Type:")
        for sample_type in ['Gum', 'Plaque']:
            subset = df_rel[df_rel['sample-type'] == sample_type]
            mean_val = subset[col].mean()
            n = len(subset)
            print(f"    {sample_type:10s} (n={n}): {mean_val:6.1f}%")

def calculate_unclassified_proportion(disease_summary, sample_type_summary):
    """Calculate proportion of reads unclassified at genus level"""
    print("\n" + "=" * 90)
    print("GENUS-LEVEL CLASSIFICATION COMPLETENESS")
    print("=" * 90)
    
    # Identify unclassified taxa (those with asterisk in name)
    unclassified_mask = disease_summary['Genus'].str.contains(r'\*', regex=True)
    
    classified_df = disease_summary[~unclassified_mask]
    unclassified_df = disease_summary[unclassified_mask]
    
    # Calculate totals
    total_abundance = disease_summary['Mean Overall'].sum()
    classified_abundance = classified_df['Mean Overall'].sum()
    unclassified_abundance = unclassified_df['Mean Overall'].sum()
    
    classified_pct = (classified_abundance / total_abundance) * 100
    unclassified_pct = (unclassified_abundance / total_abundance) * 100
    
    n_total = len(disease_summary)
    n_classified = len(classified_df)
    n_unclassified = len(unclassified_df)
    
    print(f"\nOverall Classification Summary:")
    print(f"  Total features:           {n_total}")
    print(f"  Classified to genus:      {n_classified} ({n_classified/n_total*100:.1f}%)")
    print(f"  Unclassified at genus:    {n_unclassified} ({n_unclassified/n_total*100:.1f}%)")
    print(f"\nAbundance-weighted Classification:")
    print(f"  Classified to genus:      {classified_pct:.1f}%")
    print(f"  Unclassified at genus:    {unclassified_pct:.1f}%")
    
    # Break down unclassified by level
    print(f"\nUnclassified Taxa by Highest Classification Level:")
    for level, level_name in [('(f)', 'Family'), ('(o)', 'Order'), ('(c)', 'Class'), ('(p)', 'Phylum')]:
        # Escape both parentheses for regex
        level_pattern = level.replace('(', r'\(').replace(')', r'\)')
        level_mask = unclassified_df['Genus'].str.contains(level_pattern, regex=True)
        if level_mask.any():
            level_df = unclassified_df[level_mask]
            level_abundance = level_df['Mean Overall'].sum()
            level_pct = (level_abundance / total_abundance) * 100
            print(f"  {level_name:15s}: {len(level_df):3d} features ({level_pct:5.1f}% abundance)")
    
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
    print_top_genera_by_disease(disease_summary, top_n=15)
    
    # Summarize by sample type
    sample_type_summary = summarize_by_sample_type(df_rel, taxa_cols)
    print_gum_vs_plaque(sample_type_summary, top_n=15)
    
    # Calculate unclassified proportion
    unclassified_summary = calculate_unclassified_proportion(disease_summary, sample_type_summary)
    
    # Analyze specific genera of interest
    genera_of_interest = ['Streptococcus', 'Rothia', 'Neisseriaceae', 
                          'Pasteurellaceae', 'Fusobacterium', 'Moraxella']
    analyze_specific_genera(df_rel, genera_of_interest)
    
    # Save results to CSV
    print("\n" + "=" * 90)
    print("SAVING RESULTS")
    print("=" * 90)
    
    output_file1 = os.path.join(OUTPUT_DIR, f'{output_prefix}_genus_abundance_by_disease.csv')
    output_file2 = os.path.join(OUTPUT_DIR, f'{output_prefix}_genus_abundance_by_sample_type.csv')
    output_file3 = os.path.join(OUTPUT_DIR, f'{output_prefix}_classification_summary.txt')
    
    disease_summary.to_csv(output_file1, index=False)
    print(f"\n✓ Saved: {output_file1}")
    
    sample_type_summary.to_csv(output_file2, index=False)
    print(f"✓ Saved: {output_file2}")
    
    # Save classification summary to text file
    with open(output_file3, 'w') as f:
        f.write(f"GENUS-LEVEL CLASSIFICATION SUMMARY - {dataset_type}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total features:           {unclassified_summary['n_total']}\n")
        f.write(f"Classified to genus:      {unclassified_summary['n_classified']} ")
        f.write(f"({unclassified_summary['n_classified']/unclassified_summary['n_total']*100:.1f}%)\n")
        f.write(f"Unclassified at genus:    {unclassified_summary['n_unclassified']} ")
        f.write(f"({unclassified_summary['n_unclassified']/unclassified_summary['n_total']*100:.1f}%)\n\n")
        f.write("Abundance-weighted Classification:\n")
        f.write(f"  Classified to genus:    {unclassified_summary['classified_pct']:.1f}%\n")
        f.write(f"  Unclassified at genus:  {unclassified_summary['unclassified_pct']:.1f}%\n")
    
    print(f"✓ Saved: {output_file3}")
    
    return output_file1, output_file2, output_file3

def main():
    """Main analysis pipeline"""
    
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 20 + "EOTRH MICROBIOME - TAXONOMIC ANALYSIS" + " " * 31 + "║")
    print("║" + " " * 28 + "ASV and OTU Comparison" + " " * 40 + "║")
    print("╚" + "=" * 88 + "╝")
    
    all_outputs = []
    
    # Process ASV dataset
    print("\n" + "🔬" * 45)
    asv_outputs = process_dataset(ASV_L6_FILE, "ASV ANALYSIS", "asv")
    if asv_outputs:
        all_outputs.extend(asv_outputs)
    
    # Process OTU dataset
    print("\n" + "🔬" * 45)
    otu_outputs = process_dataset(OTU_L6_FILE, "OTU ANALYSIS", "otu")
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