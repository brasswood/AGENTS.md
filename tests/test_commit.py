import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "AGENTS-resources" / "commit.py"
AGENT = "Agent Name <agent@example.com>"
USER = "Andrew Riachi <andrew.riachi@gmail.com>"
DEFAULT_GLOBAL_CONFIG = "[user]\nname = Andrew Riachi\nemail = andrew.riachi@gmail.com\n"


def run_helper(
    *arguments: str,
    cwd: Path | None = None,
    environment: dict[str, str | None] | None = None,
    global_config: str | None = DEFAULT_GLOBAL_CONFIG,
    global_files: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ | {
        "GIT_COMMITTER_NAME": "Test Committer",
        "GIT_COMMITTER_EMAIL": "committer@example.com",
        "AGENT_NAME": "Agent Name",
        "AGENT_EMAIL": "agent@example.com",
    }
    for key in ("AMP_URL", "AMP_THREAD_ID", "AMP_DISABLE_AMP_THREAD_TRAILER"):
        env.pop(key, None)
    with tempfile.TemporaryDirectory() as config_directory:
        global_path = Path(config_directory) / "global.gitconfig"
        global_path.write_text(global_config or "", encoding="utf-8")
        for relative_path, contents in (global_files or {}).items():
            included_path = Path(config_directory) / relative_path
            included_path.parent.mkdir(parents=True, exist_ok=True)
            included_path.write_text(contents, encoding="utf-8")
        env.setdefault("GIT_CONFIG_GLOBAL", str(global_path))
        for key, value in (environment or {}).items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *arguments],
            check=False,
            capture_output=True,
            cwd=cwd,
            env=env,
            text=True,
        )


def run_with_git_arguments(*arguments: str) -> subprocess.CompletedProcess[str]:
    return run_helper(
        "--subject",
        "Test forwarded arguments",
        "--author",
        "agent",
        "--human-initiator",
        "agent",
        "--",
        *arguments,
    )


def run_test_commit(
    repository: Path, *arguments: str
) -> subprocess.CompletedProcess[str]:
    return run_helper(
        "--subject",
        "Test line limit",
        "--author",
        "agent",
        "--human-initiator",
        "agent",
        *arguments,
        cwd=repository,
    )


