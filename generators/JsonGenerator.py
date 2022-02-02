"""JsonGenerator

An AbstractGenerator and ReportGenerator implementation to generate a raw JSON payload as part of the canary reporting CLI.  
This class can generate its CLI parser, load args, generate a ResultsAggregator object, and format the output data as a raw JSON payload. 
"""

import os, sys, json, argparse, re
from re import findall
from generators import AbstractGenerator,ReportGenerator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from datamodel import ResultsAggregator as ra

class JsonGenerator(AbstractGenerator.AbstractGenerator, ReportGenerator.ReportGenerator):

    def __init__(self, results_dirs, snapshot=None, branch=None, verification_level=None, stage=None, hub_version=None, 
        hub_platform=None, import_cluster_details=[], job_url=None, build_id=None,
        issue_url=None, ignorelist=[], passing_quality_gate=100, executed_quality_gate=100):
        """Create a JsonGenerator Object, unroll xml files from input, and initialize a ResultsAggregator.  

        Required Arguments:
        results_dirs    -- a list of directories that contain XML files from which to generate an aggregate report

        Keyword Arguments:
        snapshot    --  a string representation of the snapshot that these test results represent, ex. 2.2.0-SNAPSHOT-timestamp
        branch      --  a string representaiton of the integration test branch that generated the xml results, ex. 2.2-integration
        verification_level  --  the level of verification testing that this report was generated on
        stage       --  a string representaiton of the integration test stage/step that generated the xml results, ex deploy
        hub_version     --  a string representation of the hub cluster version that was tested
        hub_platform    --  a string representation of the hub cluster's hosting cloud platform
        import_cluster_details  --  a list of dicts, each identifying an import cluster's clustername, version, and platform
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
        self.job_url = job_url
        self.build_id = build_id
        self.issue_url = issue_url
        self.ignorelist = ignorelist
        self.import_cluster_details = import_cluster_details
        self.passing_quality_gate = passing_quality_gate
        self.executed_quality_gate = executed_quality_gate
        self.results_files = []
        if verification_level is not None:
            self.verification_level = verification_level
        elif branch is None:
            self.verification_level = "Verification Test"
        else:
            self.verification_level = "BVT" if re.match(r".*-integration\b", branch) else "SVT" if re.match(r".*-dev\b", branch) else "SVT-Extended" if re.match(r".*-nightly\b" ,branch) else "Verification Test"
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
        js_parser = subparser.add_parser(subparser_name, parents=[ReportGenerator.ReportGenerator.generate_parent_parser()],
            help="Generate a JSON file containing raw test results and metadata about the canary run.",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog="""
Example Usage:

    Generate a parsed and processed JSON representation of the JUnit results in the 'junit_xml' folder and output it to 'out.json':
        python3 reporter.py js junit_xml/ -o out.json    
""")
        js_parser.add_argument('-iu', '--issue-url', default=os.getenv('GIT_ISSUE_URL'),
            help="URL of the github/jira/tracking issue associated with this report.")
        js_parser.add_argument('-o', '--output-file',
            help="Destination file for slack message.  Message will be output to stdout if left blank.")
        js_parser.set_defaults(func=JsonGenerator.generate_json_report_from_args)
        return subparser_name, js_parser


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
        _import_cluster_details = []
        if args.import_cluster_details_file is not None and os.path.isfile(args.import_cluster_details_file):
            try:
                with open(args.import_cluster_details_file, "r+") as f:
                    _import_cluster_details = json.loads(f.read())
            except json.JSONDecodeError as ex:
                print(f"Import cluster details found in {args.import_cluster_details_file} was not in JSON format, ignoring.")
        elif args.import_version or args.import_platform:
            _import_cluster_details = {
                "clustername": ""
            }
            _import_cluster_details["version"] = args.import_version if args.import_version else ""
            _import_cluster_details["platform"] = args.import_platform if args.import_platform else ""
        if args.verification_level is not None:
            _verification_level = args.verification_level
        else:
            _verification_level = "BVT" if re.match(r".*-integration\b", args.branch) else "SVT" if re.match(r".*-dev\b", args.branch) else "SVT-Extended" if re.match(r".*-nightly\b" , args.branch) else "Verification Test"
        _generator = JsonGenerator(args.results_directory, snapshot=args.snapshot, branch=args.branch, verification_level=_verification_level, stage=args.stage,
            hub_version=args.hub_version, hub_platform=args.hub_platform,
            import_cluster_details=_import_cluster_details, job_url=args.job_url, build_id=args.build_id, ignorelist=_ignorelist,
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
        # Translate fields that our internal datamodel defaults to None to "" to make it more JSON-friendly
        _report["snapshot"] = self.snapshot if self.snapshot else ""
        _report["branch"] = self.branch if self.branch else ""
        _report["verification_level"] = self.verification_level
        _report["stage"] = self.stage if self.branch else ""
        _report["hub_version"] = self.hub_version if self.hub_version else ""
        _report["hub_platform"] = self.hub_platform if self.hub_platform else ""
        _report["job_url"] = self.job_url if self.job_url else ""
        _report["build_id"] = self.build_id if self.build_id else ""
        _report["issue_url"] = self.issue_url if self.issue_url else ""
        # No translation needed for integers wtih defaults and lists that default to empty in internal data model
        _report["ignorelist"] = self.ignorelist
        _report["import_cluster_details"] = self.import_cluster_details
        _report["executed_quality_gate"] = self.executed_quality_gate
        _report["passing_quality_gate"] = self.passing_quality_gate
        return _report

