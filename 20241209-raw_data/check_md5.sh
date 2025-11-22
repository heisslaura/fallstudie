#!/bin/bash

# File containing the MD5 checksums
MD5_FILE="20241209_HN00230849_MAS_Report/assets/spgs/HN00230849_23samples_md5sum_DownloadLink.txt"

# Loop through each line in the MD5 file
while read -r line; do
  # Extract file name, MD5 sum, and URL
  FILENAME=$(echo "$line" | awk '{print $1}')
  EXPECTED_MD5=$(echo "$line" | awk '{print $3}')

  # Skip lines that don't match your files
  if [[ ! -f "$FILENAME" ]]; then
    continue
  fi

  # Compute MD5 checksum of your file
  ACTUAL_MD5=$(md5sum "$FILENAME" | awk '{print $1}')

  # Compare checksums
  if [[ "$ACTUAL_MD5" == "$EXPECTED_MD5" ]]; then
    echo "$FILENAME: OK"
  else
    echo "$FILENAME: FAILED"
  fi
done < "$MD5_FILE"
