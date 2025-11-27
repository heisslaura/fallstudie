#!/usr/bin/env python

"""
09.1_greengenes2-setup.py

Helper script: ensure q2-greengenes2 plugin exists and check for the
Greengenes2 2022.10 V4 Naive Bayes classifier compatible with sklearn 1.4.2.
"""

from pathlib import Path
import sys
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLASSIFIER = PROJECT_ROOT / "data/processed/gg2-2022.10-backbone-v4-nb.qza"


def ensure_greengenes2_plugin():
    print("------------------------------------------------------------------")
    print("Checking for q2-greengenes2 plugin...")
    try:
        from qiime2.plugins import greengenes2  # noqa: F401
        print("q2-greengenes2 is already installed.")
    except Exception:
        print("q2-greengenes2 not found. Installing via pip...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "q2-greengenes2"],
                check=True,
            )
            print("q2-greengenes2 installation complete.")
        except subprocess.CalledProcessError as e:
            print("ERROR: Failed to install q2-greengenes2 via pip.")
            print(e)
            raise SystemExit(1)
    print("------------------------------------------------------------------\n")


def check_classifier():
    print("------------------------------------------------------------------")
    print("Checking for Greengenes2 V4 Naive Bayes classifier (sklearn 1.4.2)...")
    print(f"Expected path: {CLASSIFIER}")
    if CLASSIFIER.exists():
        print("Classifier found.")
    else:
        print("Classifier NOT found.")
        print("Please download it with:")
        print("")
        print("  cd ~/fallstudie/project")
        print("  mkdir -p data/processed")
        print("  wget https://ftp.microbio.me/greengenes_release/2022.10/"
              "sklearn-1.4.2-compatible-nb-classifiers/"
              "2022.10.backbone.v4.nb.sklearn-1.4.2.qza \\")
        print("    -O data/processed/gg2-2022.10-backbone-v4-nb.qza")
        print("")
        raise SystemExit(1)
    print("------------------------------------------------------------------\n")


def main():
    print("======================================================================")
    print("TASK 09.1: SETUP GREENGENES2 (PLUGIN + NB CLASSIFIER)")
    print("======================================================================\n")

    ensure_greengenes2_plugin()
    check_classifier()

    print("Setup complete.")
    print("You can now run: ./09_taxonomic-analysis.py")
    print("======================================================================")


if __name__ == "__main__":
    main()