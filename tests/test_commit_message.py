import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "AGENTS-resources" / "commit-message.py"
CODEX = "Codex <noreply@openai.com>"
ANDREW = "Andrew Riachi <andrew.riachi@gmail.com>"


def run_helper(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


class CommitMessageTests(unittest.TestCase):
    def test_orders_all_attribution_trailers(self) -> None:
        result = run_helper(
            "--subject",
            "Test attributed change",
            "--author",
            "Codex",
            "--change-author",
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
            result.stdout,
            "Test attributed change\n\n"
            "Commit message authored by Codex\n\n"
            f"Co-authored-by: {ANDREW}\n"
            f"Designed-by: {CODEX}\n"
            f"Designed-by: {ANDREW}\n"
            f"Initiated-by: {ANDREW}\n",
        )

    def test_omits_trailers_for_self_authored_change(self) -> None:
        result = run_helper(
            "--subject",
            "Test self-authored change",
            "--author",
            "Codex",
            "--change-author",
            CODEX,
            "--human-initiator",
            CODEX,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "Test self-authored change\n\nCommit message authored by Codex\n",
        )