def create_commit(
    *arguments: str,
    environment: dict[str, str | None] | None = None,
) -> tuple[subprocess.CompletedProcess[str], str]:
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory)
        subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
        result = run_helper(
            *arguments,
            "--",
            "--allow-empty",
            cwd=repository,
            environment=environment,
        )
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

    def test_rejects_41_deleted_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            path = repository / "lines.txt"
            path.write_text("line\n" * 41, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)
            base = run_test_commit(
                repository, "--large-change-justification", "Test fixture"
            )
            self.assertEqual(base.returncode, 0, base.stderr)
            path.unlink()
            subprocess.run(["git", "add", "--update"], cwd=repository, check=True)

            result = run_test_commit(repository)

        self.assertEqual(result.returncode, 2)
        self.assertIn("0 additions and 41 deletions", result.stderr)

    def test_amend_counts_the_complete_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            (repository / "lines.txt").write_text("line\n" * 41, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)
            base = run_test_commit(
                repository, "--large-change-justification", "Test fixture"
            )
            self.assertEqual(base.returncode, 0, base.stderr)

            result = run_test_commit(repository, "--", "--amend")

        self.assertEqual(result.returncode, 2)
        self.assertIn("41 additions and 0 deletions", result.stderr)

    def test_merge_amend_uses_the_first_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            base = run_test_commit(repository, "--", "--allow-empty")
            self.assertEqual(base.returncode, 0, base.stderr)
            main_branch = subprocess.run(
                ["git", "branch", "--show-current"], cwd=repository, check=True,
                capture_output=True, text=True,
            ).stdout.strip()
            subprocess.run(
                ["git", "checkout", "-q", "-b", "side"], cwd=repository, check=True
            )
            (repository / "lines.txt").write_text("line\n" * 41, encoding="utf-8")
            subprocess.run(["git", "add", "lines.txt"], cwd=repository, check=True)
            side = run_test_commit(
                repository, "--large-change-justification", "Test fixture"
            )
            self.assertEqual(side.returncode, 0, side.stderr)
            subprocess.run(
                ["git", "checkout", "-q", main_branch], cwd=repository, check=True
            )
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "merge", "--quiet", "--no-ff", "side", "-m", "Merge side"],
                cwd=repository, check=True,
            )

            result = run_test_commit(repository, "--", "--amend")

        self.assertEqual(result.returncode, 2)
        self.assertIn("41 additions and 0 deletions", result.stderr)

    def test_rejects_commit_content_selection(self) -> None:
        for arguments in (("--all",), ("-a",), ("--include",), ("--", "file")):
            with self.subTest(arguments=arguments):
                result = run_with_git_arguments(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertIn("must not", result.stderr)

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
            f"Commit message authored by {AGENT}",
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
            "--author",
            "agent",
            "--co-author",
            "user",
            "--human-initiator",
            "user",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("designer is required", result.stderr)

    def test_rejects_literal_identity_selector(self) -> None:
        result = run_helper(
            "--subject",
            "Test malformed selector",
            "--author",
            AGENT,
            "--human-initiator",
            "agent",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)

    def test_rejects_message_author_argument(self) -> None:
        result = run_helper(
            "--subject",
            "Test removed message author",
            "--message-author",
            "Agent Name",
            "--author",
            "agent",
            "--human-initiator",
            "agent",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_requires_agent_environment(self) -> None:
        for variable in ("AGENT_NAME", "AGENT_EMAIL"):
            with self.subTest(variable=variable):
                result = run_helper(
                    "--subject",
                    "Test missing agent setting",
                    "--author",
                    "agent",
                    "--human-initiator",
                    "agent",
                    environment={variable: None},
                )

                self.assertEqual(result.returncode, 2)
                self.assertIn("agent", result.stderr)
                self.assertIn("not configured", result.stderr)

    def test_rejects_malformed_agent_environment(self) -> None:
        result = run_helper(
            "--subject",
            "Test malformed agent setting",
            "--author",
            "agent",
            "--human-initiator",
            "agent",
            environment={"AGENT_EMAIL": "not-an-email"},
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("agent identity is invalid", result.stderr)

    def test_requires_global_user_identity(self) -> None:
        result = run_helper(
            "--subject",
            "Test missing global identity",
            "--author",
            "user",
            "--human-initiator",
            "user",
            global_config="[user]\nemail = andrew.riachi@gmail.com\n",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("global Git setting user.name is not configured", result.stderr)

    def test_agent_only_roles_do_not_require_global_user_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            (repository / "file.txt").write_text("content\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=repository, check=True)
            result = run_helper(
                "--subject",
                "Test agent-only identity",
                "--author",
                "agent",
                "--human-initiator",
                "agent",
                "--",
                "--dry-run",
                cwd=repository,
                global_config="",
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_uses_included_global_user_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "--quiet"], cwd=repository, check=True)
            (repository / "file.txt").write_text("content\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=repository, check=True)
            result = run_helper(
                "--subject",
                "Test included global identity",
                "--author",
                "user",
                "--human-initiator",
                "user",
                "--",
                "--dry-run",
                cwd=repository,
                global_config="[include]\npath = included.gitconfig\n",
                global_files={"included.gitconfig": DEFAULT_GLOBAL_CONFIG},
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_uses_user_selector_for_git_author(self) -> None:
        result, commit = create_commit(
            "--subject",
            "Test user-selected author",
            "--author",
            "user",
            "--human-initiator",
            "user",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(commit.startswith(f"{USER}\n"), commit)
        self.assertIn(f"Commit message authored by {AGENT}", commit)

    def test_rejects_overlong_agent_message_identity(self) -> None:
        result = run_helper(
            "--subject",
            "Test overlong message identity",
            "--author",
            "agent",
            "--human-initiator",
            "agent",
            environment={
                "AGENT_NAME": "An agent name that is deliberately very long",
                "AGENT_EMAIL": "agent@example.com",
            },
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("message author must be at most", result.stderr)

    def test_rejects_forwarded_author_override(self) -> None:
        result = run_with_git_arguments(f"--author={USER}")

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

    def test_orders_all_attribution_trailers(self) -> None:
        result, commit = create_commit(
            "--subject",
            "Test attributed change",
            "--author",
            "agent",
            "--co-author",
            "user",
            "--designer",
            "agent",
            "--designer",
            "user",
            "--human-initiator",
            "user",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            commit,
            f"{AGENT}\nTest attributed change\n\n"
            f"Commit message authored by {AGENT}\n\n"
            f"Co-authored-by: {USER}\n"
            f"Designed-by: {AGENT}\n"
            f"Designed-by: {USER}\n"
            f"Initiated-by: {USER}\n\n",
        )
