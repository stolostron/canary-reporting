#!/bin/bash

# test_slack.sh
#   This script will generate test slack message files from each of our test cases.
#

# Find the directory we're in (used to reference other scripts)
my_dir=$(dirname $(readlink -f $0))

# Make the results dir if it doesn't exist
if [ ! -d $my_dir/results ]; then mkdir $my_dir/results; fi

# Run the generate_slack_message script on each test_results file.
echo "-----Generating Slack Message Files-----"
for file in test/*/; do
    if [[ $file != "test/results/" ]]; then
        echo "Generating Slack message for: $file"
        python3 $my_dir/../generate_slack_message.py $file $my_dir/results/slack_$(basename $file .xml).json SOME_SNAPSHOT integration aws ""
    fi
done;
echo "-----Done Generating Slack Message Files-----"
