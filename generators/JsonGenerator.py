"""JsonGenerator

An AbstractGenerator and ReportGenerator implementation to generate a raw JSON payload as part of the canary reporting CLI.  
This class can generate its CLI parser, load args, generate a ResultsAggregator object, and format the output data as a raw JSON payload. 
"""

import os, sys, json, argparse
from generators import AbstractGenerator,ReportGenerator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from datamodel import ResultsAggregator as ra

class JsonGenerator(AbstractGenerator.AbstractGenerator, ReportGenerator.ReportGenerator):

    def __init__(self, results_dirs, snapshot=None, branch=None, stage=None, hub_version=None, 
        hub_platform=None, import_version=None, import_platform=None, job_url=None, build_id=None,
        issue_url=None, ignorelist=[], passing_quality_gate=100, executed_quality_gate=100):
        """Create a JsonGenerator Object, unroll xml files from input, and initialize a ResultsAggregator.  

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
        self.import_version = import_version
        self.import_platform = import_platform
        self.job_url = job_url
        self.build_id = build_id
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
        """Static method to generate a subparser for the JsonGenerator module.  

        Required Argument:
        subparser -- an argparse.ArgumentParser object to extend with a new subparser.  
        """
        subparser_name = 'js'
        md_parser = subparser.add_parser(subparser_name, parents=[ReportGenerator.ReportGenerator.generate_parent_parser()],
            help="Generate a JSON file containing raw test results and metadata about the canary run.",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog="""
Example Usage:

    Generate a parsed and processed JSON representation of the JUnit results in the 'junit_xml' folder and output it to 'out.json':
        python3 reporter.py js junit_xml/ -o out.json    
""")
        md_parser.add_argument('-eg', '--executed-quality-gate', default='100',
            help="Percentage of the test suites that must be executed (not skipped) to count as a quality result.")
        md_parser.add_argument('-pg', '--passing-quality-gate', default='100',
            help="Percentage of the executed test cases that must pass to count as a quality result.")
        md_parser.add_argument('-iu', '--issue-url',
            help="URL of the github/jira/tracking issue associated with this report.")
        md_parser.add_argument('-o', '--output-file',
            help="Destination file for slack message.  Message will be output to stdout if left blank.")
        md_parser.set_defaults(func=JsonGenerator.generate_json_report_from_args)
        return subparser_name, md_parser


    def generate_json_report_from_args(args):
        """Static method to create a JsonGenerator object and generate a slack report from the command-line args.

        Required Argument:
        args -- argparse-generated arguments from an argparse with a parser generated by JsonGenerator.generate_subparser()
        """
        _ignorelist = []
        if args.ignore_list is not None and os.path.isfile(args.ignore_list):
            try:
                with open(args.ignore_list, "r+") as f:
                    _il = json.loads(f.read())
                _ignorelist = _il['ignored_tests']
            except json.JSONDecodeError as ex:
                print(f"Ignorelist found in {args.ignore_list} was not in JSON format, ignoring the ignorelist. Ironic.")
        _generator = JsonGenerator(args.results_directory, snapshot=args.snapshot, branch=args.branch, stage=args.stage,
            hub_version=args.hub_version, hub_platform=args.hub_platform, import_version=args.import_version, import_platform=args.import_platform,
            job_url=args.job_url, build_id=args.build_id, ignorelist=_ignorelist,
            issue_url=args.issue_url, executed_quality_gate=int(args.executed_quality_gate), passing_quality_gate=int(args.passing_quality_gate))
        _message = _generator.generate_json_report()
        if args.output_file is not None:
            with open(args.output_file, "w+") as f:
                f.write(json.dumps(_message))
        else:
            print(json.dumps(_message))

    
    def generate_json_report(self):
        """Macro function to assemble our json report.  This wraps data extraction and the inclusion of metadata in our JSON payload."""
        _report = self.aggregated_results.get_raw_results()
        if self.snapshot is not None:
            _report["snapshot"] = self.snapshot
        if self.branch is not None:
            _report["branch"] = self.branch
        if self.stage is not None:
            _report["stage"] = self.stage
        if self.hub_version is not None:
            _report["hub_version"] = self.hub_version
        if self.hub_platform is not None:
            _report["hub_platform"] = self.hub_platform
        if self.import_version is not None:
            _report["import_version"] = self.import_version
        if self.import_platform is not None:
            _report["import_platform"] = self.import_platform
        if self.job_url is not None:
            _report["job_url"] = self.job_url
        if self.build_id is not None:
            _report["build_id"] = self.build_id
        if self.ignorelist is not None:
            _report["ignorelist"] = self.ignorelist
        if self.issue_url is not None:
            _report["issue_url"] = self.issue_url
        if self.executed_quality_gate is not None:
            _report["executed_quality_gate"] = self.executed_quality_gate
        if self.passing_quality_gate is not None:
            _report["passing_quality_gate"] = self.passing_quality_gate
        return _report

