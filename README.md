# ACM/OCM Canary Reporting

Reporting logic for the ACM/OCM canary process in one converged python project!  This project includes a number of command-line subutilities to generate various reports based on JUnit XML test results and manifest files.  

## Install

Install dependencies via:
```
pip install -r requirements.txt
```

## Test

Run tests via:
```
python3 -m unittest
```

## Sub-Utilities & Use

### `sl`: Slack Message Generator
This sub-utility generates a Slack report file summarizing the failures detected in a bundle of JUnit XML files.  It will consolidate the XML files into a single datastructure, detect metadata if possible, and generate the slack message json payload.

You can find the subutility and its cooresponding documentation via:
```
python3 reporter.py sl --help
```

### `md`: Markdown Report Generator
This sub-utility generates a MD report file summarizing the failures detected in a bundle of JUnit XML files.  It will consolidate the XML files into a single datastructure, detect metadata if possible, and generate the text, tables, etc. 

You can find the subutility and its cooresponding documentation via:
```
python3 reporter.py md --help
```

### `gh`: GitHub Issue Generator
This sub-utility generates a GitHub issue summarizing the failures detected in a bundle of JUnit XML files.  It will consolidate the XML files into a single datastructure, detect metadata if possible, and generate the text and any metadata for a git issue (tagging, etc) and optionally create the git issue for you.  

You can find the subutility and its cooresponding documentation via:
```
python3 reporter.py gh --help
```

### `js`: JSON Data Generator
This sub-utility generates a raw JSON dump of the datamodel from our reporting logic - this is a raw JSON formatted and processed payload generated from a bundle of JUnit XML results files.  It will consolidate the XML files into a single datastructure, detect metadata if possible, and dump the datamodel and associated metadata from the results in JSON format.  

You can find the subutility and its cooresponding documentation via:
```
python3 reporter.py js --help
```

### `sd`: Snapshot Diff Generator
This sub-utility generates a "rich diff" between two snapshots.  When sourcing snapshot manifests from github, this utility can pull Commit and PR information for each component that changed between given snapshots.  When sourcing locally, it will provide a summary of modified elements.  You can pull a diff in various formats including JSON, Markdown, Human-Readable Terminal output, and sha-focused diff for `downstream` users.  

You can find the subutility and its cooresponding documentation via:
```
python3 reporter.py sd --help
```
