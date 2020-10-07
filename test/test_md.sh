#!/bin/bash

# test_md.sh
#   This script will generate test markdown files from each of our test cases.
#

# Find the directory we're in (used to reference other scripts)
my_dir=$(dirname $(readlink -f $0))

# Make the results dir if it doesn't exist
if [ ! -d $my_dir/results ]; then mkdir $my_dir/results; fi

# Run the generate_md script on each test_results file.
echo "-----Generating Markdown Files-----"
for file in test/*/; do
    if [[ $file != "test/results/" ]]; then
        echo "Generating MD report for: $file"
        python3 $my_dir/../generate_md.py $file $my_dir/results/md_$(basename $file .xml).md SOME_SNAPSHOT integration aws
    fi
done;
echo "-----Done Generating Markdown Files-----"
