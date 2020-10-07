import argparse, os

class ReportGenerator():
    
    def generate_parent_parser() -> argparse.ArgumentParser:
        parent = argparse.ArgumentParser(add_help=False)
        parent.add_argument('results-directory', nargs='+', metavar='RESULTS_DIR',
            help="A directory that holds JUnit XML Results files to process and generate a report from.")
        parent.add_argument('-sn', '--snapshot', nargs=1, default=os.getenv('SNAPSHOT'),
            help="The snapshot whose test results are represented in RESULTS_DIR. Attempts to load from the SNAPSHOT environment variable if omitted.")
        parent.add_argument('-b', '--branch', nargs=1, default=os.getenv('TRAVIS_BRANCH'),
            help="The name of the GitHub branch whose build failed. Attempts to load from the TRAVIS_BRANCH environment variable if omitted.")
        parent.add_argument('-st', '--stage', nargs=1, default=os.getenv('TRAVIS_BUILD_STAGE_NAME'),
            help="Name of the stage during which the build failed. Attempts to load from the TRAVIS_BUILD_STAGE_NAME environment variable if omitted.")
        parent.add_argument('-hv', '--hub-version', nargs=1, default=os.getenv('HUB_CLUSTER_VERSION'),
            help="OCP Version of the hub cluster used. Attempts to load from the HUB_CLUSTER_VERSION environment variable if omitted.")
        parent.add_argument('-hp', '--hub-platform', nargs=1, default=os.getenv('HUB_PLATFORM'),
            help="Cloud Platform of the hub cluster used. Attempts to load from the HUB_PLATFORM environment variable if omitted.")
        parent.add_argument('-iv', '--import-version', nargs=1, default=os.getenv('IMPORT_CLUSTER_VERSION'),
            help="OCP Version of the import cluster used. Attempts to load from the IMPORT_CLUSTER_VERSION environment variable if omitted.")
        parent.add_argument('-ip', '--import-platform', nargs=1, default=os.getenv('IMPORT_PLATFORM'),
            help="Cloud Platform of the import cluster used. Attempts to load from the IMPORT_PLATFORM environment variable if omitted.")
        parent.add_argument('-j', '--job-url', nargs=1, default=os.getenv('TRAVIS_BUILD_WEB_URL'),
            help="URL of the CI job that created the XML Artifacts. Attempts to load from the TRAVIS_BUILD_WEB_URL environment variable if omitted.")
        parent.add_argument('-id', '--build-id', nargs=1, default=os.getenv('TRAVIS_BUILD_ID'),
            help="Unique ID of the CI job that created the XML Artifacts. Attempts to load from the TRAVIS_BUILD_ID environment variable if omitted.")
        parent.add_argument('-il', '--ignore-list', nargs=1,
            help="Path to the IgnoreList JSON file. Ignorelist won't be used if omitted.")
        return parent