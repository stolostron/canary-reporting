"""generate_slack_status.py

This file is simple, it forms a very rigid (fragile) script that will turn a JUnit XML and some metadata
into a slack status, either "danger" or "good".  Invoke it as follows:

python3 generate_slack_message.py <xml results folder filepath>

"""

import sys, os, glob, math, untangle, xml
from helpers import *

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("""
Missing arguments!  
Usage: python3 generate_slack_status.py <xml results folder filepath>
""")
        exit(1)

    _test_filename = sys.argv[1]
    exit(get_status(_test_filename))
            