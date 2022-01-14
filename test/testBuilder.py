import json, os, sys, unittest
from numpy import equal
import numpy
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from generators import JsonGenerator
from builder import process_test_results

class TestBuilder(unittest.TestCase):

    results_folder = f"{os.path.dirname(os.path.abspath(__file__))}/test_results_dir"
    def test_process_test_results(self):
        _js_generator = JsonGenerator.JsonGenerator(
            [TestBuilder.results_folder],
            snapshot="TEST_SNAPSHOT",
            branch="TEST_BRANCH",
            verification_level="BVT",
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
        processed_results['verificiation_level'] = _df['verification_level']
        processed_results['issue_url'] = _df['issue_url']
        processed_results['time'] = "SNAPSHOT_TIME"
        processed_results['acm_release'] = "SNAPSHOT_RELEASE"
        processed_results = processed_results[['id','time','acm_release', 'verification_level','squad(s)','testsuite','passes','fails','skips','ignored','severity','priority','hub_platform','hub_version','stage','branch', 'issue_url']]
        _expected = pd.read_csv(f"{os.path.dirname(os.path.abspath(__file__))}/df.txt", delimiter="\t", dtype={'passes': pd.Int64Dtype(), 'fails': pd.Int64Dtype(), 'skips': pd.Int64Dtype(), 'ignored': pd.Int64Dtype()})
        pd.testing.assert_frame_equal(_expected, processed_results)

if __name__ == '__main__':
    unittest.main()