"""SnapshotDiffGenerator

An AbstractGenerator implementation to generate a snapshot diff as part of the canary reporting CLI.  This class
can generate its CLI parser, load args, generate a diff, and format the output diff including git artifacts. 
"""

from generators import AbstractGenerator
import os, re, argparse, json, pprint, github, shutil

class SnapshotDiffGenerator(AbstractGenerator.AbstractGenerator):

    skipped_repos = [
        "stolostron/example-cicd-component"
    ]

    nullary_element = {
        "image-name": "null",
        "image-version": "null",
        "image-tag": "null",
        "git-sha256": "null",
        "git-repository": "null",
        "image-remote": "null",
        "image-digest": "null",
        "image-key": "null"
    }

    def __init__(self, base, base_repo_type, new, new_repo_type, base_timestamp=None, new_timestamp=None, base_product_version=None, new_product_version=None, github_token=None, 
                    github_org='stolostron', github_repo='pipeline', load_commits=True):
        """Create a SnapshotDiffGenerator Object, populate the diff, and conditionally load GitHub artifacts.  

        Required Arguments:
        base      -- the base manifest descriptor, could be a stage in github_repo or a manifest filename
        base_repo -- repo type for the base manifest.  Toggles between local file and github
        new       -- the new manifest descriptor, could be a stage in github_repo or a manifest filename
        new_repo  -- repo type for the new manifest.  Toggles between local file and github

        Keyword Arguments:
        base_timestamp       -- timestamp for the base manifest, only used on github type sources; will find the next-latest if not specified
        new_timestamp        -- timestamp for the new manifest, only used on github type sources
        base_product_version -- product version for the base manifest, only used on github type sources; example: 2.3.0
        new_product_version  -- product version for the new manifest, only used on github type sources; example: 2.3.0
        github_token    -- token used to access github, only used on github type sources
        github_org      -- github organization to be used for manifest query, only used on github type sources
        github_repo     -- github repo housing manifest files, only used on github type sources
        load_commits    -- toggles github artifact query, will load commits & PRs if true
        """
        # Necessary Parameterized Variables
        self.load_commits = load_commits
        self.base = base
        self.base_repo_type = base_repo_type
        self.new = new
        self.new_repo_type = new_repo_type
        self.base_timestamp = base_timestamp
        self.new_timestamp = new_timestamp
        self.base_product_version = base_product_version
        self.base_product_major_version = None
        if self.base_product_version is not None:
            self.base_product_major_version = re.search('([0-9]+\.[0-9]+)\.[0-9]+', self.base_product_version).group(1)
        self.new_product_version = new_product_version
        self.new_product_major_version = None
        if self.new_product_version is not None:
            self.new_product_major_version = re.search('([0-9]+\.[0-9]+)\.[0-9]+', self.new_product_version).group(1)
        # Toggle git features on/off based on repo types (can't check for local)
        if self.base_repo_type == "local" or self.new_repo_type == "local":
            self.load_commits = False
        # We only need git creds if the user wants us to source files from git.
        if self.base_repo_type == "github" or self.new_repo_type == "github":
            self.github_token = github_token
            self.github_org = github_org
            self.github_repo = github_repo
            if self.github_token == "":
                raise ValueError('GitHub Token cannot be an empty string.')
            # Clients and objects for global query use
            self.gh_client = github.Github(self.github_token)
            self.gh_organization = self.gh_client.get_organization(self.github_org)
            self.gh_repo = self.gh_organization.get_repo(self.github_repo)
        # Operational/Class Variables
        self.diff = []
        self.base_manifest_name = None
        self.base_manifest = []
        self.new_manifest_name = None
        self.new_manifest = []
        # Load our manifests and diff
        self.generate_snapshot_diff()
        # Load GitHub commits and PRs if requested
        if self.load_commits:
            self.load_commits_for_diff()


    def generate_subparser(subparser):
        """Static method to generate a subparser for the SnapshotDiffGenerator module.  

        Required Argument:
        subparser -- an argparse.ArgumentParser object to extend with a new subparser.  
        """
        subparser_name = 'sd'
        sd_parser = subparser.add_parser(subparser_name, 
            formatter_class=argparse.RawTextHelpFormatter,
            help="Generate a rich diff/delta between two snapshots from a given pipeline repository and branch.",
            epilog="""
Example Usages:

    Get a simple diff between two snapshots from integration:
        python3 reporter.py sd integration integration --base-timestamp 2021-02-08-23-56-26 --new-timestamp 2021-02-09-23-34-56

    View the same diff in brief sha form: 
        python3 reporter.py sd integration integration --base-timestamp 2021-02-08-23-56-26 --new-timestamp 2021-02-09-23-34-56 -o sha

    Get a diff for a specific product version:
        python3 reporter.py sd integration integration --base-timestamp 2021-02-08-23-56-26 --new-timestamp 2021-02-09-23-34-56 --base-product-version 2.3.0 --new-product-version 2.3.0

    Generate a diff from a local file:
        python3 reporter.py sd oldmanifest.json newmanifest.json --base-repo local --new-repo local

    Generate a markdown diff between a specific timestamp and the snapshot previous to it, and output it to a file:
        python3 reporter.py sd integration integration --new-timestamp 2021-02-09-23-34-56 -o md --output-file diff.md

    Generate a markdown diff and output it to a file, specifying both timestamps:
        python3 reporter.py sd integration integration --base-timestamp 2021-02-08-23-56-26 --new-timestamp 2021-02-09-23-34-56 -o md --output-file diff.md
""")
        sd_parser.add_argument('base', metavar='base',
            help="Our 'base' manifest specificaiton.  By default it will look for a GitHub branch named <base> on the specified repo and org. If --base-repo=local is specified, we'll use this as a filepath to a local manifest file instead.")
        sd_parser.add_argument('--base-repo', choices=['github', 'local'], default="github",
            help="The type of repo to use when looking for the base manifest.  'github' will source the manifest from github, 'local' will source it from a file stored locally")
        sd_parser.add_argument('new', metavar='new',
            help="Our 'new' manifest specificaiton.  By default it will look for a GitHub branch named <new> on the specified repo and org. If --new-repo=local is specified, we'll use this as a filepath to a local manifest file instead.")
        sd_parser.add_argument('--new-repo', choices=['github', 'local'], default="github",
            help="The type of repo to use when looking for the new manifest.  'github' will source the manifest from github, 'local' will source it from a file stored locally")
        sd_parser.add_argument('--base-timestamp',
            help="Timestamp portion of a specific snapshot to be pulled from the base stage branch of the org/repo specified for use in diff.")
        sd_parser.add_argument('--new-timestamp',
            help="Timestamp portion of a specific snapshot to be pulled from the new stage branch of the org/repo specified for use in diff.")
        sd_parser.add_argument('--base-product-version', default=os.getenv('OCM_RELEASE_VERSION') if os.getenv('OCM_RELEASE_VERSION') is not None else '2.3.0', type=SnapshotDiffGenerator.product_version_type,
            help="Full Release version in the format X.Y.Z for the manifest of base_snapshot.  Used for manifest lookup. Defaults to OCM_RELEASE_VERSION environment variable value if set, '2.3.0' if not.")
        sd_parser.add_argument('--new-product-version', default=os.getenv('OCM_RELEASE_VERSION') if os.getenv('OCM_RELEASE_VERSION') is not None else '2.3.0', type=SnapshotDiffGenerator.product_version_type,
            help="Full Release version in the format X.Y.Z for the manifest of new_snapshot.  Used for manifest lookup. Defaults to OCM_RELEASE_VERSION environment variable value if set, '2.3.0' if not.")
        sd_parser.add_argument('--output-file',
            help="Path to a file where the computed snapshot diff should be output.  If ommitted, the diff will be logged to the stdout.")
        sd_parser.add_argument('-o', '--output-type', choices=['json', 'markdown', 'md', 'sha', 'default'],
            help="Output format.  Options include JSON, Markdown, component-sha list, and user-friendly terminal output.")
        sd_parser.add_argument('-org', '--github-org', default='stolostron',
            help="Name of the GitHub organization to pull manifests from.  Defaults to 'stolostron'.")
        sd_parser.add_argument('-r', '--github-repo', default='pipeline',
            help="Name of the GitHub repo to pull manifests from.  Defaults to 'pipeline'.")
        sd_parser.add_argument('--github-token', default=os.getenv('GITHUB_TOKEN'),
            help="GitHub token for access to pull manifests from pipeline repo.  Pulls from the GITHUB_TOKEN environment variable if not specified.")
        sd_parser.set_defaults(func=SnapshotDiffGenerator.generate_snapshot_diff_from_args)
        return subparser_name, sd_parser

    
    def product_version_type(arg, pattern=re.compile('[0-9]+\.[0-9]+\.[0-9]+')):
        """Validate that an argument, arg, is in the format pattern.
        
        Required Argument:
        arg -- the argument to validate against our regex

        Keyword Argument:
        pattern -- a regex pattern to apply to arg and raise an ArgumentTypeError if the parameter does not match.  Defaults to X.Y.Z.  
        """
        if not pattern.match(arg):
            raise argparse.ArgumentTypeError("...product_version parameters must be specified in the format X.Y.Z to match the regex '[0-9]+\.[0-9]+\.[0-9]+'")
        return arg


    def generate_snapshot_diff_from_args(args):
        """Static method to create a SnapshotDiffGenerator object and generate a diff in the correct format from command-line args.  

        Required Argument:
        args -- argparse-generated arguments from an argparse with a parser generated by SnapshotDiffGenerator.generate_subparser()
        """
        generator = SnapshotDiffGenerator(
            base=args.base,
            base_repo_type=args.base_repo,
            new=args.new, 
            new_repo_type=args.new_repo,
            base_timestamp=args.base_timestamp,
            new_timestamp=args.new_timestamp,
            base_product_version=args.base_product_version,
            new_product_version=args.new_product_version, 
            github_token=args.github_token,            
            github_org=args.github_org,
            github_repo=args.github_repo,
            load_commits=(not args.output_type == "sha"))
        _output = ""
        if args.output_type is None or args.output_type == "default":
            _output = generator.diff_to_terminal()                    
        elif args.output_type == "json":
            _output = generator.diff_to_json()
        elif args.output_type == "md" or args.output_type == "markdown":
            _output = generator.diff_to_md()
        elif args.output_type == "sha":
            _output = generator.diff_to_sha()
        if args.output_file is not None:
            with open(args.output_file, "w+") as f:
                f.write(_output)
        else:
            print(_output)


    def generate_snapshot_diff(self):
        """Macro function to generate our manifest objects and generate a diff dict."""
        self.base_manifest, self.base_manifest_name = self.get_manifest(self.base_repo_type, self.base, self.base_product_version, self.base_product_major_version, self.base_timestamp)
        self.new_manifest, self.new_manifest_name = self.get_manifest(self.new_repo_type, self.new, self.new_product_version, self.new_product_major_version, self.new_timestamp)
        self.diff = self.generate_component_diff(self.base_manifest, self.new_manifest)


    def get_manifest(self, source_type, source, product_version=None, product_major_version=None, timestamp=None):
        """Pulls a specific manifest from source based on the source_type configured, loads as JSON.

        Required Arguments:
        source_type -- source of the manifest, toggles between github and local
        source      -- manifest stage, either a filename for local or a timestamp for github-sourced
        product_version         -- X.Y.Z version of the product represented by the target manfiest
        product_major_version   -- X.Y version of the product represented by the target manifest

        Keyword Arguments:
        timestamp -- timestamp of the specific manifest to pull, latest snapshot from soruce is pulled if empty
        """
        _loaded_manifest = {}
        _loaded_manifest_name = None
        if source_type == "local":
            with open(source, "r") as f:
                _loaded_manifest = json.load(f)
            _loaded_manifest_name = source
        else:
            try:
                _manifest = None
                _branch = f"{product_major_version}-{source}"
                if timestamp is None: # If we aren't given a specific timestamp, grab the latest
                    _manifest = self.gh_repo.get_contents("snapshots", ref=_branch)
                    _manifest = list(filter(lambda x: "manifest" in x.name and f"{product_version}" in x.name, _manifest))
                    _manifest = sorted(_manifest, key = lambda manifest: manifest.name)
                    if len(_manifest) == 0:
                        raise RuntimeError(f"Didn't find any manifests in the snapshots directory of branch {_branch} in github.com/{self.github_org}/{self.github_repo}.")
                    _manifest = _manifest[-1]
                else: # Otherwise, grab a specific snapshot
                    _manifest = self.gh_repo.get_contents("snapshots", ref=_branch)
                    _manifest = list(filter(lambda x: x.name == f"manifest-{timestamp}-{product_version}.json", _manifest))
                    if len(_manifest) != 1:
                        raise RuntimeError(f"Didn't find any manifests in the snapshots directory of branch {_branch} in github.com/{self.github_org}/{self.github_repo} matching manifest-{timestamp}-{product_version}.json.")
                    _manifest = _manifest[0]
                _loaded_manifest = json.loads(_manifest.decoded_content)
                _loaded_manifest_name = _manifest.name
            except github.GithubException as ex:
                print(f"ERROR - Encountered an issue while trying to pull manifests from github.com/{self.github_org}/{self.github_repo}/tree/{_branch}.  Please verify your stage and product version variables.  We recieved the follwing error messaage from the GitHub API:\n{ex}")
                exit(1)
        return _loaded_manifest, _loaded_manifest_name

    
    def generate_component_diff(self, base_manifest, new_manifest):
        """Generate a dict respresenting the difference between two manifests.  

        Required Arguments:
        base_manifest -- "base" manifest for the diff, this is our "old" state so we'll note differences compared to this manifest 
        new_manifest  -- "new" manifest for the diff, this is our new state so we'll compare this state to the "base"
        """
        _diff = []
        for _base_image in base_manifest:
            # get a list of all images from the base manifest and filter for matching repository/image-name pairs
            _new_matches = list(filter(lambda _new_repo_type: _new_repo_type["git-repository"] == _base_image["git-repository"] and _new_repo_type["image-name"] == _base_image["image-name"], new_manifest))
            if len(_new_matches) < 1:
                # if there is no match (< 1 results that match), then either it was deleted or an error occurred
                _diff.append({
                    "image-name": _base_image["image-name"],
                    "git-repository": _base_image["git-repository"],
                    "image-remote": _base_image["image-remote"],
                    "operation": "deleted",
                    "base": _base_image,
                    "new": SnapshotDiffGenerator.nullary_element
                })
            elif len(_new_matches) > 1:
                # if there is more than one match, that's a problem, we check unique identifiers, mark the duplicate
                _diff.append({
                    "image-name": _base_image["image-name"],
                    "git-repository": _base_image["git-repository"],
                    "image-remote": _base_image["image-remote"],
                    "operation": "duplicate",
                    "base": _base_image,
                    "new": _new_matches
                })
            elif len(_new_matches) == 1 and _new_matches[0]["git-sha256"] != _base_image["git-sha256"]:
                # if there is one matching image but the shas don't match, image was updated
                _diff.append({
                    "image-name": _base_image["image-name"],
                    "git-repository": _base_image["git-repository"],
                    "image-remote": _base_image["image-remote"],
                    "operation": "modified",
                    "base": _base_image,
                    "new": _new_matches[0]
                })
        for _new_image in new_manifest:
            # get a list of all images from the new manifest and filter for matching repository/image-name pairs
            _base_matches = list(filter(lambda _base_repo_type: _base_repo_type["git-repository"] == _new_image["git-repository"] and _base_repo_type["image-name"] == _new_image["image-name"], base_manifest))
            if len(_base_matches) < 1:
                # if there is no match (< 1 results that match), then the component is new to our new manifest
                _diff.append({
                    "image-name": _new_image["image-name"],
                    "git-repository": _new_image["git-repository"],
                    "image-remote": _new_image["image-remote"],
                    "operation": "added",
                    "base": SnapshotDiffGenerator.nullary_element,
                    "new": _new_image
                })
        return _diff


    def load_commits_for_diff(self):
        """Loop through all components in the diff object and annotate github artifacts."""
        for _component in self.diff:
            _component["details"] = self.load_commits_for_image(_component)

    
    def load_commits_for_image(self, component):
        """Generate a dict representing the commits, PRs, and metadata for a given component's diff.

        Required Argument:
        component -- A dict representation of a component's diff between some base and new state to operate on
        """
        _gh_artifacts = {}
        if component['operation'] == 'modified':
            # derive org/repo from the image name from the manifest entry
            _org_name, _image_name = component['git-repository'].split("/")
            _org = self.gh_client.get_organization(_org_name)
            _repo = _org.get_repo(_image_name)

            # grab commits from the cooresponding shas
            _base_commit = _repo.get_commit(component['base']['git-sha256'])
            _new_commit = _repo.get_commit(component['new']['git-sha256'])

            _gh_artifacts = {
                "comapare-url": f"https://github.com/{_org}/{_repo}/compare/{component['base']['git-sha256']}..{component['new']['git-sha256']}",
                "success": True
            }

            # walk the tree from the newest commit back up to the oldest commit.  
            # we have to do this because the github api has no git log like behavior
            # if we can't walk back up the tree, some branching nonsense has occurred that
            # we don't care to accomodate, so skip this part.  
            # 
            # if we can get a path of commits, we can print each and try to link them to pull requests
            # print(f"Walking the git tree from {_new_commit.commit.sha} to find all commits between it and {_base_commit.commit.sha}")
            _commit_path = [_new_commit]
            _iter_commit = _new_commit.parents[0]
            _iter_max = 25
            _iter_count = 0
            while _iter_commit is not None and _iter_commit.sha != _base_commit.sha and _iter_count < _iter_max:
                _commit_path.append(_iter_commit)
                _iter_commit = _iter_commit.parents[0] if len(_iter_commit.parents) > 0 else None
                _iter_count = _iter_count + 1
            _commit_path.append(_base_commit)
            if _iter_commit is None:
                _commit_path = [_new_commit, _base_commit]
                _gh_artifacts["success"] = False
            _commit_list = []
            for _commit in _commit_path:
                _prs = []
                for _pr in _commit.get_pulls():
                    _pr_details = {
                        "assignees": [],
                        "title": _pr.title,
                        "body": _pr.body,
                        "html_url": _pr.html_url,
                        "merged_at": str(_pr.merged_at),
                        "merged_by": _pr.merged_by.name,
                        "number": _pr.number
                    }
                    for assignee in _pr.assignees:
                        _pr_details["assignees"].append(assignee.name)
                    _prs.append(_pr_details)
                _commit_list.append({
                    "author": _commit.commit.author.name,
                    "html_url": _commit.commit.html_url,
                    "message": _commit.commit.message,
                    "sha": _commit.commit.sha,
                    "prs": _prs
                })
            _gh_artifacts["commits"] = _commit_list
        return _gh_artifacts


    def diff_to_dict(self):
        """Return our underlying dict representation of the diff"""
        return self.diff


    def diff_to_json(self):
        """Convert our diff object into a json string."""
        return json.dumps(self.diff)


    def diff_to_sha(self):
        """Convert our diff object into a sha-focused string."""
        _sha_diff = ""
        for component in self.diff:
            if component['operation'] == "modified":
                _sha_diff = _sha_diff + f"{component['base']['git-sha256']}..{component['new']['git-sha256']}\t{component['image-name']}\n"
            elif component['operation'] == "deleted":
                _sha_diff = _sha_diff + f"{component['base']['git-sha256']}..deleted\t{component['image-name']}\n"
            elif component['operation'] == "added":
                _sha_diff = _sha_diff + f"missing..{component['new']['git-sha256']}\t{component['image-name']}\n"
            elif component['operation'] == "duplicate":
                _sha_diff = _sha_diff + f"duplicate detected\t{component['image-name']}\n"
        return _sha_diff


    def diff_to_md(self):
        """Convert our diff object into a markdown string."""
        _md_diff = f"""
# Diff Between `{self.base_manifest_name}` and `{self.new_manifest_name}`

"""
        for component in self.diff:
            if component['operation'] == "modified":
                _md_diff = _md_diff + f"""
## {component['image-name']} was modified between `{component['base']['git-sha256']}` and `{component['new']['git-sha256']}`

**Image Repo:** {component['git-repository']}

**Image Tag:** `{component['base']['image-tag']}` -> `{component['new']['image-tag']}`

### Commits
-----
"""
                if bool(component['details']['success']):
                    for commit in component['details']['commits']:
                        _md_diff = _md_diff + f"""
#### {commit["sha"]}

**Author:** {commit["author"]}

**URL:** {commit["html_url"]}

**Message:** {commit["message"]}

##### PRs
"""
                        for pr in commit['prs']:
                            _md_diff = _md_diff + f"""

###### PR #{pr['number']}

**URL:** {pr['html_url']}

**Title:** {pr['title']}

**Body:**
{pr['body']}

**Assignees:** {str(pr['assignees'])}

Merged at {pr['merged_at']} by {pr['merged_by']}
"""
                        _md_diff = _md_diff + "\n------\n"
            elif component['operation'] == "added":
                _md_diff = _md_diff + f"""
## {component['image-name']} was added between `{self.base_manifest_name}` and `{self.new_manifest_name}`

**Image Repo:** {component['git-repository']}

**Image Tag:** `{component['new']['image-tag']}`

**Git Sha:** `{component['new']['git-sha256']}`
"""
            elif component['operation'] == "deleted":
                _md_diff = _md_diff + f"""
## {component['image-name']} was deleted between `{self.base_manifest_name}` and `{self.new_manifest_name}`

**Image Repo:** {component['git-repository']}

**Image Tag:** `{component['base']['image-tag']}` -> `{component['new']['image-tag']}`

**Old Git Sha:** `{component['base']['git-sha256']}`
"""
            elif component['operation'] == "duplicate":
                _md_diff = _md_diff + f"""
## Duplicate {component['image-name']} detected

**Image Repo:** {component['git-repository']}
"""
        return _md_diff


    def diff_to_terminal(self):
        """Convert our diff object into a user-friendly terminal string."""
        col, rows = shutil.get_terminal_size((80, 20))
        _t_diff = f"""
> Diff Between `{self.base_manifest_name}` and `{self.new_manifest_name}`

"""
        for component in self.diff:
            _t_diff = _t_diff + ("=" * (col - 2)) + "\n"
            if component['operation'] == "modified":
                _t_diff = _t_diff + f"""
>> {component['image-name']} was modified between `{component['base']['git-sha256']}` and `{component['new']['git-sha256']}`
Image Repo: {component['git-repository']}
Image Tag: `{component['base']['image-tag']}` -> `{component['new']['image-tag']}`

>>> Commits
"""
                if bool(component['details']['success']):
                    for commit in component['details']['commits']:
                        _t_diff = _t_diff + f"""
>>>> {commit["sha"]}
Author: {commit["author"]}
URL: {commit["html_url"]}
Message: {commit["message"]}
PRs:
"""
                        for pr in commit['prs']:
                            _t_diff = _t_diff + f"""
    >>>>> PR #{pr['number']}
    Merged at {pr['merged_at']} by {pr['merged_by']}
    URL: {pr['html_url']}
    Title: {pr['title']}
    Body:
    {pr['body']}
    Assignees: {str(pr['assignees'])}
"""
                        _t_diff = _t_diff + "\n"
            elif component['operation'] == "added":
                _t_diff = _t_diff + f"""
>> {component['image-name']} was added between `{self.base_manifest_name}` and `{self.new_manifest_name}`
Image Repo: {component['git-repository']}
Image Tag: `{component['new']['image-tag']}`
Git Sha: `{component['new']['git-sha256']}`

"""
            elif component['operation'] == "deleted":
                _t_diff = _t_diff + f"""
>> {component['image-name']} was deleted between `{self.base_manifest_name}` and `{self.new_manifest_name}`
Image Repo: {component['git-repository']}
Image Tag: `{component['base']['image-tag']}` -> `{component['new']['image-tag']}`
Old Git Sha: `{component['base']['git-sha256']}`

"""
            elif component['operation'] == "duplicate":
                _t_diff = _t_diff + f"""
>> Duplicate {component['image-name']} detected
Image Repo: {component['git-repository']}

"""
        return _t_diff
