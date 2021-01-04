import os, sys, json
from generators import AbstractGenerator,ReportGenerator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from datamodel import ResultsAggregator as ra

class MarkdownGenerator(AbstractGenerator.AbstractGenerator, ReportGenerator.ReportGenerator):
    
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
        sd_url=None, issue_url=None, ignorelist=[], passing_quality_gate=100, executed_quality_gate=100):
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
        subparser_name = 'md'
        md_parser = subparser.add_parser(subparser_name, parents=[ReportGenerator.ReportGenerator.generate_parent_parser()],
            help="Generate a formatted markdown summary report based on input JUnit XML test results.")
        md_parser.add_argument('-eg', '--executed-quality-gate', default='100',
            help="Percentage of the test suites that must be executed (not skipped) to count as a quality result.")
        md_parser.add_argument('-pg', '--passing-quality-gate', default='100',
            help="Percentage of the executed test cases that must pass to count as a quality result.")
        md_parser.add_argument('-sd', '--snapshot-diff-url',
            help="URL of the snapshot diff file artifact associated with this report.")
        md_parser.add_argument('-iu', '--issue-url',
            help="URL of the github/jira/tracking issue associated with this report.")
        md_parser.add_argument('-o', '--output-file',
            help="Destination file for slack message.  Message will be output to stdout if left blank.")
        md_parser.set_defaults(func=MarkdownGenerator.generate_markdown_report_from_args)
        return subparser_name, md_parser


    def generate_markdown_report_from_args(args):
        _ignorelist = []
        if args.ignore_list is not None and os.path.isfile(args.ignore_list):
            try:
                with open(args.ignore_list, "r+") as f:
                    _il = json.loads(f.read())
                _ignorelist = _il['ignored_tests']
            except json.JSONDecodeError as ex:
                print(f"Ignorelist found in {args.ignore_list} was not in JSON format, ignoring the ignorelist. Ironic.")
        _generator = MarkdownGenerator(args.results_directory, snapshot=args.snapshot, branch=args.branch, stage=args.stage,
            hub_version=args.hub_version, hub_platform=args.hub_platform, import_version=args.import_version, import_platform=args.import_platform,
            job_url=args.job_url, build_id=args.build_id, ignorelist=_ignorelist, sd_url=args.snapshot_diff_url,
            issue_url=args.issue_url, executed_quality_gate=int(args.executed_quality_gate), passing_quality_gate=int(args.passing_quality_gate))
        _message = _generator.generate_markdown_report()
        if args.output_file is not None:
            with open(args.output_file, "w+") as f:
                f.write(_message)
        else:
            print(_message)

    
    def generate_markdown_report(self):
        _report = ""
        _report = _report + self.generate_header() + "\n"
        _report = _report + self.generate_metadata() + "\n"
        _report = _report + self.generate_summary() + "\n"
        _report = _report + self.generate_table() + "\n"
        _report = _report + self.generate_body() + "\n"
        return _report


    def generate_header(self):
        _status = self.aggregated_results.get_status()
        _header = f"# {MarkdownGenerator.header_symbols[_status]}"
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
        if self.sd_url is not None or self.hub_version is not None or self.import_version is not None or self.issue_url is not None:
            _metadata = _metadata + f"## Artifacts & Details\n"
            # Add a link to the snapshot diff
            if self.sd_url is not None:
                _metadata = _metadata + f"[**Snapshot Diff**]({self.sd_url})\n\n"
            # Include a link to the git issue where available
            if self.issue_url is not None:
                _metadata = _metadata + f"[**Opened Issue**]({self.issue_url})\n\n"
            # Add a hub + import verion where available
            if self.hub_version is not None and self.import_version is not None:
                _metadata = _metadata + f"**Hub Cluster Version:** {self.hub_version}\n\n**Import Cluster Version:** {self.import_version}\n\n"
            elif self.hub_version is not None:
                _metadata = _metadata + f"**Hub Cluster Version:** {self.hub_version}\n\n"
            elif self.import_version is not None:
                _metadata = _metadata + f"**Import Cluster Version:** {self.import_version}\n\n"
        return _metadata


    def generate_summary(self):
        _total, _passed, _failed, _skipped, _ignored = self.aggregated_results.get_counts()
        _percentage_exectued = round(100 - ((_skipped / _total) * 100))
        _percentage_passing = round((_passed / (_total - _skipped)) * 100) # Note - percentage of executed tests, ignoring skipped tests
        # Determine icon for our percentage executed gate
        if _percentage_exectued >= self.executed_quality_gate:
            # Mark with passing if it fully meets quality gates
            _executed_icon = MarkdownGenerator.quality_symbols[ra.ResultsAggregator.passed]
        elif _percentage_exectued >= (self.executed_quality_gate * .8):
            # Mark with a warning if 80% of gates or above
            _executed_icon = MarkdownGenerator.quality_symbols[ra.ResultsAggregator.ignored]
        else:
            # If less than 80% of quality gate, mark as red
            _executed_icon = MarkdownGenerator.quality_symbols[ra.ResultsAggregator.failed]
        # Determine icon for our percentage passing gate
        if _percentage_passing >= self.executed_quality_gate:
            # Mark with passing if it fully meets quality gates
            _passing_icon = MarkdownGenerator.quality_symbols[ra.ResultsAggregator.passed]
        elif _percentage_passing >= (self.executed_quality_gate * .8):
            # Mark with a warning if 80% of gates or above
            _passing_icon = MarkdownGenerator.quality_symbols[ra.ResultsAggregator.ignored]
        else:
            # If less than 80% of quality gate, mark as red
            _passing_icon = MarkdownGenerator.quality_symbols[ra.ResultsAggregator.failed]
        _summary = f"## Quality Gate\n\n"
        _summary = _summary + f"{_executed_icon} **Percentage Executed:** {_percentage_exectued}% ({self.executed_quality_gate}% Quality Gate)\n\n"
        _summary = _summary + f"{_passing_icon} **Percentage Passing:** {_percentage_passing}% ({self.passing_quality_gate}% Quality Gate)\n\n"
        _total, _passed, _failed, _skipped, _ignored = self.aggregated_results.get_counts()
        _summary = _summary + "## Summary\n\n"
        _summary = _summary + f"**{MarkdownGenerator.status_symbols[ra.ResultsAggregator.passed]} {_passed} " + ("Test" if _passed == 1 else "Tests") + " Passed**\n\n"
        _summary = _summary + f"**{MarkdownGenerator.status_symbols[ra.ResultsAggregator.failed]} {_failed} "  + ("Test" if _failed == 1 else "Tests") + " Failed**\n\n"
        _summary = _summary + f"**{MarkdownGenerator.status_symbols[ra.ResultsAggregator.ignored]} {_ignored} " + ("Failure" if _ignored == 1 else "Failures") +  " Ignored**\n\n"
        _summary = _summary + f"**{MarkdownGenerator.status_symbols[ra.ResultsAggregator.skipped]} {_skipped} Test " + ("Case" if _skipped == 1 else "Cases") + " Skipped**\n\n"
        return _summary

    def generate_table(self):
        _table = "## Test Case Summary\n\n"
        _table = _table + "|Results|Testsuite|Test|\n"
        _table = _table + "|---|---|---|\n"
        _results = self.aggregated_results.get_results()
        for _result in _results:
            _table = _table + f"| {MarkdownGenerator.status_symbols[_result['state']]} | {_result['testsuite']} | {_result['name']} |\n"
        return _table

    
    def generate_body(self):
        _body = "## Failing Tests\n\n"
        _results = self.aggregated_results.get_results()
        for _result in _results:
            if _result['state'] == ra.ResultsAggregator.failed or _result['state'] == ra.ResultsAggregator.ignored:
                _body = _body + f"### {MarkdownGenerator.status_symbols[_result['state']]} {_result['testsuite']} -> {_result['name']}\n\n"
                _body = _body + f"```\n{_result['metadata']['message']}\n```\n"
        return _body
 
