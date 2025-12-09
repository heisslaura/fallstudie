#!/usr/bin/env python3
"""
Master Analysis Script for EOTRH Microbiome Study
Runs all analysis scripts in the correct order
"""

import subprocess
import sys
import os
from datetime import datetime

# Define the base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# Define all scripts in execution order
SCRIPTS = [
    "01_sample-metadata.py",
    "02_obtaining-and-importing-data.py",
    "03_demultiplexing-sequences.py",
    "04.1_dada2-metadata.py",
    "04.1_dada2.py",
    "04.2_vsearch.py",
    "04.3_ftable-fdata.py",
    "05_filter-ftable.py",
    "06.1_check-cont-identify.py",
    "07.0_filter-for-div.py",
    "07_phylo-trees.py",
    "07.1_a-b-div.py",
    "07.1.1_a-sig.py",
    "07.1.2_b-sig.py",
    "08_a-rare.py",
    "09_tax.py",
    "10.1_ancom-bc-tables.py",
    "10.2_ancom-bc-diff.py",
    "10.3_ancom-bc-genus.py",
]

def print_header():
    """Print script header"""
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 15 + "EOTRH MICROBIOME - MASTER ANALYSIS PIPELINE" + " " * 30 + "║")
    print("║" + " " * 25 + "Running All Analysis Scripts" + " " * 35 + "║")
    print("╚" + "=" * 88 + "╝")
    print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total scripts to run: {len(SCRIPTS)}")
    print("=" * 90)

def print_script_header(script_num, script_name, total_scripts):
    """Print header for each script execution"""
    print("\n")
    print("┌" + "─" * 88 + "┐")
    print(f"│  STEP {script_num}/{total_scripts}: {script_name:<75}│")
    print("└" + "─" * 88 + "┘")

def run_script(script_path, script_name):
    """Run a single script and return success status"""
    try:
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=SCRIPTS_DIR,
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✓ {script_name} completed successfully")
            return True
        else:
            print(f"\n✗ {script_name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n✗ {script_name} failed with error: {str(e)}")
        return False

def print_summary(results, start_time):
    """Print execution summary"""
    end_time = datetime.now()
    duration = end_time - start_time
    
    successful = sum(results.values())
    failed = len(results) - successful
    
    print("\n")
    print("╔" + "=" * 88 + "╗")
    print("║" + " " * 32 + "EXECUTION SUMMARY" + " " * 39 + "║")
    print("╚" + "=" * 88 + "╝")
    
    print(f"\nStart time:      {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time:        {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration:  {duration}")
    print(f"\nTotal scripts:   {len(results)}")
    print(f"Successful:      {successful} ✓")
    print(f"Failed:          {failed} ✗")
    
    if failed > 0:
        print("\n" + "=" * 90)
        print("FAILED SCRIPTS:")
        print("=" * 90)
        for script, success in results.items():
            if not success:
                print(f"  ✗ {script}")
    
    print("\n" + "=" * 90)
    
    if failed == 0:
        print("ALL SCRIPTS COMPLETED SUCCESSFULLY! 🎉")
    else:
        print(f"PIPELINE COMPLETED WITH {failed} FAILED SCRIPT(S)")
    
    print("=" * 90)

def main():
    """Main execution function"""
    
    # Print header
    print_header()
    
    # Track results
    results = {}
    start_time = datetime.now()
    
    # Run each script in sequence
    for i, script_name in enumerate(SCRIPTS, 1):
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        
        # Check if script exists
        if not os.path.exists(script_path):
            print(f"\n⚠ Warning: {script_name} not found, skipping...")
            results[script_name] = False
            continue
        
        # Print script header
        print_script_header(i, script_name, len(SCRIPTS))
        
        # Run script
        success = run_script(script_path, script_name)
        results[script_name] = success
        
        # If script failed, ask user if they want to continue
        if not success:
            print("\n" + "⚠" * 45)
            user_input = input("\nScript failed. Continue with remaining scripts? (y/n): ")
            if user_input.lower() != 'y':
                print("\nPipeline execution stopped by user.")
                break
    
    # Print summary
    print_summary(results, start_time)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()