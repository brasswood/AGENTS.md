import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "AGENTS-resources" / "commit-message.py"
CODEX = "Codex <noreply@openai.com>"


def run_helper(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


class CommitMessageTests(unittest.TestCase):
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
