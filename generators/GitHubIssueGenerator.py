import os, sys, json
from github import Github, UnknownObjectException
from generators import AbstractGenerator,ReportGenerator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from datamodel import ResultsAggregator as ra

class GitHubIssueGenerator(AbstractGenerator.AbstractGenerator, ReportGenerator.ReportGenerator):

    header_symbols = {
        f"{ra.ResultsAggregator.failed}": ":red_circle:",
        f"{ra.ResultsAggregator.passed}": ":white_check_mark:",
        f"{ra.ResultsAggregator.skipped}": ":large_blue_circle:",
        f"{ra.ResultsAggregator.ignored}": ":warning:"
    }

    status_symbols = {
        f"{ra.ResultsAggregator.failed}": ":x:",
        f"{ra.ResultsAggregator.passed}": ":white_check_mark:",
        f"{ra.ResultsAggregator.skipped}": ":large_blue_circle:",
        f"{ra.ResultsAggregator.ignored}": ":large_orange_diamond:"
    }

    quality_symbols = {
        f"{ra.ResultsAggregator.failed}": ":red_circle:",
        f"{ra.ResultsAggregator.passed}": ":white_check_mark:",
        f"{ra.ResultsAggregator.ignored}": ":warning:",
    }

    def __init__(self, results_dirs, snapshot=None, branch=None, stage=None, hub_version=None, 
        hub_platform=None, import_version=None, import_platform=None, job_url=None, build_id=None,
        sd_url=None, md_url=None, must_gather_url=None, results_url=None, ignorelist=[], 
        passing_quality_gate=100, executed_quality_gate=100, github_token=os.getenv('GITHUB_TOKEN'), github_org=["open-cluster-management"],
        github_repo=["cicd-staging"], tags=[], dry_run=True, output_file="github.md"):
        self.snapshot = snapshot
        self.branch = branch
        self.stage = stage
        self.hub_version = hub_version
        self.hub_platform = hub_platform
        self.import_version = import_version
        self.import_platform = import_platform
        self.job_url = job_url
        self.build_id = build_id
        self.sd_url = sd_url
        self.md_url = md_url
        self.mg_url = must_gather_url
        self.results_url = results_url
        self.ignorelist = ignorelist
        self.passing_quality_gate = passing_quality_gate
        self.executed_quality_gate = executed_quality_gate
        self.results_files = []
        self.github_token = github_token
        self.github_org = github_org
        self.github_repo = github_repo
        self.tags = tags
        self.dry_run = dry_run
        self.output_file = output_file
        for _results_dir in results_dirs:
            _files_list = os.listdir(_results_dir)
            for _f in _files_list:
                _full_path = os.path.join(_results_dir, _f)
                if os.path.isfile(_full_path) and _full_path.endswith('.xml'):
                    self.results_files.append(_full_path)
        self.aggregated_results = ra.ResultsAggregator(files=self.results_files, ignorelist=ignorelist)

    def generate_subparser(subparser):
        subparser_name = 'gh'
        gh_parser = subparser.add_parser(subparser_name, parents=[ReportGenerator.ReportGenerator.generate_parent_parser()],
            help="Generate a GitHub issue on a given GitHub repo with artifacts from input JUnit XML tests if a failure is detected.")
        gh_parser.add_argument('--github-organization', nargs=1, default=["open-cluster-management"],
            help="GitHub organization to open an issue against if a failing test is detected.  Defaults to open-cluster-management.")
        gh_parser.add_argument('-r', '--repo', nargs=1, default=["backlog"],
            help="GitHub repo to open an issue against if a failing test is detected.  Defaults to 'backlog'.")
        gh_parser.add_argument('--github-token', nargs=1, default=os.getenv('GITHUB_TOKEN'),
            help="GitHub token for access to create GitHub issues.  Pulls from teh GITHUB_TOKEN environment variable if not specified.")
        gh_parser.add_argument('-eg', '--executed-quality-gate', default='100',
            help="Percentage of the test suites that must be executed (not skipped) to count as a quality result.")
        gh_parser.add_argument('-pg', '--passing-quality-gate', default='100',
            help="Percentage of the executed test cases that must pass to count as a quality result.")
        gh_parser.add_argument('-md', '--markdown-url',
            help="URL of the markdown report file artifact associated with this report.")
        gh_parser.add_argument('-sd', '--snapshot-diff-url',
            help="URL of the snapshot diff file artifact associated with this report.")
        gh_parser.add_argument('-ru', '--results-url',
            help="URL of the S3 bucket containing full results artifacts.")
        gh_parser.add_argument('-mg', '--must-gather-url',
            help="URL of the S3 bucket containing must-gather artifacts.")
        gh_parser.add_argument('-o', '--output-file',
            help="If provided - GitHub issue contents will be mirrored to the input filename.")
        gh_parser.add_argument('-dr', '--dry-run', action='store_true',
            help="If provided - an actual GitHub issue will not be created, but the file will be generated, best used with -o.")
        gh_parser.add_argument('-t', '--tags', action='append',
            help="GitHub issue tags to apply to the created issue.  Only applied if the tags exist on the target repository.")
        gh_parser.set_defaults(func=GitHubIssueGenerator.generate_github_issue_from_args)
        return subparser_name, gh_parser

    
    def generate_github_issue_from_args(args):
        _ignorelist = []
        if args.ignore_list is not None and os.path.isfile(args.ignore_list):
            try:
                with open(args.ignore_list, "r+") as f:
                    _il = json.loads(f.read())
                _ignorelist = _il['ignored_tests']
            except json.JSONDecodeError as ex:
                print(f"Ignorelist found in {args.ignore_list} was not in JSON format, ignoring the ignorelist. Ironic.")
        _generator = GitHubIssueGenerator(args.results_directory, snapshot=args.snapshot, branch=args.branch, stage=args.stage,
            hub_version=args.hub_version, hub_platform=args.hub_platform, import_version=args.import_version, import_platform=args.import_platform,
            job_url=args.job_url, build_id=args.build_id, ignorelist=_ignorelist, sd_url=args.snapshot_diff_url,
            md_url=args.markdown_url, executed_quality_gate=int(args.executed_quality_gate), passing_quality_gate=int(args.passing_quality_gate),
            results_url=args.results_url, must_gather_url=args.must_gather_url, github_token=args.github_token, github_org=args.github_organization,
            github_repo=args.repo, tags=args.tags, dry_run=args.dry_run, output_file=args.output_file)
        _message = _generator.open_github_issue()

    
    def open_github_issue(self):
        _message = self.generate_github_issue_body()
        if self.output_file is not None:
            with open(self.output_file, "w+") as f:
                f.write(_message)
        if not self.dry_run:
            try:
                g = Github(self.github_token)
                org = g.get_organization(self.github_org[0])
                repo = org.get_repo(self.github_repo[0])
            except UnknownObjectException as ex:
                print("Failed login to GitHub or find org/repo.  See error below for additional details:")
                print(ex)
                exit(1)
            _tags = []
            if self.tags:
                for tag in self.tags:
                    try:
                        _tags.append(repo.get_label(tag))
                    except UnknownObjectException as ex:
                        print(f"Couldn't find GitHub Tag {tag}, skipping and continuing.")
                        pass
            _issue = repo.create_issue(self.generate_issue_title(), body=_message, labels=_tags)
            print(_issue.html_url)
        else:
            print("--dry-run as been set, skipping git issue creation")
            print(f"GitHub issue would've been created on github.com/{self.github_org[0]}/{self.github_repo[0]}.")
            if self.tags:
                print("We would attempt to apply the following tags:")
                for tag in self.tags:
                    print(f"* {tag}")

    
    def generate_github_issue_body(self):
        # Generate GitHub Issue Test
        _report = ""
        _report = _report + self.generate_header() + "\n"
        _report = _report + self.generate_metadata() + "\n"
        _report = _report + self.generate_summary() + "\n"
        _report = _report + self.generate_body() + "\n"
        # Create GitHub Issue with generated report body
        return _report


    def generate_issue_title(self):
        _header = ""
        if self.branch is not None:
            _header = _header + f"[{self.branch.capitalize()}] "
        _header = _header + f"CICD Canary Build Failure"
        if self.snapshot is not None:
            _header = _header + f" for {self.snapshot}"
        if self.stage is not None:
            _header = _header + f" During the {self.stage.capitalize()} Stage"
        return _header


    def generate_header(self):
        _status = self.aggregated_results.get_status()
        _header = f"# {GitHubIssueGenerator.header_symbols[_status]}"
        if self.snapshot is not None:
            _header = _header + self.snapshot
        _header = _header + f" {_status.capitalize()}"
        if self.stage is not None:
            _header = _header + f" on branch {self.stage.capitalize()}"
        return _header

    
    def generate_metadata(self):
        _metadata = ""
        # Add a link to the CI Job
        if self.job_url is not None:
            _metadata = _metadata + f"## Job URL: {self.job_url}\n"
        if (self.sd_url is not None or self.hub_version is not None or self.import_version is not None
            or self.mg_url is not None or self.results_url is not None):
            _metadata = _metadata + f"## Artifacts & Details\n"
            # Add a link to the s3 buckets for results and must-gather
            if self.mg_url is not None:
                _metadata = _metadata + f"[**Must-Gather Bucket**]({self.mg_url})\n\n"
            if self.results_url is not None:
                _metadata = _metadata + f"[**Results Bucket**]({self.results_url})\n\n"
            # Include a link to the git issue where available
            if self.md_url is not None:
                _metadata = _metadata + f"[**Markdown Report**]({self.md_url})\n\n"
            # Add a link to the snapshot diff
            if self.sd_url is not None:
                _metadata = _metadata + f"[**Snapshot Diff**]({self.sd_url})\n\n"
            # Add hub cluster details where available
            if self.hub_platform is not None and self.hub_version is not None:
                _metadata = _metadata + f"**Hub Cluster Platform:** {self.hub_platform}    **Hub Cluster Version:** {self.hub_version}\n\n"
            elif self.hub_version is not None:
                _metadata = _metadata + f"**Hub Cluster Version:** {self.hub_version}\n\n"
            elif self.hub_platform is not None:
                _metadata = _metadata + f"**Hub Cluster Platform:** {self.hub_platform}\n\n"
            # Add import cluster details where available
            if self.import_platform is not None and self.import_version is not None:
                _metadata = _metadata + f"**Import Cluster Platform:** {self.import_platform}    **Import Cluster Version:** {self.import_version}\n\n"
            elif self.import_version is not None:
                _metadata = _metadata + f"**Import Cluster Version:** {self.import_version}\n\n"
            elif self.import_platform is not None:
                _metadata = _metadata + f"**Import Cluster Platform:** {self.import_platform}\n\n"
        return _metadata


    def generate_summary(self):
        _total, _passed, _failed, _skipped, _ignored = self.aggregated_results.get_counts()
        _percentage_exectued = round(100 - ((_skipped / _total) * 100))
        _percentage_passing = round((_passed / (_total - _skipped)) * 100) # Note - percentage of executed tests, ignoring skipped tests
        # Determine icon for our percentage executed gate
        if _percentage_exectued >= self.executed_quality_gate:
            # Mark with passing if it fully meets quality gates
            _executed_icon = GitHubIssueGenerator.quality_symbols[ra.ResultsAggregator.passed]
        elif _percentage_exectued >= (self.executed_quality_gate * .8):
            # Mark with a warning if 80% of gates or above
            _executed_icon = GitHubIssueGenerator.quality_symbols[ra.ResultsAggregator.ignored]
        else:
            # If less than 80% of quality gate, mark as red
            _executed_icon = GitHubIssueGenerator.quality_symbols[ra.ResultsAggregator.failed]
        # Determine icon for our percentage passing gate
        if _percentage_passing >= self.executed_quality_gate:
            # Mark with passing if it fully meets quality gates
            _passing_icon = GitHubIssueGenerator.quality_symbols[ra.ResultsAggregator.passed]
        elif _percentage_passing >= (self.executed_quality_gate * .8):
            # Mark with a warning if 80% of gates or above
            _passing_icon = GitHubIssueGenerator.quality_symbols[ra.ResultsAggregator.ignored]
        else:
            # If less than 80% of quality gate, mark as red
            _passing_icon = GitHubIssueGenerator.quality_symbols[ra.ResultsAggregator.failed]
        _summary = f"## Quality Gate\n\n"
        _summary = _summary + f"{_executed_icon} **Percentage Executed:** {_percentage_exectued}% ({self.executed_quality_gate}% Quality Gate)\n\n"
        _summary = _summary + f"{_passing_icon} **Percentage Passing:** {_percentage_passing}% ({self.passing_quality_gate}% Quality Gate)\n\n"
        _total, _passed, _failed, _skipped, _ignored = self.aggregated_results.get_counts()
        _summary = _summary + "## Summary\n\n"
        _summary = _summary + f"**{GitHubIssueGenerator.status_symbols[ra.ResultsAggregator.passed]} {_passed} " + ("Test" if _passed == 1 else "Tests") + " Passed**\n\n"
        _summary = _summary + f"**{GitHubIssueGenerator.status_symbols[ra.ResultsAggregator.failed]} {_failed} "  + ("Test" if _failed == 1 else "Tests") + " Failed**\n\n"
        _summary = _summary + f"**{GitHubIssueGenerator.status_symbols[ra.ResultsAggregator.ignored]} {_ignored} " + ("Failure" if _ignored == 1 else "Failures") +  " Ignored**\n\n"
        _summary = _summary + f"**{GitHubIssueGenerator.status_symbols[ra.ResultsAggregator.skipped]} {_skipped} Test " + ("Case" if _skipped == 1 else "Cases") + " Skipped**\n\n"
        return _summary

    
    def generate_body(self):
        _body = "## Failing Tests\n\n"
        _results = self.aggregated_results.get_results()
        for _result in _results:
            if _result['state'] == ra.ResultsAggregator.failed or _result['state'] == ra.ResultsAggregator.ignored:
                _body = _body + f"### {GitHubIssueGenerator.status_symbols[_result['state']]} {_result['testsuite']} -> {_result['name']}\n\n"
                _body = _body + f"```\n{_result['metadata']['message']}\n```\n"
        return _body
    

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
