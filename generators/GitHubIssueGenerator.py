from generators import AbstractGenerator,ReportGenerator

class GitHubIssueGenerator(AbstractGenerator.AbstractGenerator, ReportGenerator.ReportGenerator):

    def generate_subparser(subparser):
        subparser_name = 'gh'
        gh_parser = subparser.add_parser(subparser_name, parents=[ReportGenerator.ReportGenerator.generate_parent_parser()],
            help="Generate a GitHub issue on a given GitHub repo with artifacts from input JUnit XML tests if a failure is detected.")
        gh_parser.add_argument('-r', '--repo', nargs=1,
            help="GitHub repo to open an issue against if a failing test is detected.  Defaults to 'backlog'.")
        gh_parser.add_argument('--github-token', nargs=1,
            help="GitHub token for access to create GitHub issues.  Pulls from teh GITHUB_TOKEN environment variable if not specified.")
        gh_parser.set_defaults(func=GitHubIssueGenerator.generate_github_issue)
        return subparser_name, gh_parser

    
    def generate_github_issue_from_args(args):
        print("GitHub Issue Generation from args")
        print("Printing details of invocation below.\n")
        args_dict = vars(args)
        print(f"Subparser {args.generator_name} called with arguments:")
        for attr in args_dict.keys():
            if attr != "func":
                print(f"\t{attr}: {args_dict[attr]}")


    def generate_github_issue(args):
        print("GitHub Issue Generation")
        print("Printing details of invocation below.\n")
        args_dict = vars(args)
        print(f"Subparser {args.generator_name} called with arguments:")
        for attr in args_dict.keys():
            if attr != "func":
                print(f"\t{attr}: {args_dict[attr]}")
    

# """generate_github_issue.py

# This file will generate a github issue for the current build/results.  It will follow a basic boilerplate.  

# python3 generate_github_issue.py <folder containing xml results> <target github repo> <snapshot> <stage> <platform> <build stage>

# """

# import os, json
# from github import Github
# from helpers import *

# if __name__ == "__main__":

#     if len(sys.argv) < 9:
#         print("""
# Missing arguments!  
# Usage: python3 generate_github_issue.py <folder containing xml results> <target github repo> <snapshot> <stage> <platform> <build stage> <hub-cluster-version> <import-cluster-version>
# """)
#         exit(1)

#     _test_foldername = sys.argv[1]
#     _dest_repo = sys.argv[2]
#     _snapshot = sys.argv[3]
#     _stage = sys.argv[4]
#     _platform = sys.argv[5]
#     _build_stage = sys.argv[6]
#     _hub_cluster_version = sys.argv[7]
#     _import_cluster_version = sys.argv[8]
#     _job_url = ""
#     _ignorelist_filepath = None

#     # Load our ignorelist and related info.
#     _ignorelist_filepath = os.getenv("IGNORELIST_FILEPATH")
#     _ignorelist = []
#     if _ignorelist_filepath is not None:
#         with open(_ignorelist_filepath, "r") as file:
#             _ignorelist=json.load(file)["ignored_tests"]

#     #-----Load our build URL, or a dummy value (and print out a warning if not set)----#
#     try:
#         _url = os.getenv("TRAVIS_BUILD_WEB_URL") if os.getenv("TRAVIS_BUILD_WEB_URL") is not None else "No Job URL"
#         _s3_bucket = os.getenv("RESULTS_S3_BUCKET")
#         _job_id = os.getenv("TRAVIS_BUILD_ID")
#         _job_url = "Job URL: " + _url + "\n"
#     except AttributeError as ex:
#         print("No env var for TRAVIS_BUILD_WEB_URL, skipping printing the URL.", file=sys.stderr)

#     _issue_body = ""
#     _issue = None

#     g = Github(os.getenv("GITHUB_TOKEN"))
#     org = g.get_organization("open-cluster-management")
#     repo = org.get_repo(_dest_repo)

#     if _build_stage == "clean":
#         _issue_body = f"""# Overview

# {_job_url}

# The {_stage} CICD Canary for the snapshot {_snapshot} failed during the {_build_stage} stage.  This is probably an infrastructure issue that CICD needs to resolve.  

# **Hub Cluster Version:** {_hub_cluster_version}, **Import Cluster Version:** {_import_cluster_version}
# """
#         if _job_id != None and _s3_bucket != None:
#             _issue_body = _issue_body + f"""**S3 Bucket for Test Artifacts:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}/?region=us-east-1&tab=overview
# **S3 Bucket for must-gather:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}-must-gather/?region=us-east-1&tab=overview
#             """
#         else:
#             _issue_body = _issue_body + "\n"
#         _issue = repo.create_issue(f"[{_stage.capitalize()}] CICD Canary Build Failure for {_snapshot} During the {_build_stage.capitalize()} Stage",
#             body=_issue_body, assignees=["gurnben", "Kyl-Bempah"],
#             labels=[repo.get_label("infrastructure"), repo.get_label("squad:cicd")])

#     elif _build_stage == "deploy":
#         _issue_body = f"""# Overview

# {_job_url}

