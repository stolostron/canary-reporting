import os, sys, json, db_utils
import pymysql
from github import Github, UnknownObjectException
from datetime import datetime

# Aligns all defects recorded in database with their github status

TABLE_NAME = "canary_issues"
c = None
conn = None
github_token=os.getenv('GITHUB_TOKEN')
github_org=os.getenv('GITHUB_ORG')
github_repo=os.getenv('GITHUB_REPO')
days_grace=os.getenv('CANARY_DEDUP_GRACE_DAYS')
if days_grace == None:
    days_grace = 2

def query_github_status(defect):
    try:
        issue_state = repo.get_issue(defect).state
    except UnknownObjectException:
        issue_state = None
    return issue_state

#
# Do we have the things we need?
#
if github_token == None:
    print("Required environment variable GITHUB_TOKEN missing")
    exit(1)
if github_org == None:
    print("Required environment variable GITHUB_ORG missing (likely candidate: open-cluster-management)")
    exit(1)
if github_repo == None:
    print("Required environment variable GITHUB_REPO missing (likely candidates: backlog or canary-staging)")
    exit(1)

#
# Get conneted to the Database
#
ret = db_utils.connect_to_db()

#
# Get connected to GitHub
#
github_token=os.getenv('GITHUB_TOKEN')
try:
    g = Github(github_token)
    org = g.get_organization(github_org)
    repo = org.get_repo(github_repo)
except UnknownObjectException as ex:
    print(ex)
    exit(1)

print("Connected to {}/{}, pulling defects with grace period of {} days".format(github_org,github_repo,days_grace))
ret = db_utils.pull_open_defects(github_repo, days_grace)
if ret != None:
    open_defects = list(ret)
    print("{} open defects in the database, checking for GitHub status".format(len(open_defects)))
    changed = False
    for row in open_defects:
        id = list(row)[0]
        defect = list(row)[1]
        status = query_github_status(int(defect))
        if (status != "open") and (status != None):
            rc = db_utils.update_status(id, status, github_repo)
            print("Updating defect {} to status {} returns: {}".format(defect,status,rc))
            if rc == 1:
                changed = True
    if changed == False:
        print("No changes made.")
    print("Processing complete.")
else:
    print("No open defects!")
ret = db_utils.disconnect_from_db()
