import unittest, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from generators import SnapshotDiffGenerator

class TestSnapshotDiffGenerator(unittest.TestCase):

    base_manifest = f"{os.path.dirname(os.path.abspath(__file__))}/base.json"
    new_manifest = f"{os.path.dirname(os.path.abspath(__file__))}/new.json"

    def test_local_modified(self):
        if os.path.exists(TestSnapshotDiffGenerator.base_manifest):
            os.remove(TestSnapshotDiffGenerator.base_manifest)
        with open(TestSnapshotDiffGenerator.base_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  },
  {
    "image-name": "component-2",
    "image-version": "2.0.0",
    "image-tag": "2.0.0-0000000000000000000000000000000000000000",
    "git-sha256": "0000000000000000000000000000000000000000",
    "git-repository": "dummy-github-organization/component-2",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "image-key": "component-2"
  }
]            
""")
        if os.path.exists(TestSnapshotDiffGenerator.new_manifest):
            os.remove(TestSnapshotDiffGenerator.new_manifest)
        with open(TestSnapshotDiffGenerator.new_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  },
  {
    "image-name": "component-2",
    "image-version": "2.0.1",
    "image-tag": "2.0.1-00000000000000000000ffffffffffffffffffff",
    "git-sha256": "00000000000000000000ffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-2",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:00000000000000000000000000000000ffffffffffffffffffffffffffffffff",
    "image-key": "component-2"
  }
]            
""")
        expected_diff = [
            {
                'image-name': 'component-2', 
                'git-repository': 'dummy-github-organization/component-2', 
                'image-remote': 'quay.io/dummy-quay-organization', 
                'operation': 'modified', 
                'base': {
                    'image-name': 'component-2', 
                    'image-version': '2.0.0', 
                    'image-tag': '2.0.0-0000000000000000000000000000000000000000', 
                    'git-sha256': '0000000000000000000000000000000000000000', 
                    'git-repository': 'dummy-github-organization/component-2', 
                    'image-remote': 'quay.io/dummy-quay-organization', 
                    'image-digest': 'sha256:0000000000000000000000000000000000000000000000000000000000000000', 
                    'image-key': 'component-2'
                }, 
                'new': {
                    'image-name': 'component-2', 
                    'image-version': '2.0.1', 
                    'image-tag': '2.0.1-00000000000000000000ffffffffffffffffffff', 
                    'git-sha256': '00000000000000000000ffffffffffffffffffff', 
                    'git-repository': 'dummy-github-organization/component-2', 
                    'image-remote': 'quay.io/dummy-quay-organization', 
                    'image-digest': 'sha256:00000000000000000000000000000000ffffffffffffffffffffffffffffffff', 
                    'image-key': 'component-2'
                }
            }
        ]
        generator = SnapshotDiffGenerator.SnapshotDiffGenerator(
            base=TestSnapshotDiffGenerator.base_manifest,
            base_repo_type="local",
            new=TestSnapshotDiffGenerator.new_manifest, 
            new_repo_type="local")
        self.assertEqual(generator.diff_to_dict(), expected_diff)


    def test_local_added(self):
        if os.path.exists(TestSnapshotDiffGenerator.base_manifest):
            os.remove(TestSnapshotDiffGenerator.base_manifest)
        with open(TestSnapshotDiffGenerator.base_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  }
]            
""")
        if os.path.exists(TestSnapshotDiffGenerator.new_manifest):
            os.remove(TestSnapshotDiffGenerator.new_manifest)
        with open(TestSnapshotDiffGenerator.new_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  },
  {
    "image-name": "component-2",
    "image-version": "2.0.0",
    "image-tag": "2.0.0-0000000000000000000000000000000000000000",
    "git-sha256": "0000000000000000000000000000000000000000",
    "git-repository": "dummy-github-organization/component-2",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "image-key": "component-2"
  }
]            
""")
        expected_diff = [
            {
                'image-name': 'component-2', 
                'git-repository': 'dummy-github-organization/component-2', 
                'image-remote': 'quay.io/dummy-quay-organization', 
                'operation': 'added', 
                'base': {
                    'image-name': 'null', 
                    'image-version': 'null', 
                    'image-tag': 'null', 
                    'git-sha256': 'null', 
                    'git-repository': 'null', 
                    'image-remote': 'null', 
                    'image-digest': 'null', 
                    'image-key': 'null'
                }, 
                'new':   {
                    "image-name": "component-2",
                    "image-version": "2.0.0",
                    "image-tag": "2.0.0-0000000000000000000000000000000000000000",
                    "git-sha256": "0000000000000000000000000000000000000000",
                    "git-repository": "dummy-github-organization/component-2",
                    "image-remote": "quay.io/dummy-quay-organization",
                    "image-digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
                    "image-key": "component-2"
                }
            }
        ]
        generator = SnapshotDiffGenerator.SnapshotDiffGenerator(
            base=TestSnapshotDiffGenerator.base_manifest,
            base_repo_type="local",
            new=TestSnapshotDiffGenerator.new_manifest, 
            new_repo_type="local")
        self.assertEqual(generator.diff_to_dict(), expected_diff)


    def test_local_deleted(self):
        if os.path.exists(TestSnapshotDiffGenerator.base_manifest):
            os.remove(TestSnapshotDiffGenerator.base_manifest)
        with open(TestSnapshotDiffGenerator.base_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  },
  {
    "image-name": "component-2",
    "image-version": "2.0.0",
    "image-tag": "2.0.0-0000000000000000000000000000000000000000",
    "git-sha256": "0000000000000000000000000000000000000000",
    "git-repository": "dummy-github-organization/component-2",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "image-key": "component-2"
  }
]            
""")
        if os.path.exists(TestSnapshotDiffGenerator.new_manifest):
            os.remove(TestSnapshotDiffGenerator.new_manifest)
        with open(TestSnapshotDiffGenerator.new_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  }
]            
""")
        expected_diff = [
            {
                'image-name': 'component-2', 
                'git-repository': 'dummy-github-organization/component-2', 
                'image-remote': 'quay.io/dummy-quay-organization', 
                'operation': 'deleted', 
                'base':   {
                    "image-name": "component-2",
                    "image-version": "2.0.0",
                    "image-tag": "2.0.0-0000000000000000000000000000000000000000",
                    "git-sha256": "0000000000000000000000000000000000000000",
                    "git-repository": "dummy-github-organization/component-2",
                    "image-remote": "quay.io/dummy-quay-organization",
                    "image-digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
                    "image-key": "component-2"
                },
                'new':   {
                    "image-name": "null",
                    "image-version": "null",
                    "image-tag": "null",
                    "git-sha256": "null",
                    "git-repository": "null",
                    "image-remote": "null",
                    "image-digest": "null",
                    "image-key": "null"
                }
            }
        ]
        generator = SnapshotDiffGenerator.SnapshotDiffGenerator(
            base=TestSnapshotDiffGenerator.base_manifest,
            base_repo_type="local",
            new=TestSnapshotDiffGenerator.new_manifest, 
            new_repo_type="local")
        self.assertEqual(generator.diff_to_dict(), expected_diff)


    def test_local_duplicate(self):
        if os.path.exists(TestSnapshotDiffGenerator.base_manifest):
            os.remove(TestSnapshotDiffGenerator.base_manifest)
        with open(TestSnapshotDiffGenerator.base_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  },
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  }
]            
""")
        if os.path.exists(TestSnapshotDiffGenerator.new_manifest):
            os.remove(TestSnapshotDiffGenerator.new_manifest)
        with open(TestSnapshotDiffGenerator.new_manifest, 'w+') as f:
            f.write("""
