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


def run_with_git_arguments(*arguments: str) -> subprocess.CompletedProcess[str]:
    return run_helper(
        "--subject",
        "Test forwarded arguments",
        "--message-author",
        "Codex",
        "--author",
        CODEX,
        "--human-initiator",
        CODEX,
        "--",
        *arguments,
    )


def run_test_commit(
    repository: Path, *arguments: str
) -> subprocess.CompletedProcess[str]:
    return run_helper(
        "--subject",
        "Test line limit",
        "--message-author",
        "Codex",
        "--author",
        CODEX,
        "--human-initiator",
        CODEX,
        *arguments,
        cwd=repository,
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
    def test_accepts_40_added_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            (repository / "lines.txt").write_text("line\n" * 40, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)

            result = run_test_commit(repository)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_counts_additions_and_deletions_separately(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            path = repository / "lines.txt"
            path.write_text("old\n" * 40, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)
            base = run_test_commit(repository)
            self.assertEqual(base.returncode, 0, base.stderr)
            path.write_text("new\n" * 40, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)

            result = run_test_commit(repository)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_41_added_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            base = run_test_commit(repository, "--", "--allow-empty")
            self.assertEqual(base.returncode, 0, base.stderr)
            (repository / "lines.txt").write_text("line\n" * 41, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)

            result = run_test_commit(repository)

        self.assertEqual(result.returncode, 2)
        self.assertIn("41 additions and 0 deletions", result.stderr)

    def test_records_large_change_justification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            (repository / "lines.txt").write_text("line\n" * 41, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)

            result = run_test_commit(
                repository,
                "--large-change-justification",
                "Mechanical generated fixture",
            )
            message = subprocess.run(
                ["git", "show", "-s", "--format=%B"],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("warning: allowing 41 additions", result.stderr)
        self.assertIn(
            "Large commit justification: Mechanical generated fixture\n\n"
            "Commit message authored by Codex",
            message,
        )

    def test_rejects_unnecessary_justification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            result = run_test_commit(
                repository, "--large-change-justification", "Not needed"
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("justification is unnecessary", result.stderr)

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

    def test_rejects_forwarded_author_override(self) -> None:
        result = run_with_git_arguments(f"--author={ANDREW}")

        self.assertEqual(result.returncode, 2)
        self.assertIn("must not override the author", result.stderr)

    def test_rejects_forwarded_message_options(self) -> None:
        message_options = (
            "-m", "-mText", "-amText", "--message", "--message=Text", "--no-message",
            "-F", "-Ffile", "-aFfile", "--file", "--file=file", "--no-file",
            "-c", "-cHEAD", "-acHEAD", "--reedit-message", "--no-reedit-message",
            "-C", "-CHEAD", "-aCHEAD", "--reuse-message", "--no-reuse-message",
            "--fixup", "--fixup=HEAD", "--no-fixup",
            "--squash", "--squash=HEAD", "--no-squash",
        )

        for option in message_options:
            with self.subTest(option=option):
                result = run_with_git_arguments(option)
                self.assertEqual(result.returncode, 2)
                self.assertIn("must not override the message", result.stderr)

    def test_allows_message_text_outside_option_names(self) -> None:
        for arguments in (("--", "--message"), ("-Smycommit",)):
            with self.subTest(arguments=arguments):
                result = run_with_git_arguments("--dry-run", *arguments)
                self.assertNotIn("must not override the message", result.stderr)

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
