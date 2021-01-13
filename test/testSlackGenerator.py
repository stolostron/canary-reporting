import unittest, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from generators import SlackGenerator

class TestSlackGenerator(unittest.TestCase):

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

    def test_slack_report_full(self):
        _sl_generator = SlackGenerator.SlackGenerator(
            [TestSlackGenerator.results_folder],
            snapshot="TEST_SNAPSHOT",
            branch="TEST_BRANCH",
            stage="TEST_STAGE",
            hub_version="TEST_HUB_VERSION",
            hub_platform="TEST_HUB_PLATFORM",
            import_version="TEST_IMPORT_VERSION",
            import_platform="TEST_IMPORT_PLATFORM",
            job_url="TEST_JOB_URL",
            build_id="TEST_BUILD_ID",
            sd_url="TEST_SD_URL",
            issue_url="TEST_ISSUE_URL",
            md_url="TEST_MD_URL"
        )
        _sl_report = _sl_generator.generate_slack_report()
        self.assertEqual(_sl_report, """*:red_circle:TEST_SNAPSHOT Failed on branch Test_stage*
*Job URL:* TEST_JOB_URL
*Results Markdown:* TEST_MD_URL
*Snapshot Diff:* TEST_SD_URL
*Hub Cluster Version:* TEST_HUB_VERSION  *Import Cluster Version:* TEST_IMPORT_VERSION
*Opened Issue URL:* TEST_ISSUE_URL

*Quality Gate (100% - 100%):*
:red_jenkins_circle:*92% Executed - 75% Passing*

*Results:*
*:white_check_mark: 9 Tests Passed*
*:failed: 3 Tests Failed*
*:warning: 0 Failures Ignored*
*:blue_question: 1 Test Case Skipped*

*Failing Tests*
:failed: adminSearch.test -> Search: Search for secret
```    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)```
:failed: viewerSearch.test -> Search: Viewer is NOT able to edit configmaps
```    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Viewer is NOT able to edit configmaps (/tests/e2e/viewerSearch.test.js:41:16)```
:failed: Provider connections -> Provider connections should be able to be created
```CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:

`<button tabindex="0" class="bx--btn bx--btn--primary" disabled="" type="button">Go to p...</button>`

Fix this problem, or use `{force: true}` to disable error checking.

https://on.cypress.io/element-cannot-be-interacted-with
    at cypressErr (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146621:16)
    at cypressErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146630:10)
    at Object.throwErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146593:11)
    at Object.ensureNotDisabled (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:137570:24)
    at runAllChecks (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127486:14)
    at retryActionability (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127542:16)
    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)
    at Function.Promise.attempt.Promise.try (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:6339:29)
    at tryFn (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140680:21)
    at whenStable (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140715:12)
    at https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140259:16
    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)
    at Promise._settlePromiseFromHandler (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7000:31)
    at Promise._settlePromise (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7057:18)
    at Promise._settlePromise0 (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7102:10)
    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)```
""")


    def test_slack_report_ignorelist(self):
        _sl_generator = SlackGenerator.SlackGenerator(
            [TestSlackGenerator.results_folder],
            snapshot="TEST_SNAPSHOT",
            branch="TEST_BRANCH",
            stage="TEST_STAGE",
            hub_version="TEST_HUB_VERSION",
            hub_platform="TEST_HUB_PLATFORM",
            import_version="TEST_IMPORT_VERSION",
            import_platform="TEST_IMPORT_PLATFORM",
            job_url="TEST_JOB_URL",
            build_id="TEST_BUILD_ID",
            sd_url="TEST_SD_URL",
            issue_url="TEST_ISSUE_URL",
            md_url="TEST_MD_URL",
            ignorelist=TestSlackGenerator.ignorelist
        )
        _sl_report = _sl_generator.generate_slack_report()
        self.assertEqual(_sl_report, """*:red_circle:TEST_SNAPSHOT Failed on branch Test_stage*
*Job URL:* TEST_JOB_URL
*Results Markdown:* TEST_MD_URL
*Snapshot Diff:* TEST_SD_URL
*Hub Cluster Version:* TEST_HUB_VERSION  *Import Cluster Version:* TEST_IMPORT_VERSION
*Opened Issue URL:* TEST_ISSUE_URL

*Quality Gate (100% - 100%):*
:red_jenkins_circle:*92% Executed - 75% Passing*

*Results:*
*:white_check_mark: 9 Tests Passed*
*:failed: 2 Tests Failed*
*:warning: 1 Failure Ignored*
*:blue_question: 1 Test Case Skipped*

*Failing Tests*
:failed: adminSearch.test -> Search: Search for secret
```    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)```
:failed: Provider connections -> Provider connections should be able to be created
```CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:

`<button tabindex="0" class="bx--btn bx--btn--primary" disabled="" type="button">Go to p...</button>`

Fix this problem, or use `{force: true}` to disable error checking.

https://on.cypress.io/element-cannot-be-interacted-with
    at cypressErr (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146621:16)
    at cypressErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146630:10)
    at Object.throwErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146593:11)
    at Object.ensureNotDisabled (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:137570:24)
    at runAllChecks (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127486:14)
    at retryActionability (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127542:16)
    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)
    at Function.Promise.attempt.Promise.try (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:6339:29)
    at tryFn (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140680:21)
    at whenStable (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140715:12)
    at https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140259:16
    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)
    at Promise._settlePromiseFromHandler (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7000:31)
    at Promise._settlePromise (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7057:18)
    at Promise._settlePromise0 (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7102:10)
    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)```
""")


    def test_slack_report_min(self):
        _sl_generator = SlackGenerator.SlackGenerator([TestSlackGenerator.results_folder])
        _sl_report = _sl_generator.generate_slack_report()
        self.assertEqual(_sl_report, """*:red_circle: Failed*

*Quality Gate (100% - 100%):*
:red_jenkins_circle:*92% Executed - 75% Passing*

*Results:*
*:white_check_mark: 9 Tests Passed*
*:failed: 3 Tests Failed*
*:warning: 0 Failures Ignored*
*:blue_question: 1 Test Case Skipped*

*Failing Tests*
:failed: adminSearch.test -> Search: Search for secret
```    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)```
:failed: viewerSearch.test -> Search: Viewer is NOT able to edit configmaps
```    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Viewer is NOT able to edit configmaps (/tests/e2e/viewerSearch.test.js:41:16)```
:failed: Provider connections -> Provider connections should be able to be created
```CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:

`<button tabindex="0" class="bx--btn bx--btn--primary" disabled="" type="button">Go to p...</button>`

Fix this problem, or use `{force: true}` to disable error checking.

https://on.cypress.io/element-cannot-be-interacted-with
    at cypressErr (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146621:16)
    at cypressErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146630:10)
    at Object.throwErrByPath (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:146593:11)
    at Object.ensureNotDisabled (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:137570:24)
    at runAllChecks (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127486:14)
    at retryActionability (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:127542:16)
    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)
    at Function.Promise.attempt.Promise.try (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:6339:29)
    at tryFn (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140680:21)
    at whenStable (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140715:12)
    at https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:140259:16
    at tryCatcher (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:9065:23)
    at Promise._settlePromiseFromHandler (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7000:31)
    at Promise._settlePromise (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7057:18)
    at Promise._settlePromise0 (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7102:10)
    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)```
""")


if __name__ == '__main__':
    unittest.main()