[
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  },
  {
    "image-name": "component-1",
    "image-version": "1.0.0",
    "image-tag": "1.0.0-ffffffffffffffffffffffffffffffffffffffff",
    "git-sha256": "ffffffffffffffffffffffffffffffffffffffff",
    "git-repository": "dummy-github-organization/component-1",
    "image-remote": "quay.io/dummy-quay-organization",
    "image-digest": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "image-key": "component-1"
  }
]            
""")
        expected_diff = [
            {
                'image-name': 'component-1', 
                'git-repository': 'dummy-github-organization/component-1', 
                'image-remote': 'quay.io/dummy-quay-organization', 
                'operation': 'duplicate', 
                'base': {
                    'image-name': 'component-1', 
                    'image-version': '1.0.0', 
                    'image-tag': '1.0.0-ffffffffffffffffffffffffffffffffffffffff', 
                    'git-sha256': 'ffffffffffffffffffffffffffffffffffffffff', 
                    'git-repository': 'dummy-github-organization/component-1', 
                    'image-remote': 'quay.io/dummy-quay-organization', 
                    'image-digest': 'sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 
                    'image-key': 'component-1'
                }, 
                'new': [
                    {
                        'image-name': 'component-1',
                        'image-version': '1.0.0', 
                        'image-tag': '1.0.0-ffffffffffffffffffffffffffffffffffffffff', 
                        'git-sha256': 'ffffffffffffffffffffffffffffffffffffffff', 
                        'git-repository': 'dummy-github-organization/component-1', 
                        'image-remote': 'quay.io/dummy-quay-organization', 
                        'image-digest': 'sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 
                        'image-key': 'component-1'
                    }, 
                    {
                        'image-name': 'component-1', 
                        'image-version': '1.0.0', 
                        'image-tag': '1.0.0-ffffffffffffffffffffffffffffffffffffffff', 
                        'git-sha256': 'ffffffffffffffffffffffffffffffffffffffff', 
                        'git-repository': 'dummy-github-organization/component-1', 
                        'image-remote': 'quay.io/dummy-quay-organization', 
                        'image-digest': 'sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 
                        'image-key': 'component-1'
                    }
                ]
            }, 
            {
                'image-name': 'component-1', 
                'git-repository': 'dummy-github-organization/component-1', 
                'image-remote': 'quay.io/dummy-quay-organization', 
                'operation': 'duplicate', 
                'base': {
                    'image-name': 'component-1', 
                    'image-version': '1.0.0', 
                    'image-tag': '1.0.0-ffffffffffffffffffffffffffffffffffffffff', 
                    'git-sha256': 'ffffffffffffffffffffffffffffffffffffffff', 
                    'git-repository': 'dummy-github-organization/component-1', 
                    'image-remote': 'quay.io/dummy-quay-organization', 
                    'image-digest': 'sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 
                    'image-key': 'component-1'
                }, 
                'new': [
                    {
                        'image-name': 'component-1', 
                        'image-version': '1.0.0', 
                        'image-tag': '1.0.0-ffffffffffffffffffffffffffffffffffffffff', 
                        'git-sha256': 'ffffffffffffffffffffffffffffffffffffffff', 
                        'git-repository': 'dummy-github-organization/component-1', 
                        'image-remote': 'quay.io/dummy-quay-organization', 
                        'image-digest': 'sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 
                        'image-key': 'component-1'
                    }, 
                    {
                        'image-name': 'component-1', 
                        'image-version': '1.0.0', 
                        'image-tag': '1.0.0-ffffffffffffffffffffffffffffffffffffffff', 
                        'git-sha256': 'ffffffffffffffffffffffffffffffffffffffff',
                        'git-repository': 'dummy-github-organization/component-1', 
                        'image-remote': 'quay.io/dummy-quay-organization', 
                        'image-digest': 'sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 
                        'image-key': 'component-1'
                    }
                ]
            }
        ]
        generator = SnapshotDiffGenerator.SnapshotDiffGenerator(
            base=TestSnapshotDiffGenerator.base_manifest,
            base_repo_type="local",
            new=TestSnapshotDiffGenerator.new_manifest, 
            new_repo_type="local")
        self.assertEqual(generator.diff_to_dict(), expected_diff)


    def tearDown(self):
        if os.path.exists(TestSnapshotDiffGenerator.base_manifest):
            os.remove(TestSnapshotDiffGenerator.base_manifest)
        if os.path.exists(TestSnapshotDiffGenerator.new_manifest):
            os.remove(TestSnapshotDiffGenerator.new_manifest)


if __name__ == '__main__':
    unittest.main()