import unittest, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from generators import JsonGenerator

class TestJsonGenerator(unittest.TestCase):

    results_folder = f"{os.path.dirname(os.path.abspath(__file__))}/test_results_dir"
    ignorelist = [
        {
            "name": "Search: Viewer is NOT able to edit configmaps",
            "squad": "search",
            "owner": "@anonymous-user-that-I-wont-name"
        },
        {
            "name": "Search: Load page",
            "squad": "search",
            "owner": "@anonymous-user-that-I-wont-name"
        }
    ]

    def test_json_report_full(self):
        _js_generator = JsonGenerator.JsonGenerator(
            [TestJsonGenerator.results_folder],
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
        _expected = {'results': [{'name': 'Cluster can be created on AWS', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Cluster comes to the Ready status - "ds8-aws-444"', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Cluster import command can be applied on "ds8-aws-444"', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Cluster import command can be generated for "ds8-aws-444"', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Edit secret as Admin user', 'state': 'skipped', 'testsuite': 'adminSearch.test', 'metadata': {'message': '', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_adminSearch.test.xml'}}, {'name': 'Overview page should load', 'state': 'passed', 'testsuite': 'Overview', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Provider connections page should load', 'state': 'passed', 'testsuite': 'Provider connections', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Provider connections should be able to be created', 'state': 'failed', 'testsuite': 'Provider connections', 'metadata': {'message': 'CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:\n\n`<button tabindex="0" class="bx--btn bx--btn--primary" disabled="" type="button">Go to p...</button>`\n\nFix this problem, or use `{force: true}` to disable error checking.\n\nhttps://on.cypress.io/element-cannot-be-interacted-with\n    at cypressErr (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146621:16)\n    at cypressErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146630:10)\n    at Object.throwErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146593:11)\n    at Object.ensureNotDisabled (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:137570:24)\n    at runAllChecks (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127486:14)\n    at retryActionability (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127542:16)\n    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)\n    at Function.Promise.attempt.Promise.try (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:6339:29)\n    at tryFn (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140680:21)\n    at whenStable (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140715:12)\n    at https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140259:16\n    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)\n    at Promise._settlePromiseFromHandler (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7000:31)\n    at Promise._settlePromise (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7057:18)\n    at Promise._settlePromise0 (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7102:10)\n    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Provider connections should be abled to be edited', 'state': 'passed', 'testsuite': 'Provider connections', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Search: Load page', 'state': 'passed', 'testsuite': 'adminSearch.test', 'metadata': {'message': '', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_adminSearch.test.xml'}}, {'name': 'Search: Load page', 'state': 'passed', 'testsuite': 'viewerSearch.test', 'metadata': {'message': '', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_viewerSearch.test.xml'}}, {'name': 'Search: Search for secret', 'state': 'failed', 'testsuite': 'adminSearch.test', 'metadata': {'message': '    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)\n    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_adminSearch.test.xml'}}, {'name': 'Search: Viewer is NOT able to edit configmaps', 'state': 'failed', 'testsuite': 'viewerSearch.test', 'metadata': {'message': '    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)\n    at Object.Search: Viewer is NOT able to edit configmaps (/tests/e2e/viewerSearch.test.js:41:16)', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_viewerSearch.test.xml'}}], 'total': 13, 'failed': 3, 'passed': 9, 'skipped': 1, 'ignored': 0, 'snapshot': 'TEST_SNAPSHOT', 'branch': 'TEST_BRANCH', 'stage': 'TEST_STAGE', 'hub_version': 'TEST_HUB_VERSION', 'hub_platform': 'TEST_HUB_PLATFORM', 'job_url': 'TEST_JOB_URL', 'build_id': 'TEST_BUILD_ID', 'issue_url': 'TEST_ISSUE_URL', 'ignorelist': [], 'import_cluster_details': [{'clustername': 'cluster1', 'version': '4.7.0', 'platform': 'aws'}, {'clustername': 'cluster2', 'version': '4.7.1', 'platform': 'gcp'}], 'executed_quality_gate': 100, 'passing_quality_gate': 100}
        self.assertEqual(_js_report, _expected)

    
    def test_json_report_ignorelist(self):
        _js_generator = JsonGenerator.JsonGenerator(
            [TestJsonGenerator.results_folder],
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
            ignorelist=TestJsonGenerator.ignorelist
        )
        _js_report = _js_generator.generate_json_report()
        _expected = {'results': [{'name': 'Cluster can be created on AWS', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Cluster comes to the Ready status - "ds8-aws-444"', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Cluster import command can be applied on "ds8-aws-444"', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Cluster import command can be generated for "ds8-aws-444"', 'state': 'passed', 'testsuite': 'Cluster', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Edit secret as Admin user', 'state': 'skipped', 'testsuite': 'adminSearch.test', 'metadata': {'message': '', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_adminSearch.test.xml'}}, {'name': 'Overview page should load', 'state': 'passed', 'testsuite': 'Overview', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Provider connections page should load', 'state': 'passed', 'testsuite': 'Provider connections', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Provider connections should be able to be created', 'state': 'failed', 'testsuite': 'Provider connections', 'metadata': {'message': 'CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:\n\n`<button tabindex="0" class="bx--btn bx--btn--primary" disabled="" type="button">Go to p...</button>`\n\nFix this problem, or use `{force: true}` to disable error checking.\n\nhttps://on.cypress.io/element-cannot-be-interacted-with\n    at cypressErr (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146621:16)\n    at cypressErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146630:10)\n    at Object.throwErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146593:11)\n    at Object.ensureNotDisabled (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:137570:24)\n    at runAllChecks (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127486:14)\n    at retryActionability (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127542:16)\n    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)\n    at Function.Promise.attempt.Promise.try (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:6339:29)\n    at tryFn (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140680:21)\n    at whenStable (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140715:12)\n    at https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140259:16\n    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)\n    at Promise._settlePromiseFromHandler (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7000:31)\n    at Promise._settlePromise (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7057:18)\n    at Promise._settlePromise0 (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7102:10)\n    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Provider connections should be abled to be edited', 'state': 'passed', 'testsuite': 'Provider connections', 'metadata': {'message': '', 'filename': 'console-ui-5a5a75448822a22f63c3c1aa6155320048f82336-console-ui-init.xml'}}, {'name': 'Search: Load page', 'state': 'passed', 'testsuite': 'adminSearch.test', 'metadata': {'message': '', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_adminSearch.test.xml'}}, {'name': 'Search: Load page', 'state': 'passed', 'testsuite': 'viewerSearch.test', 'metadata': {'message': '', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_viewerSearch.test.xml'}}, {'name': 'Search: Search for secret', 'state': 'failed', 'testsuite': 'adminSearch.test', 'metadata': {'message': '    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)\n    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_adminSearch.test.xml'}}, {'name': 'Search: Viewer is NOT able to edit configmaps', 'state': 'ignored', 'testsuite': 'viewerSearch.test', 'metadata': {'message': '    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)\n    at Object.Search: Viewer is NOT able to edit configmaps (/tests/e2e/viewerSearch.test.js:41:16)', 'filename': 'search-5a5a75448822a22f63c3c1aa6155320048f82336-CHROME_83.0.4103.116_Linux_viewerSearch.test.xml'}}], 'total': 13, 'failed': 2, 'passed': 9, 'skipped': 1, 'ignored': 1, 'snapshot': 'TEST_SNAPSHOT', 'branch': 'TEST_BRANCH', 'stage': 'TEST_STAGE', 'hub_version': 'TEST_HUB_VERSION', 'hub_platform': 'TEST_HUB_PLATFORM', 'job_url': 'TEST_JOB_URL', 'build_id': 'TEST_BUILD_ID', 'issue_url': 'TEST_ISSUE_URL', 'ignorelist': [{'name': 'Search: Viewer is NOT able to edit configmaps', 'squad': 'search', 'owner': '@anonymous-user-that-I-wont-name'}, {'name': 'Search: Load page', 'squad': 'search', 'owner': '@anonymous-user-that-I-wont-name'}], 'import_cluster_details': [{'clustername': 'cluster1', 'version': '4.7.0', 'platform': 'aws'}, {'clustername': 'cluster2', 'version': '4.7.1', 'platform': 'gcp'}], 'executed_quality_gate': 100, 'passing_quality_gate': 100}
        self.assertEqual(_js_report, _expected)


if __name__ == '__main__':
    unittest.main()