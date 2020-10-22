import os, sys, json
from generators import AbstractGenerator,ReportGenerator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from datamodel import ResultsAggregator

class SlackGenerator(AbstractGenerator.AbstractGenerator, ReportGenerator.ReportGenerator):


    def __init__(self, results_dirs, snapshot=None, branch=None, stage=None, hub_version=None, 
        hub_platform=None, import_version=None, import_platform=None, job_url=None, build_id=None, ignorelist=[]):
        self.snapshot = snapshot
        self.branch = branch
        self.stage = stage
        self.hub_version = hub_version
        self.hub_platform = hub_platform
        self.import_version = import_version
        self.import_platform = import_platform
        self.job_url = job_url
        self.build_id = build_id
        self.ignorelist = ignorelist
        self.results_files = []
        for _results_dir in results_dirs:
            _files_list = os.listdir(_results_dir)
            for _f in _files_list:
                _full_path = os.path.join(_results_dir, _f)
                if os.path.isfile(_full_path) and _full_path.endswith('.xml'):
                    self.results_files.append(_full_path)
        self.aggregated_results = ResultsAggregator.ResultsAggregator(files=self.results_files)
        print(json.dumps(self.aggregated_results.get_raw_results()))


    def generate_subparser(subparser):
        subparser_name = 'sl'
        sl_parser = subparser.add_parser(subparser_name, parents=[ReportGenerator.ReportGenerator.generate_parent_parser()],
            help="Generate a formatted Slack message json payload based on input JUnit XML test results.")
        sl_parser.set_defaults(func=SlackGenerator.generate_slack_report_from_args)
        return subparser_name, sl_parser


    def generate_slack_report_from_args(args):
        # print("Slack Message Generation")
        # print("Printing details of invocation below.\n")
        # args_dict = vars(args)
        # print(f"Subparser {args.generator_name} called with arguments:")
        # for attr in args_dict.keys():
        #     if attr != "func":
        #         print(f"\t{attr}: {args_dict[attr]}")
        _ignorelist = []
        if args.ignore_list is not None and os.path.isfile(args.ignore_list):
            try:
                with open(args.ignore_list, "r+") as f:
                    _il = json.loads(f)
                    _ignorelist = _il['ignored_tests']
            except json.JSONDecodeError as ex:
                print(f"Ignorelist found in {args.ignore_list} was not in JSON format, ignoring the ignorelist. Ironic.")
        _generator = SlackGenerator(args.results_directory, snapshot=args.snapshot, branch=args.branch, stage=args.stage,
            hub_version=args.hub_version, hub_platform=args.hub_platform, import_version=args.import_version, import_platform=args.import_platform,
            job_url=args.job_url, build_id=args.build_id, ignorelist=_ignorelist)



# """generate_slack_message.py

# This file is simple, it forms a very rigid (fragile) script that will turn a JUnit XML and some metadata
# into a nicely formatted slack message.  Invoke it as follows:

# python3 generate_slack_message.py <xml results filepath> <snapshot> <stage> <platform> <issue-url>

# """

# import os, sys, untangle, xml, json
# from helpers import *


# def generate_header(snapshot, stage, platform, job_url, issue_url, status, total, failed, skipped, passed, ignored, 
#     foldername, hub_cluster_version, import_cluster_version, incomplete=False):
#     """This function will generate the header for our slack message.  

#     Params:
#         - snapshot      -   textual representation of the snapshot (pretty printed)
#         - stage         -   string representaiton of the pipeline stage
#         - platform      -   the canary platform
#         - job_url       -   the travis job URL
#         - total         -   the total number of tests run
#         - failed        -   number of failed tests
#         - skipped       -   the number of skipped tests
#         - passed        -   the number of passing tests
#         - incomplete    -   True if results were incomplete
#     """
#     _message = ""
#     if status != 0 and not incomplete:
#         _message = f""":red_circle: *{_snapshot} Failed from {_stage.upper()} on {_platform.upper()}*
# {_job_url}
# *Results Markdown:* https://github.com/open-cluster-management/canary/blob/{stage}/tests/{_snapshot}/results.md
# *Snapshot Diff:* https://github.com/open-cluster-management/canary/blob/{stage}/tests/{_snapshot}/snapshot_diff.md
# *Hub Cluster Version:* {hub_cluster_version}, *Import Cluster Version:* {import_cluster_version}
# {f"*Opened Issue URL:* {issue_url}" if issue_url != "" else ""}

# *Results*
# :white_check_mark: *{_passed} Tests Passed*

# :blue_question: *{_skipped} Tests Skipped*

# :failed: *{_failed} Tests Failed*

# :warning: *{ignored} Test Failure(s) Ignored*
# """
#     elif incomplete:
#         files_actual, files_expected, files = get_file_counts(foldername)
#         files_string = ""
#         for f in files:
#             files_string = files_string + "* " + f + "\n"
#         files_string = files_string.rstrip()
#         _message = f""":red_circle: *{_snapshot} Failed from {_stage.upper()} on {_platform.upper()}*
# {_job_url}
# *Results Markdown:* https://github.com/open-cluster-management/canary/blob/{stage}/tests/{_snapshot}/results.md
# *Snapshot Diff:* https://github.com/open-cluster-management/canary/blob/{stage}/tests/{_snapshot}/snapshot_diff.md
# *Hub Cluster Version:* {hub_cluster_version}, *Import Cluster Version:* {import_cluster_version}
# {f"*Opened Issue URL:* {issue_url}" if issue_url != "" else ""}

