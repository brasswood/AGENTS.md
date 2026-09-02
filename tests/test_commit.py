import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "AGENTS-resources" / "commit.py"
CODEX = "Codex <noreply@openai.com>"
ANDREW = "Andrew Riachi <andrew.riachi@gmail.com>"


def run_helper(
    *arguments: str, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        cwd=cwd,
        env=os.environ | {
            "GIT_COMMITTER_NAME": "Test Committer",
            "GIT_COMMITTER_EMAIL": "committer@example.com",
        },
        text=True,
    )


def create_commit(*arguments: str) -> tuple[subprocess.CompletedProcess[str], str]:
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory)
        subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
        result = run_helper(*arguments, "--", "--allow-empty", cwd=repository)
        commit = subprocess.run(
            ["git", "show", "-s", "--format=%an <%ae>%n%B"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
    return result, commit.stdout


class CommitTests(unittest.TestCase):
    def test_rejects_co_author_without_designer(self) -> None:
        result = run_helper(
            "--subject",
            "Test missing designer",
            "--message-author",
            "Codex",
            "--author",
            CODEX,
            "--co-author",
            ANDREW,
            "--human-initiator",
            ANDREW,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("designer is required", result.stderr)

    def test_rejects_malformed_identity(self) -> None:
        result = run_helper(
            "--subject",
            "Test malformed identity",
            "--message-author",
            "Codex",
            "--author",
            "Codex",
            "--human-initiator",
            CODEX,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Name <email>", result.stderr)

    def test_orders_all_attribution_trailers(self) -> None:
        result, commit = create_commit(
            "--subject",
            "Test attributed change",
            "--message-author",
            "Codex",
            "--author",
            CODEX,
            "--co-author",
            ANDREW,
            "--designer",
            CODEX,
            "--designer",
            ANDREW,
            "--human-initiator",
            ANDREW,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            commit,
            f"{CODEX}\nTest attributed change\n\n"
            "Commit message authored by Codex\n\n"
            f"Co-authored-by: {ANDREW}\n"
            f"Designed-by: {CODEX}\n"
            f"Designed-by: {ANDREW}\n"
            f"Initiated-by: {ANDREW}\n\n",
        )

    def test_omits_trailers_for_self_authored_change(self) -> None:
        result, commit = create_commit(
            "--subject",
            "Test self-authored change",
            "--message-author",
            "Codex",
            "--author",
            CODEX,
            "--designer",
            CODEX,
            "--human-initiator",
            CODEX,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            commit,
            f"{CODEX}\nTest self-authored change\n\n"
            "Commit message authored by Codex\n\n",
        )
