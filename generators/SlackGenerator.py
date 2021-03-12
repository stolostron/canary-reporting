"""SlackGenerator

An AbstractGenerator and ReportGenerator implementation to generate a slack message JSON payload as part of the canary reporting CLI.  
This class can generate its CLI parser, load args, generate a ResultsAggregator object, and format the output data as a Slack JSON payload. 
"""

import os, sys, json, argparse
from generators import AbstractGenerator,ReportGenerator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from datamodel import ResultsAggregator as ra

class SlackGenerator(AbstractGenerator.AbstractGenerator, ReportGenerator.ReportGenerator):

    header_symbols = {
        f"{ra.ResultsAggregator.failed}": ":red_circle:",
        f"{ra.ResultsAggregator.passed}": ":green-circle:",
        f"{ra.ResultsAggregator.skipped}": ":large_blue_circle:",
        f"{ra.ResultsAggregator.ignored}": ":yellow_jenkins_circle:"
    }

    status_symbols = {
        f"{ra.ResultsAggregator.failed}": ":failed:",
        f"{ra.ResultsAggregator.passed}": ":white_check_mark:",
        f"{ra.ResultsAggregator.skipped}": ":blue_question:",
        f"{ra.ResultsAggregator.ignored}": ":warning:"
    }

    quality_symbols = {
        f"{ra.ResultsAggregator.failed}": ":red_jenkins_circle:",
        f"{ra.ResultsAggregator.passed}": ":green_jenkins_circle:",
        f"{ra.ResultsAggregator.ignored}": ":yellow_jenkins_circle:",
    }

    def __init__(self, results_dirs, snapshot=None, branch=None, stage=None, hub_version=None, 
        hub_platform=None, import_cluster_details=[], job_url=None, build_id=None,
        md_url=None, sd_url=None, issue_url=None, ignorelist=[], passing_quality_gate=100, executed_quality_gate=100):
        """Create a SlackGenerator Object, unroll xml files from input, and initialize a ResultsAggregator.  

        Required Arguments:
        results_dirs    -- a list of directories that contain XML files from which to generate an aggregate report

        Keyword Arguments:
        snapshot    --  a string representation of the snapshot that these test results represent, ex. 2.2.0-SNAPSHOT-timestamp
        branch      --  a string representaiton of the integration test branch that generated the xml results, ex. 2.2-integration
        stage       --  a string representaiton of the integration test stage/step that generated the xml results, ex deploy
        hub_version     --  a string representation of the hub cluster version that was tested
        hub_platform    --  a string representation of the hub cluster's hosting cloud platform
        import_version  --  a string representation of the import cluster version that was tested
        import_platform --  a string representation of the import cluster's hosting cloud platform
        job_url     --  the URL of the CI job that produced this JUnit XML, ex. $TRAVIS_BUILD_WEB_URL
        build_id    --  CI build id (unique identifier) that produced this JUnit XML, ex. $TRAVIS_BUILD_ID
        md_url      --  the URL of any hosted md report generated previously from this XML
        sd_url      --  the URL of any snapshot diff report generated previously for this snapshot
        issue_url   --  the URL of any opened git issue related to this JUnit XML
        ignorelist  --  a list of dicts contianing "name", "squad", and "owner" keys
        passing_quality_gate    --  a number between 0 and 100 that defines the percentage of tests that must pass to declare success
        executed_quality_gate   --  a number between 0 and 100 that defines the percentage of tests that must be executed to declare success
        """
        self.snapshot = snapshot
        self.branch = branch
        self.stage = stage
        self.hub_version = hub_version
        self.hub_platform = hub_platform
        self.import_cluster_details = import_cluster_details
        self.job_url = job_url
        self.build_id = build_id
        self.md_url = md_url
        self.sd_url = sd_url
        self.issue_url = issue_url
        self.ignorelist = ignorelist
        self.passing_quality_gate = passing_quality_gate
        self.executed_quality_gate = executed_quality_gate
        self.results_files = []
        for _results_dir in results_dirs:
            _files_list = os.listdir(_results_dir)
            for _f in _files_list:
                _full_path = os.path.join(_results_dir, _f)
                if os.path.isfile(_full_path) and _full_path.endswith('.xml'):
                    self.results_files.append(_full_path)
        self.aggregated_results = ra.ResultsAggregator(files=self.results_files, ignorelist=ignorelist)


    def generate_subparser(subparser):
        """Static method to generate a subparser for the SlackGenerator module.  

        Required Argument:
        subparser -- an argparse.ArgumentParser object to extend with a new subparser.  
        """
        subparser_name = 'sl'
        sl_parser = subparser.add_parser(subparser_name, parents=[ReportGenerator.ReportGenerator.generate_parent_parser()],
            help="Generate a formatted Slack message json payload based on input JUnit XML test results.",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog="""
Example Usages:

    Generate a slack report from the JUnit xml in the 'juint_xml' folder and save it locally to 'out.json':
        python3 reporter.py md junit_xml/ -o out.json
""")
        sl_parser.add_argument('-eg', '--executed-quality-gate', default='100',
            help="Percentage of the test suites that must be executed (not skipped) to count as a quality result.")
        sl_parser.add_argument('-pg', '--passing-quality-gate', default='100',
            help="Percentage of the executed test cases that must pass to count as a quality result.")
        sl_parser.add_argument('-md', '--markdown-url',
            help="URL of the markdown report file artifact associated with this report.")
        sl_parser.add_argument('-sd', '--snapshot-diff-url',
            help="URL of the snapshot diff file artifact associated with this report.")
        sl_parser.add_argument('-iu', '--issue-url',
            help="URL of the github/jira/tracking issue associated with this report.")
        sl_parser.add_argument('-o', '--output-file',
            help="Destination file for slack message.  Message will be output to stdout if left blank.")
        sl_parser.set_defaults(func=SlackGenerator.generate_slack_report_from_args)
        return subparser_name, sl_parser


    def generate_slack_report_from_args(args):
        """Static method to create a SlackGenerator object and generate a slack report from the command-line args.

        Required Argument:
        args -- argparse-generated arguments from an argparse with a parser generated by SlackGenerator.generate_subparser()
        """
        _ignorelist = []
        if args.ignore_list is not None and os.path.isfile(args.ignore_list):
            try:
                with open(args.ignore_list, "r+") as f:
                    _il = json.loads(f.read())
                _ignorelist = _il['ignored_tests']
            except json.JSONDecodeError as ex:
                print(f"Ignorelist found in {args.ignore_list} was not in JSON format, ignoring the ignorelist. Ironic.")
        _import_cluster_details = []
        if args.import_cluster_details_file is not None and os.path.isfile(args.import_cluster_details_file):
            try:
                with open(args.import_cluster_details_file, "r+") as f:
                    _import_cluster_details = json.loads(f.read())
            except json.JSONDecodeError as ex:
                print(f"Import cluster details found in {args.import_cluster_details_file} was not in JSON format, ignoring.")
        elif args.import_version or args.import_platform:
            _import_cluster = {
                "clustername": ""
            }
            _import_cluster["version"] = args.import_version if args.import_version else ""
            _import_cluster["platform"] = args.import_platform if args.import_platform else ""
            _import_cluster_details.append(_import_cluster)
        _generator = SlackGenerator(args.results_directory, snapshot=args.snapshot, branch=args.branch, stage=args.stage,
            hub_version=args.hub_version, hub_platform=args.hub_platform, import_cluster_details=_import_cluster_details,
            job_url=args.job_url, build_id=args.build_id, ignorelist=_ignorelist, md_url=args.markdown_url, sd_url=args.snapshot_diff_url,
            issue_url=args.issue_url, executed_quality_gate=int(args.executed_quality_gate), passing_quality_gate=int(args.passing_quality_gate))
        _message = {
            "text": _generator.generate_slack_report()
        }
        if args.output_file is not None:
            with open(args.output_file, "w+") as f:
                f.write(json.dumps(_message))
        else:
            print(json.dumps(_message))

    
    def generate_slack_report(self):
        """Macro function to assemble our slack report.  This wraps the header, metadata, summary, and body generation with a neat bow."""
        _report = ""
        _report = _report + self.generate_header() + "\n"
        _report = _report + self.generate_metadata() + "\n"
        _report = _report + self.generate_summary() + "\n"
        _full_body = self.generate_body_full()
        if (len(_report) + len(_full_body)) < 4000:
            _report = _report + _full_body
        else:
            _short_body = self.generate_body_short()
            if (len(_report) + len(_short_body)) < 4000:
                _report = _report + _short_body
            # else - all body tests are too long, skip it
        return _report


    def generate_header(self):
        """Generates a header string for our slack message in correct slack format, handling with any combination of optional vars."""
        _status = self.aggregated_results.get_status()
        _header = f"{SlackGenerator.header_symbols[_status]}"
        if self.snapshot is not None:
            _header = _header + self.snapshot
        _header = _header + f" {_status.capitalize()}"
        if self.stage is not None:
            _header = _header + f" on branch {self.stage.capitalize()}"
        return f"*{_header}*"

    
    def generate_metadata(self):
        """Generates a metadata string for our slack message containing all links and metadata given in optional vars."""
        _metadata = ""
        # Add a link to the CI Job
        if self.job_url is not None:
            _metadata = _metadata + f"*Job URL:* {self.job_url}\n"
        # Add a link to the markdown report
        if self.md_url is not None:
            _metadata = _metadata + f"*Results Markdown:* {self.md_url}\n"
        # Add a link to the snapshot diff
        if self.sd_url is not None:
            _metadata = _metadata + f"*Snapshot Diff:* {self.sd_url}\n"
        # Add hub cluster details where available
        if self.hub_platform is not None and self.hub_version is not None:
            _metadata = _metadata + f"*Hub Cluster Platform:* {self.hub_platform}    *Hub Cluster Version:* {self.hub_version}\n\n"
        elif self.hub_version is not None:
            _metadata = _metadata + f"*Hub Cluster Version:* {self.hub_version}\n\n"
        elif self.hub_platform is not None:
            _metadata = _metadata + f"*Hub Cluster Platform:* {self.hub_platform}\n\n"
        # Add import cluster details where available
        if len(self.import_cluster_details) > 0:
            _metadata = _metadata + f"*Import Cluster(s):*\n"
        for import_cluster in self.import_cluster_details:
            if import_cluster['platform'] is not None and import_cluster["version"] is not None:
                _metadata = _metadata + f"• *Import Cluster Platform:* {import_cluster['platform']}    *Import Cluster Version:* {import_cluster['version']}\n"
            elif import_cluster['version'] is not None:
                _metadata = _metadata + f"• *Import Cluster Version:* {import_cluster['version']}\n"
            elif import_cluster['platform']:
                _metadata = _metadata + f"• *Import Cluster Platform:* {import_cluster['platform']}\n"
        _metadata = _metadata + "\n"
        # Include a link to the git issue where available
        if self.issue_url is not None:
            _metadata = _metadata + f"*Opened Issue URL:* {self.issue_url}\n"
        return _metadata


    def generate_summary(self):
        """Generates a summary of our test results including gating percentages and pass/fail/skip/ignored results as available."""
        _total, _passed, _failed, _skipped, _ignored = self.aggregated_results.get_counts()
        _percentage_exectued = round(100 - ((_skipped / _total) * 100))
        _percentage_passing = round((_passed / (_total - _skipped)) * 100) # Note - percentage of executed tests, ignoring skipped tests
        if _percentage_exectued >= self.executed_quality_gate and _percentage_passing >= self.passing_quality_gate:
            # Mark with passing if it fully meets quality gates
            _quality_icon = SlackGenerator.quality_symbols[ra.ResultsAggregator.passed]
        elif _percentage_exectued >= (self.executed_quality_gate * .8) and _percentage_passing >= (self.passing_quality_gate * .8):
            # Mark with a warning if 80% of gates or above
            _quality_icon = SlackGenerator.quality_symbols[ra.ResultsAggregator.ignored]
        else:
            # If less than 80% of quality gate, mark as red
            _quality_icon = SlackGenerator.quality_symbols[ra.ResultsAggregator.failed]
        _summary = f"*Quality Gate ({self.executed_quality_gate}% - {self.passing_quality_gate}%):*\n"
        _summary = _summary + f"{_quality_icon}*{_percentage_exectued}% Executed - {_percentage_passing}% Passing*\n\n"
        _summary = _summary + "*Results:*\n"
        _summary = _summary + f"*{SlackGenerator.status_symbols[ra.ResultsAggregator.passed]} {_passed} " + ("Test" if _passed == 1 else "Tests") + " Passed*\n"
        _summary = _summary + f"*{SlackGenerator.status_symbols[ra.ResultsAggregator.failed]} {_failed} "  + ("Test" if _failed == 1 else "Tests") + " Failed*\n"
        _summary = _summary + f"*{SlackGenerator.status_symbols[ra.ResultsAggregator.ignored]} {_ignored} " + ("Failure" if _ignored == 1 else "Failures") +  " Ignored*\n"
        _summary = _summary + f"*{SlackGenerator.status_symbols[ra.ResultsAggregator.skipped]} {_skipped} Test " + ("Case" if _skipped == 1 else "Cases") + " Skipped*\n"
        return _summary

    
    def generate_body_full(self):
        """Generates a full slack results body - this edition of the slack message body includes console output for failing test cases."""
        _body = ""
        if self.aggregated_results.get_status() == ra.ResultsAggregator.failed:
            _body = "*Failing Tests*\n"
            _results = self.aggregated_results.get_results()
            for _result in _results:
                if _result['state'] == ra.ResultsAggregator.failed:
                    _body = _body + f"{SlackGenerator.status_symbols[_result['state']]} {_result['testsuite']} -> {_result['name']}\n"
                    _body = _body + f"```{_result['metadata']['message']}```\n"
        return _body


    def generate_body_short(self):
        """Generates a shortened slack message results body - this edition omits error messages for failing test cases and only includes the case name."""
        _body = ""
        if self.aggregated_results.get_status() == ra.ResultsAggregator.failed:
            _body = "*Failing Tests*\n"
            _results = self.aggregated_results.get_results()
            for _result in _results:
                if _result['state'] == ra.ResultsAggregator.failed:
                    _body = _body + f"{SlackGenerator.status_symbols[_result['state']]} {_result['testsuite']} -> {_result['name']}\n"
        return _body