# *We didn't get all of our test results files back, but we do have partial results.*  We're showing them below and marking
# as a failure, we recommend checking the job for other critical failures.  

# *We only recieved {files_actual} file(s) back {f"({files_expected-files_actual}/{files_expected} missing)" if files_expected is not None else ""}.  Here are the file(s) we _have_:*
# ```
# {files_string}
# ```

# *Available Results*
# :white_check_mark: *{_passed} Tests Passed*

# :blue_question: *{_skipped} Tests Skipped*

# :failed: *{_failed} Tests Failed*

# :warning: *{ignored} Test Failure(s) Ignored*
# """
#     else:
#         _message = f""":green-circle: *{_snapshot} Passed from {_stage.upper()} on {_platform.upper()}*
# {_job_url}
# *Results Markdown:* https://github.com/open-cluster-management/canary/blob/{stage}/tests/{_snapshot}/results.md
# *Snapshot Diff:* https://github.com/open-cluster-management/canary/blob/{stage}/tests/{_snapshot}/snapshot_diff.md
# *Hub Cluster Version:* {hub_cluster_version}, *Import Cluster Version:* {import_cluster_version}

# *Results*
# :white_check_mark: *{_passed} Tests Passed*

# :blue_question: *{_skipped} Tests Skipped*

# :failed: *{_failed} Tests Failed*

# :warning: *{ignored} Test Failure(s) Ignored*
# """
#     return _message


# def generate_content(_total, _failed, _skipped, _passed, _ignored, _details):
#     """Generate the testing content for the slack message - a summary of any and all test failures.  
    
#     Params:
#         - _total    -   The total number of tests
#         - _failed   -   The total number of failed tests
#         - _skipped  -   The total number of skipped tests
#         - _passed   -   The total number of passed tests
#         - _details  -   A list of dicts defining test results
#     """
#     if _failed > 0:
#         _output = """
# *Failing Tests*
# """
#         for test in _details:
#             if test["failed"]:
#                 if test["ignored"]:
#                     _output = _output + f":warning: - {test['name']}"
#                 else:
#                     _output = _output + f":failed: - {test['name']}"
#                 _output = _output + f"""
# ```
# {test["message"]}
# ```
# """
#         if len(_output) > 3000:
#             _output = ""
#             for test in _details:
#                 if test["failed"]:
#                     if test["ignored"]:
#                         _output = _output + f":warning: - {test['name']}\n"
#                     else:
#                         _output = _output + f":failed: - {test['name']}\n"
#             if len(_output) > 3400:
#                 _output = ""
#         return _output
#     else:
#         return ""


# if __name__ == "__main__":

#     if len(sys.argv) < 9:
#         print("""
# Missing arguments!  
# Usage: python3 generate_slack_message.py <folder containing xml results> <target filepath> <snapshot> <stage> <platform> <issue-url> <hub-cluster-version> <import-cluster-version>
# """)
#         exit(1)

#     test_results = None

#     _test_foldername = sys.argv[1]
#     _dest_filename = sys.argv[2]
#     _snapshot = sys.argv[3]
#     _stage = sys.argv[4]
#     _platform = sys.argv[5]
#     _issue_url = sys.argv[6]
#     _hub_cluster_version = sys.argv[7]
#     _import_cluster_version = sys.argv[8]
#     _job_url = ""
#     _ignorelist_filepath = None

#     _url = os.getenv("TRAVIS_BUILD_WEB_URL") if os.getenv("TRAVIS_BUILD_WEB_URL") is not None else "No Job URL"
#     _job_url = "*Job URL:* " + _url + "\n"

#     _ignorelist_filepath = os.getenv("IGNORELIST_FILEPATH")
#     _ignorelist = []

#     if _ignorelist_filepath is not None:
#         with open(_ignorelist_filepath, "r") as file:
#             _ignorelist=json.load(file)["ignored_tests"]

#     _total, _failed, _skipped, _passed, _ignored = get_folder_counts(_test_foldername, _ignorelist)
#     _details = get_folder_details(_test_foldername, _ignorelist)
#     _status = get_status(_test_foldername, _ignorelist)

#     _message = ('{"text": "' 
#         + generate_header(_snapshot, _stage, _platform, _job_url, _issue_url, _status, _total, _failed, _skipped, _passed, _ignored, _test_foldername, _hub_cluster_version, _import_cluster_version, incomplete=complete_results(_test_foldername)).replace('"', '\\\"') 
#         + generate_content(_total, _failed, _skipped, _passed, _ignored, _details).replace('"', '\\\"') + '"}')
#     with open(_dest_filename, "w+") as dest:
#         dest.write(_message.replace("\n", "\\n").replace("\\\\\"", "\\\"")) # Necessary to make JSON-safe, we have to un-escape doubly escaped quotes!
