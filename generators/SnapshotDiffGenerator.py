from generators import AbstractGenerator

class SnapshotDiffGenerator(AbstractGenerator.AbstractGenerator):

    def generate_subparser(subparser):
        subparser_name = 'sd'
        sd_parser = subparser.add_parser(subparser_name, help="Generate a rich diff/delta between two snapshots from a given pipeline repository and branch.")
        sd_parser.add_argument('base-snapshot', metavar='BASE_SNAPSHOT',
            help="Our 'base' snapshot to compute a diff from.  This snapshot will be compared with our 'new' snapshot to calculate a diff.")
        sd_parser.add_argument('new-snapshot', metavar='NEW_SNAPSHOT',
            help="Our snapshot to compute a diff vs our base snapshot.  This snapshot will be compared with our 'base' snapshot to calculate a diff.")
        sd_parser.add_argument('-o', '--output-file', nargs=1,
            help="Path to a file where the computed snapshot diff should be output.  If ommitted, the diff will be logged to the stdout.")
        sd_parser.add_argument('-org', '--github-org', nargs=1,
            help="Name of the GitHub organization to pull manifests from.  Defaults to 'open-cluster-management'.")
        sd_parser.add_argument('-r', '--repo', nargs=1,
            help="Name of the GitHub repo to pull manifests from.  Defaults to 'pipeline'.")
        sd_parser.add_argument('--github-token', nargs=1,
            help="GitHub token for access to pull manifests from pipeline repo.  Pulls from teh GITHUB_TOKEN environment variable if not specified.")
        sd_parser.set_defaults(func=SnapshotDiffGenerator.generate_snapshot_diff)
        return subparser_name, sd_parser


    def generate_snapshot_diff(args):
        print("Snapshot Diff Generation")
        print("Printing details of invocation below.\n")
        args_dict = vars(args)
        print(f"Subparser {args.generator_name} called with arguments:")
        for attr in args_dict.keys():
            if attr != "func":
                print(f"\t{attr}: {args_dict[attr]}")

# """generate_snapshot_diff.py

# This file is simple, it forms a very rigid (fragile) script that will pull snapshot info and generate a
# nicely formatted markdown file overviewing the changed components, commits, and PRs. 

# Usage: python3 generate_snapshot_diff.py <destination-md-file> <old-snapshot> <new-snapshot>

# """

# import os, sys, json, shutil
# from github import Github

# _stage_list = [
#     "integration",
#     "edge",
#     "stable",
#     "release"
# ]

# _skipped_repos = [
#     "open-cluster-management/example-cicd-component"
# ]

# if __name__ == "__main__":

#     if len(sys.argv) < 3:
#         print("Not enough parameters\nUsage: python3 generate_snapshot_diff.py <destination-md-file> <old-snapshot> <new-snapshot>")

#     # default release version is 1.0.0... might be a bad idea to set a default but we're doing it
#     release_version = os.getenv("OCM_RELEASE_VERSION") if os.getenv("OCM_RELEASE_VERSION") is not None else "2.0.0"
#     release_major_version = os.getenv("OCM_MAJOR_RELEASE_VERSION") if os.getenv("OCM_MAJOR_RELEASE_VERSION") is not None else "2.0"

#     dest_file = sys.argv[1] # the md file to put our results in
#     snapshot1 = sys.argv[2] # first variable should be your "old" snapshot
#     snapshot2 = sys.argv[3] # second variable should be your "new" snapshot

#     g = Github(os.getenv("GITHUB_TOKEN"))
#     org = g.get_organization("open-cluster-management")
#     repo = org.get_repo("pipeline")

#     with open(dest_file, "w+") as dest:

