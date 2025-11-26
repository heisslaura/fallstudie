#!/usr/bin/env python3

"""
09.2_greengenes2-download-tree.py

Download the Greengenes2 2022.10 rooted taxonomy tree (ASV-based).
"""

import subprocess
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEST = PROJECT_ROOT / "data/processed/gg2-taxonomy-asv-tree.qza"

URL = (
    "http://ftp.microbio.me/greengenes_release/2022.10/"
    "2022.10.taxonomy.asv.nwk.qza"
)

def main():
    print("======================================================================")
    print("TASK 09.2: DOWNLOAD GREENGENES2 TAXONOMY TREE")
    print("======================================================================\n")

    # Ensure directory exists
    (PROJECT_ROOT / "data/processed").mkdir(parents=True, exist_ok=True)

    print(f"Downloading Greengenes2 taxonomy tree -> {DEST}\n")
    try:
        subprocess.run(
            ["wget", "-O", str(DEST), URL],
            check=True
        )
    except subprocess.CalledProcessError:
        print("ERROR: wget failed. Please check your network or the URL.")
        sys.exit(1)

    print("\nDownload complete.\n")

    print("Sanity check (qiime tools peek):\n")
    try:
        subprocess.run(
            ["qiime", "tools", "peek", str(DEST)],
            check=True
        )
    except subprocess.CalledProcessError:
        print("WARNING: qiime tools peek failed. Check if QIIME2 is active.")
        sys.exit(1)

    print("\nGreengenes2 taxonomy tree setup complete.")
    print("======================================================================")

if __name__ == "__main__":
    main()