# **Hub Cluster Version:** {_hub_cluster_version}, **Import Cluster Version:** {_import_cluster_version}
# """
#         if _job_id != None and _s3_bucket != None:
#             _issue_body = _issue_body + f"""**S3 Bucket for Test Artifacts:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}/?region=us-east-1&tab=overview
# **S3 Bucket for must-gather:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}-must-gather/?region=us-east-1&tab=overview
#             """
#         else:
#             _issue_body = _issue_body + "\n"
        
#         _issue_body = _issue_body + f"""

# The CICD {_stage} Canary for the snapshot {_snapshot} failed during the {_build_stage} stage with the following failing pods:
# """
#         _failing_pods = os.popen(os.path.join(os.path.dirname(os.path.realpath(__file__)), "get_failed_pods.sh")).read()
#         if _failing_pods != "":
#             _issue_body = _issue_body + f"""
# ## Failing Pods
# ```
# {_failing_pods}
# ```
# """
#         else:
#             _issue_body = _issue_body + "\nThere are no failing pods to list, this is likely a malformed snapshot!"
#         _issue = repo.create_issue(f"[{_stage.capitalize()}] CICD Canary Build Failure for {_snapshot} During the {_build_stage.capitalize()} Stage",
#             body=_issue_body,
#             labels=[repo.get_label("blocker (P0)"), repo.get_label("bug"), repo.get_label("canary-failure")])

#     elif _build_stage == "results":
#         _total, _failed, _skipped, _passed, _ignored = get_folder_counts(_test_foldername, _ignorelist)
#         _details = get_folder_details(_test_foldername, _ignorelist)

#         _issue_body = f"""# Overview

# {_job_url}

# **Hub Cluster Version:** {_hub_cluster_version}, **Import Cluster Version:** {_import_cluster_version}
# """
#         if _job_id != None and _s3_bucket != None:
#             _issue_body = _issue_body + f"""**S3 Bucket for Test Artifacts:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}/?region=us-east-1&tab=overview
# **S3 Bucket for must-gather:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}-must-gather/?region=us-east-1&tab=overview
#             """
#         else:
#             _issue_body = _issue_body + "\n"

#         _issue_body = _issue_body + f"""

# The CICD {_stage} Canary for the snapshot {_snapshot} failed during the {_build_stage} stage with the following test failures:
# """
#         if complete_results(_test_foldername):
#             _issue_body = _issue_body + f"""
# We didn't get all of our test results files back, but we do have partial results.  We're showing them below and marking
# as a failure, we recommend checking the job for other critical failures.  
# """
#         _issue_body = _issue_body + f"""

# ## Failed Tests

# """

#         for test in _details:
#             if test["failed"]:
#                 if test["ignored"]:
#                     _issue_body = _issue_body + f"#### :large_orange_diamond: {test['name']}"
#                 else:
#                     _issue_body = _issue_body + f"#### :x: {test['name']}"
#                 _issue_body = _issue_body + f"""

# ```
# {test['message']}
# ```  

# """
#         files_actual, files_expected, files = get_file_counts(_test_foldername)
#         files_string = ""
#         for f in files:
#             files_string = files_string + "* " + f + "\n"
#         files_string = files_string.rstrip()
#         if files_actual < files_expected:
#             for f in files:
#                 _issue_body = _issue_body + f"""#### :x: {files_expected-files_actual}/{files_expected} Results Files Missing

# ```
# {files_expected-files_actual} results files not found, test results from some bins could be missing or reporting skipped.  
# We only recieved the following files:
# {files_string}
# ```

# """
#         _issue = repo.create_issue(f"[{_stage.capitalize()}] CICD Canary Build Failure for {_snapshot} During the {_build_stage.capitalize()} Stage",
#             body=_issue_body,
#             labels=[repo.get_label("blocker (P0)"), repo.get_label("bug"), repo.get_label("canary-failure")])

#     else:        
#         _issue_body = f"""# Overview

# {_job_url}

# **Hub Cluster Version:** {_hub_cluster_version}, **Import Cluster Version:** {_import_cluster_version}
# """

#         if _job_id != None and _s3_bucket != None:
#             _issue_body = _issue_body + f"""**S3 Bucket for Test Artifacts:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}/?region=us-east-1&tab=overview
# **S3 Bucket for must-gather:** https://s3.console.aws.amazon.com/s3/buckets/{_s3_bucket}/data/{_job_id}-must-gather/?region=us-east-1&tab=overview
#             """
#         else:
#             _issue_body = _issue_body + "\n"

#         _issue_body = _issue_body + f"""

# The {_stage} CICD Canary for the snapshot {_snapshot} failed outside of build stages.  This is probably an infrastructure issue that CICD needs to resolve.  
# """
#         _issue = repo.create_issue(f"[{_stage.capitalize()}] CICD Canary Build Failure for {_snapshot} Outside of Stages",
#             body=_issue_body, assignees=["gurnben", "Kyl-Bempah"],
#             labels=[repo.get_label("infrastructure"), repo.get_label("squad:cicd")])
    
#     if _issue is None:
#         print("Issue failed to create, no URL.")
#     else:
#         print(_issue.html_url)
