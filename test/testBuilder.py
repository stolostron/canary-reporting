import json
import datetime
import re
import os
import sys
import unittest
from pandas.core.frame import DataFrame
import pymysql
import pandas as pd
from pandas.io.json import json_normalize
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from generators import JsonGenerator
from builder import process_test_results
from __future__ import print_function

class TestBuilder(unittest.TestCase):
    results_folder = f"{os.path.dirname(os.path.abspath(__file__))}/test_results_dir"
    def process_test_results(self):
        _js_generator = JsonGenerator.JsonGenerator(
            [TestBuilder.results_folder],
            snapshot="TEST_SNAPSHOT",
            branch="TEST_BRANCH",
            stage="TEST_STAGE",
            hub_version="TEST_HUB_VERSION",
            hub_platform="TEST_HUB_PLATFORM",
            import_cluster_details=[
                {
                    "clustername": "cluster1",
                    "version": "4.7.0",
                    "platform": "aws"
                },
                {
                    "clustername": "cluster2",
                    "version": "4.7.1",
                    "platform": "gcp"
                }
            ],
            job_url="TEST_JOB_URL",
            build_id="TEST_BUILD_ID",
            executed_quality_gate=100,
            passing_quality_gate=100,
            issue_url="TEST_ISSUE_URL",
            ignorelist=[]
        )
        _js_report = _js_generator.generate_json_report()
        _json = json.dumps(_js_report)
        _df = json.loads(_json)
        processed_results = process_test_results(_df)
        processed_results['hub_platform'] = _df['hub_platform']
        processed_results['hub_version'] = _df['hub_version']
        processed_results['id'] = _df['snapshot']
        processed_results['stage'] = _df['stage']
        processed_results['branch'] = _df['branch']
        processed_results['issue_url'] = _df['issue_url']
        processed_results['time'] = _df['snapshot']
        processed_results['acm_release'] = _df['snapshot']
        processed_results = processed_results[['id','time','acm_release','squad(s)','testsuite','passes','fails','skips','ignored','severity','priority','hub_platform','hub_version','stage','branch','issue_url']]
        _expected = pd.read_csv('df.txt', delimiter="\t")
        self.assertEqual(processed_results, _expected)

if __name__ == '__main__':
    unittest.main()