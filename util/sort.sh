#!/bin/bash

for input_file in "./datasets/original"/hetero_test_file*.txt; do
    filename=$(basename -- "$input_file")
    output_file="./datasets/sorted/sorted_$filename"

    awk 'NR==1 {print $0} NR>1' "$input_file" | sort -n -k8,8 | \
    awk 'BEGIN {OFS=" "} NR==1 {print $0} NR>1 { $1=NR-1; print $0 }' > "$output_file"
done