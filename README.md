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
*Coming Soon*
A "dummy" template for this generator is present, but it doesn't do anything!  You can find it via `python3 reporter.py --help` and its doc via `python3 reporter.py sl --help`.  

### `md`: Markdown Report Generator
*Coming Soon*
A "dummy" template for this generator is present, but it doesn't do anything!  You can find it via `python3 reporter.py --help` and its doc via `python3 reporter.py md --help`.  

### `gh`: GitHub Issue Generator
*Coming Soon*
A "dummy" template for this generator is present, but it doesn't do anything!  You can find it via `python3 reporter.py --help` and its doc via `python3 reporter.py gh --help`.  

### `sd`: Snapshot Diff Generator
This sub-utility generates a "rich diff" between two snapshots.  When sourcing snapshot manifests from github, this utility can pull Commit and PR information for each component that changed between given snapshots.  When sourcing locally, it will provide a summary of modified elements.  You can pull a diff in various formats including JSON, Markdown, Human-Readable Terminal output, and sha-focused diff for `downstream` users.  

You can find the subutility and its cooresponding documentation via:
```
python3 reporter.py sd --help
```
