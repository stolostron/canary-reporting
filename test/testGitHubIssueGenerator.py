import unittest, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from generators import GitHubIssueGenerator

class TestGitHubIssueGenerator(unittest.TestCase):

    results_folder = f"{os.path.dirname(os.path.abspath(__file__))}/test_results_dir"
    output_file = f"{os.path.dirname(os.path.abspath(__file__))}/github.md"
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

    def test_github_issue_full(self):
        _gh_generator = GitHubIssueGenerator.GitHubIssueGenerator(
            [TestGitHubIssueGenerator.results_folder],
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
            sd_url="TEST_SD_URL",
            must_gather_url="TEST_MUST_GATHER_URL",
            results_url="TEST_RESULTS_URL",
            tags=["TEST_TAG"],
            output_file=TestGitHubIssueGenerator.output_file,
            dry_run=True
        )
        _gh_generator.open_github_issue()
        with open(TestGitHubIssueGenerator.output_file, "r+") as f:
            _gh_report = f.read()
        self.assertEqual(_gh_report, """# :red_circle:TEST_SNAPSHOT Failed on branch Test_stage
## Job URL: TEST_JOB_URL
## Artifacts & Details
[**Must-Gather Bucket**](TEST_MUST_GATHER_URL)

[**Results Bucket**](TEST_RESULTS_URL)

[**Snapshot Diff**](TEST_SD_URL)

**Hub Cluster Platform:** TEST_HUB_PLATFORM    **Hub Cluster Version:** TEST_HUB_VERSION

**Import Cluster(s):**
* **Import Cluster Platform:** aws    **Import Cluster Version:** 4.7.0
* **Import Cluster Platform:** gcp    **Import Cluster Version:** 4.7.1


## Quality Gate

:warning: **Percentage Executed:** 92.31% (100% Quality Gate)

:red_circle: **Percentage Passing:** 75.0% (100% Quality Gate)

## Summary

**:white_check_mark: 9 Tests Passed**

**:x: 3 Tests Failed**

**:large_orange_diamond: 0 Failures Ignored**

**:large_blue_circle: 1 Test Case Skipped**


## Failing Tests

### :x: Provider connections -> Provider connections should be able to be created

```
CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:

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
    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)
```
### :x: adminSearch.test -> Search: Search for secret

```
    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)
```
### :x: viewerSearch.test -> Search: Viewer is NOT able to edit configmaps

```
    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Viewer is NOT able to edit configmaps (/tests/e2e/viewerSearch.test.js:41:16)
```

""")


    def test_github_issue_ignorelist(self):
        _gh_generator = GitHubIssueGenerator.GitHubIssueGenerator(
            [TestGitHubIssueGenerator.results_folder],
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
            sd_url="TEST_SD_URL",
            must_gather_url="TEST_MUST_GATHER_URL",
            results_url="TEST_RESULTS_URL",
            tags=["TEST_TAG"],
            dry_run=True,
            output_file=TestGitHubIssueGenerator.output_file,
            ignorelist=TestGitHubIssueGenerator.ignorelist
        )
        _gh_generator.open_github_issue()
        with open(TestGitHubIssueGenerator.output_file, "r+") as f:
            _gh_report = f.read()
        self.assertEqual(_gh_report, """# :red_circle:TEST_SNAPSHOT Failed on branch Test_stage
## Job URL: TEST_JOB_URL
## Artifacts & Details
[**Must-Gather Bucket**](TEST_MUST_GATHER_URL)

[**Results Bucket**](TEST_RESULTS_URL)

[**Snapshot Diff**](TEST_SD_URL)

**Hub Cluster Platform:** TEST_HUB_PLATFORM    **Hub Cluster Version:** TEST_HUB_VERSION

**Import Cluster(s):**
* **Import Cluster Platform:** aws    **Import Cluster Version:** 4.7.0
* **Import Cluster Platform:** gcp    **Import Cluster Version:** 4.7.1


## Quality Gate

:warning: **Percentage Executed:** 92.31% (100% Quality Gate)

:red_circle: **Percentage Passing:** 75.0% (100% Quality Gate)

## Summary

**:white_check_mark: 9 Tests Passed**

**:x: 2 Tests Failed**

**:large_orange_diamond: 1 Failure Ignored**

**:large_blue_circle: 1 Test Case Skipped**


## Failing Tests

### :x: Provider connections -> Provider connections should be able to be created

```
CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:

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
    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)
```
### :x: adminSearch.test -> Search: Search for secret

```
    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)
```
### :large_orange_diamond: viewerSearch.test -> Search: Viewer is NOT able to edit configmaps

```
    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Viewer is NOT able to edit configmaps (/tests/e2e/viewerSearch.test.js:41:16)
```

""")


    def test_github_issue_min(self):
        _gh_generator = GitHubIssueGenerator.GitHubIssueGenerator(
            [TestGitHubIssueGenerator.results_folder], 
            output_file=TestGitHubIssueGenerator.output_file,
            dry_run=True
        )
        _gh_report = _gh_generator.open_github_issue()
        with open(TestGitHubIssueGenerator.output_file, "r+") as f:
            _gh_report = f.read()
        self.assertEqual(_gh_report, """# :red_circle: Failed
## Artifacts & Details


## Quality Gate

:warning: **Percentage Executed:** 92.31% (100% Quality Gate)

:red_circle: **Percentage Passing:** 75.0% (100% Quality Gate)

## Summary

**:white_check_mark: 9 Tests Passed**

**:x: 3 Tests Failed**

**:large_orange_diamond: 0 Failures Ignored**

**:large_blue_circle: 1 Test Case Skipped**


## Failing Tests

### :x: Provider connections -> Provider connections should be able to be created

```
CypressError: Timed out retrying: `cy.click()` failed because this element is `disabled`:

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
    at Promise._settlePromises (https://multicloud-console.apps.ds4-aws-444.aws.red-chesterfield.com/__cypress/runner/cypress_runner.js:7182:18)
```
### :x: adminSearch.test -> Search: Search for secret

```
    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Search for secret (/tests/e2e/adminSearch.test.js:34:16)
```
### :x: viewerSearch.test -> Search: Viewer is NOT able to edit configmaps

```
    at Page.enterTextInSearchbar (/tests/page-objects/SearchPage.js:73:8)
    at Object.Search: Viewer is NOT able to edit configmaps (/tests/e2e/viewerSearch.test.js:41:16)
```

""")


    def tearDown(self):
        if os.path.exists(TestGitHubIssueGenerator.output_file):
            os.remove(TestGitHubIssueGenerator.output_file)


if __name__ == '__main__':
    unittest.main()