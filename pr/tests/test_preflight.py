"""Exercise PR preflight against real local Git repositories without GitHub writes."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


PREFLIGHT = Path(__file__).resolve().parents[1] / "scripts" / "pr-preflight"


class PreflightTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.environment = {
            **os.environ,
            "PATH": f"{root}:{os.environ['PATH']}",
            "PR_TEST_COUNTS": "0\t0\t0",
            "PR_TEST_PERMISSION": "WRITE",
        }
        gh = root / "gh"
        gh.write_text(
            '#!/bin/sh\ncase "$1:$2" in\n'
            'repo:view) printf "fixture/repo\\tmain\\t%s\\n" "$PR_TEST_PERMISSION" ;;\n'
            'pr:list) printf "%s\\n" "$PR_TEST_COUNTS" ;;\n'
            '*) exit 99 ;;\nesac\n'
        )
        gh.chmod(0o755)
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("commit", "--allow-empty", "-m", "chore: initial commit")
        remote = root / "remote.git"
        self.git("clone", "--bare", str(self.repo), str(remote))
        self.git("remote", "add", "origin", str(remote))
        self.git("switch", "-c", "chore/minisago-5b57de87-5229-45d0-b288-e22b558d9d2a")
        self.git("commit", "--allow-empty", "-m", "fix: example change")

    def git(self, *arguments):
        return subprocess.run(
            ["git", *arguments], cwd=self.repo, env=self.environment,
            text=True, capture_output=True, check=True,
        )

    def preflight(self, code, expected):
        result = subprocess.run(
            ["bash", str(PREFLIGHT)], cwd=self.repo, env=self.environment,
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout + result.stderr)

    def test_accepts_prepared_branch_without_renaming(self):
        before = self.git("branch", "--show-current").stdout
        self.preflight(0, "PR_PREFLIGHT_OK")
        self.assertEqual(self.git("branch", "--show-current").stdout, before)

    def test_accepts_conventional_feature_branch(self):
        self.git("branch", "-m", "fix/example-change")
        self.preflight(0, "PR_PREFLIGHT_OK")

    def test_blocks_non_conventional_branch_type(self):
        self.git("branch", "-m", "minisago/5b57de87-5229-45d0-b288-e22b558d9d2a")
        self.preflight(9, "reason=invalid_branch_name")

    def test_blocks_default_branch(self):
        self.git("switch", "main")
        self.preflight(4, "reason=default_branch")

    def test_blocks_detached_head(self):
        self.git("checkout", "--detach")
        self.preflight(2, "reason=detached_head")

    def test_blocks_tracked_changes(self):
        (self.repo / "changed.txt").write_text("unfinished")
        self.git("add", "changed.txt")
        self.preflight(3, "reason=tracked_changes")

    def test_blocks_spent_branch(self):
        self.environment["PR_TEST_COUNTS"] = "1\t0\t0"
        self.preflight(5, "reason=spent_branch")

    def test_blocks_non_draft_pr(self):
        self.environment["PR_TEST_COUNTS"] = "0\t1\t0"
        self.preflight(6, "reason=non_draft_pr")

    def test_blocks_read_only_repository(self):
        self.environment["PR_TEST_PERMISSION"] = "READ"
        self.preflight(12, "reason=repository_not_writable")


if __name__ == "__main__":
    unittest.main()