#         if snapshot1 in _stage_list: # if someone passed in a stage name, grab the newest snapshot in that release_version-stage pipeline branch
#             m1 = repo.get_contents("snapshots", ref=f"{release_major_version}-{snapshot1}")
#             m1 = list(filter(lambda x: "manifest" in x.name and f"{release_version}" in x.name, m1))
#             m1 = sorted(m1, key = lambda manifest: manifest.name)
#             if len(m1) == 0:
#                 print(f"Found 0 manifest files in the snapshots directory of pipeline branch {release_major_version}-{snapshot1}.  Writing nullary results with and exiting.")
#                 dest.write(f"Found 0 manifest files in the snapshots directory of pipeline branch {release_major_version}-{snapshot1}.  No snapshots to compare to, so all changes are net new!")
#                 exit(0)
#             m1 = m1[len(m1) - 1]
#         else: # otherwise get the stage:snapshot that was passed in from the release_version-stage pipeline branch
#             m1_stage, m1_snapshot = snapshot1.split(":")
#             m1 = repo.get_contents("snapshots", ref=f"{release_major_version}-{m1_stage}")
#             m1 = list(filter(lambda x: x.name == f"manifest-{m1_snapshot}-{release_version}.json", m1))
#             if len(m1) != 1:
#                 print(f"Found {len(m1)} matches for manifest-{m1_snapshot}-{release_version}.json in {release_major_version}-{m1_stage} when we should've found 1.  Exiting with an error.")
#                 exit(1)
#             m1 = m1[0]

#         if snapshot2 in _stage_list: # if someone passed in a stage name, grab the newest snapshot in that release_version-stage pipeline branch
#             m2 = repo.get_contents("snapshots", ref=f"{release_major_version}-{snapshot2}")
#             m2 = list(filter(lambda x: "manifest" in x.name and f"{release_version}" in x.name, m2))
#             m2 = sorted(m2, key = lambda manifest: manifest.name)
#             if len(m2) == 0:
#                 print(f"Found 0 manifest files in the snapshots directory of pipeline branch {release_major_version}-{snapshot2}.  Writing nullary results with and exiting.")
#                 dest.write(f"Found 0 manifest files in the snapshots directory of pipeline branch {release_major_version}-{snapshot2}.  No snapshots to compare to, so all changes are net new!")
#                 exit(0)
#             m2 = m2[len(m2) - 1]
#         else: # otherwise get the stage:snapshot that was passed in from the release_version-stage pipeline branch
#             m2_stage, m2_snapshot = snapshot2.split(":")
#             m2_target = f"manifest-{m2_snapshot}-{release_version}.json"
#             m2 = repo.get_contents("snapshots", ref=f"{release_major_version}-{m2_stage}")
#             m2 = list(filter(lambda x: x.name == m2_target, m2))
#             if len(m2) != 1:
#                 print(f"Found {len(m2)} matches for {m2_target} in {release_major_version}-{m2_stage} when we should've found 1.  Exiting with an error.")
#                 exit(1)
#             m2 = m2[0]

#         # grab names and json load the decoded content (content in plain text of the manifest file)
#         m1_name = m1.name
#         m2_name = m2.name
#         m1_json = json.loads(m1.decoded_content)
#         m2_json = json.loads(m2.decoded_content)

#         for m2_image in m2_json:
#             if not m2_image["git-repository"] in _skipped_repos:
#                 # get a list of all images from manifest 1 that match the entry in manifest 1, so we can compare them.  
#                 m1_entries = list(filter(lambda repo: repo["git-repository"] == m2_image["git-repository"] and repo["image-name"] == m2_image["image-name"], m1_json))
#                 if len(m1_entries) < 1: # if there is no match (< 1 results that match), then either it was deleted or an error occurred
#                     print(f'\nImage from {m2_image["git-repository"]} was not present in {m1_name} but was present in {m2_name}.')
#                     dest.write(f'# Repo: {m2_image["git-repository"]}, Image: {m2_image["image-name"]}\n')
#                     dest.write("\n")
#                     dest.write(f'Image from {m2_image["git-repository"]} was not present in {m1_name} but was present in {m2_name}.\n')
#                     dest.write("---\n")
#                     dest.write("\n")
#                 elif len(m1_entries) > 1: # if there is more than one match, that's a problem, we check unique identifiers
#                     print(f'\nImage from {m2_image["git-repository"]} had multiple entries in {m1_name}, something is wrong!')
#                     dest.write(f'# Repo: {m2_image["git-repository"]}, Image: {m2_image["image-name"]}\n')
#                     dest.write("\n")
#                     dest.write(f'Image from {m2_image["git-repository"]} had multiple entries in {m1_name}, something is wrong!\n')
#                     dest.write("---\n")
#                     dest.write("\n")
#                 elif m1_entries[0]["git-sha256"] != m2_image["git-sha256"]: # if there is one matching image but the shas don't match, work begins
#                     print(f'\nProcessing repo named {m2_image["git-repository"]} changed between {m1_name} and {m2_name}.')
#                     m1_image = m1_entries[0]
#                     dest.write(f'# Repo: `{m2_image["git-repository"]}`, Image: `{m2_image["image-name"]}`\n')
#                     dest.write("\n")
#                     dest.write(f'Repo named `{m2_image["git-repository"]}` changed between `{m1_name}` and `{m2_name}`.\n')
#                     dest.write("\n")

#                     # derive org/repo from the image name from the manifest entry
#                     image_details = m2_image["git-repository"].split("/")
#                     org = g.get_organization(image_details[0])
#                     repo = org.get_repo(image_details[1])

#                     # grab commits from the cooresponding shas
#                     m1_commit = repo.get_commit(m1_image["git-sha256"])
#                     m2_commit = repo.get_commit(m2_image["git-sha256"])

#                     # walk the tree from the newest commit back up to the oldest commit.  
#                     # we have to do this because the github api has no git log like behavior
#                     # if we can't walk back up the tree, some branching nonsense has occurred that
#                     # we don't care to accomodate, so skip this part.  
#                     # 
#                     # if we can get a path of commits, we can print each and try to link them to pull requests
#                     print(f"Walking the git tree from {m2_commit.commit.sha} to find all commits between it and {m1_commit.commit.sha}")
#                     commit_path = [m2_commit]
#                     iter_commit = m2_commit.parents[0]
#                     iter_max = 1000
#                     iter_count = 0
#                     while iter_commit is not None and iter_commit.sha != m1_commit.sha and iter_count < iter_max:
#                         commit_path.append(iter_commit)
#                         iter_commit = iter_commit.parents[0] if len(iter_commit.parents) > 0 else None
#                         iter_count = iter_count + 1
#                     commit_path.append(m1_commit)
#                     if iter_commit is None:
#                         dest.write(f"Walked the entire commit tree up from {m2_commit.sha} without finding {m1_commit.sha}, we can't report on changes.\n")
#                     else:
#                         print(f"Listing commits between {m1_commit.commit.sha} and {m2_commit.commit.sha}")
#                         dest.write(f"## COMMITS between {m1_commit.commit.sha[:7]} and {m2_commit.commit.sha[:7]}\n\n")
#                         for commit in commit_path:
#                             dest.write(f"### Commit: {commit.commit.sha[:7]}\n\n")
#                             dest.write(f"**SHA:** {commit.commit.sha}\n\n")
#                             dest.write(f"**URL:** {commit.commit.html_url}\n\n")
#                             for pull in commit.get_pulls():
#                                 dest.write(f"**Appears in Pull Request:** {pull.html_url}\n\n")

#                                 # TODO: Currently, events don't show mentions/references to other issues, only
#                                 # References to _this_ pr from a commit.  These features should be coming to the
#                                 # api, but they're not here yet.  Here's a github community post about the linked
#                                 # issues to follow: https://github.community/t5/GitHub-API-Development-and/Get-all-issues-linked-to-a-pull-request/td-p/46955

#                                 # Here's some code I was poking around with, events and comments both omit
#                                 # any linkage information.  
#                                 # print("Events:")
#                                 # for event in pull.as_issue().get_events():
#                                 #     print(event.event)
#                                 #     if event.event == "referenced":
#                                 #         print(f"Reference: {event.commit_id}")
#                                 #     if event.event == "mentioned":
#                                 #         print(f"Mentioned by {event.commit_id}")
#                                 # print("Comments")
#                                 # for comment in pull.get_comments():
#                                 #     print(comment)
                            
#                             if len(commit.commit.message) > 0:
#                                 dest.write(f"**Message:**\n\n")
#                                 dest.write("```\n")
#                                 dest.write(commit.commit.message.replace("```", "'''"))
#                                 dest.write("\n")
#                                 dest.write("```\n\n")
#                             dest.write("---\n")
#                             dest.write("\n")

#                     # finally, generate a compare link.  
#                     dest.write(f'Compare all changes at: https://github.com/{image_details[0]}/{image_details[1]}/compare/{m1_image["git-sha256"]}..{m2_image["git-sha256"]}\n\n')
#                     dest.write("\n")
#             else:
#                 print(f'Skipping {m2_image["git-repository"]} because it\'s in our Ignored Repositories list.')
#                 dest.write(f'# Repo: {m2_image["git-repository"]}, Image: {m2_image["image-name"]}\n\n')
#                 dest.write(f'Ignoring changes in Repo named {m2_image["git-repository"]} because its in our Ignored Repositories list!\n\n')