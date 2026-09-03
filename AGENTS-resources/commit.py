#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Create a Git commit with a validated 50/72 message and attribution."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path

SUBJECT_WIDTH = 50
BODY_WIDTH = 72
CHANGE_LINE_LIMIT = 40
AUTHOR_PREFIX = "Commit message authored by "
IDENTITY_PATTERN = re.compile(r"(?P<name>[^<>]+?) <(?P<email>[^<>\s]+@[^<>\s]+)>")
MESSAGE_LONG_OPTIONS = {
    "file",
    "fixup",
    "message",
    "reedit-message",
    "reuse-message",
    "squash",
}
MESSAGE_SHORT_OPTIONS = {"F", "m", "c", "C"}
CLUSTERABLE_SHORT_OPTIONS = set("aeinopqsvz")


@dataclass(frozen=True)
class Identity:
    name: str
    email: str

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


def parse_identity(value: str) -> Identity:
    match = IDENTITY_PATTERN.fullmatch(value)
    if match is None or value != value.strip():
        raise argparse.ArgumentTypeError("identity must use the format 'Name <email>'")
    name = match.group("name")
    if name != name.strip():
        raise argparse.ArgumentTypeError(
            "identity name must not have surrounding spaces"
        )
    return Identity(name, match.group("email"))


def format_attribution_trailers(
    author: Identity,
    co_authors: list[Identity],
    designers: list[Identity],
    human_initiator: Identity,
) -> list[str]:
    if author in co_authors:
        raise ValueError("the change author cannot also be a co-author")
    if len(set(co_authors)) != len(co_authors):
        raise ValueError("co-authors must not contain duplicates")
    if len(set(designers)) != len(designers):
        raise ValueError("designers must not contain duplicates")
    if co_authors and not designers:
        raise ValueError("at least one designer is required when co-authors are recorded")

    record_designers = bool(co_authors) or any(
        designer != author for designer in designers
    )
    trailers = [f"Co-authored-by: {co_author}" for co_author in co_authors]
    if record_designers:
        trailers.extend(f"Designed-by: {designer}" for designer in designers)
    if human_initiator != author or trailers:
        trailers.append(f"Initiated-by: {human_initiator}")
    return trailers


def validate_single_line(value: str, name: str, width: int) -> str:
    if "\n" in value or "\r" in value:
        raise ValueError(f"{name} must be one line")
    if not value or value != value.strip():
        raise ValueError(f"{name} must not be empty or have surrounding spaces")
    if len(value) > width:
        raise ValueError(f"{name} must be at most {width} characters")
    return value


def wrap_body(body: str) -> str:
    paragraphs: list[str] = []
    for paragraph in re.split(r"\n\s*\n", body.strip()):
        text = " ".join(paragraph.split())
        long_word = next((word for word in text.split() if len(word) > BODY_WIDTH), None)
        if long_word is not None:
            raise ValueError(
                f"body contains a {len(long_word)}-character word; "
                f"no body word may exceed {BODY_WIDTH} characters"
            )
        paragraphs.append(
            textwrap.fill(
                text,
                width=BODY_WIDTH,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    return "\n\n".join(paragraphs)


def format_message(
    subject: str,
    body: str | None,
    message_author: str,
    author: Identity,
    co_authors: list[Identity],
    designers: list[Identity],
    human_initiator: Identity,
) -> str:
    subject = validate_single_line(subject, "subject", SUBJECT_WIDTH)
    message_author = validate_single_line(
        message_author, "message author", BODY_WIDTH - len(AUTHOR_PREFIX)
    )
    parts = [subject]
    if body and body.strip():
        parts.extend(("", wrap_body(body)))
    parts.extend(("", f"{AUTHOR_PREFIX}{message_author}"))
    trailers = format_attribution_trailers(
        author, co_authors, designers, human_initiator
    )
    if trailers:
        parts.extend(("", *trailers))
    return "\n".join(parts) + "\n"


def validate_git_arguments(arguments: list[str]) -> None:
    author_options = {
        "--author",
        "--no-author",
        "--reset-author",
        "--no-reset-author",
    }
    for argument in arguments:
        if argument == "--":
            return
        option = argument.split("=", 1)[0]
        if option in author_options:
            raise ValueError("extra Git arguments must not override the author")
        long_option = option.removeprefix("--").removeprefix("no-")
        if argument.startswith("--") and long_option in MESSAGE_LONG_OPTIONS:
            raise ValueError("extra Git arguments must not override the message")
        if argument.startswith("-") and not argument.startswith("--"):
            for short_option in argument[1:]:
                if short_option in MESSAGE_SHORT_OPTIONS:
                    raise ValueError(
                        "extra Git arguments must not override the message"
                    )
                if short_option not in CLUSTERABLE_SHORT_OPTIONS:
                    break


def count_candidate_changes(amend: bool) -> tuple[int, int]:
    revision = "HEAD^1" if amend else "HEAD"
    base_result = subprocess.run(
        ["git", "rev-parse", "--verify", revision],
        check=False,
        capture_output=True,
        text=True,
    )
    if base_result.returncode == 0:
        base = base_result.stdout.strip()
    else:
        empty_tree = subprocess.run(
            ["git", "hash-object", "-t", "tree", "--stdin"],
            check=True,
            capture_output=True,
            input="",
            text=True,
        )
        base = empty_tree.stdout.strip()
    diff = subprocess.run(
        ["git", "diff", "--cached", "--numstat", "--no-renames", base, "--"],
        check=True,
        capture_output=True,
        text=True,
    )
    additions = 0
    deletions = 0
    for line in diff.stdout.splitlines():
        added, deleted, _path = line.split("\t", 2)
        if added != "-":
            additions += int(added)
        if deleted != "-":
            deletions += int(deleted)
    return additions, deletions


def run_commit(
    message: str,
    author: Identity,
    arguments: list[str],
    large_change_justification: str | None,
) -> int:
    validate_git_arguments(arguments)
    amend = False
    for argument in arguments:
        if argument == "--":
            break
        if argument == "--amend":
            amend = True
        elif argument == "--no-amend":
            amend = False
    additions, deletions = count_candidate_changes(amend)
    is_large = additions > CHANGE_LINE_LIMIT or deletions > CHANGE_LINE_LIMIT
    if not is_large and large_change_justification is not None:
        raise ValueError("large-change justification is unnecessary")
    if is_large and large_change_justification is None:
        raise ValueError(
            f"proposed commit has {additions} additions and {deletions} deletions; "
            f"the limit is {CHANGE_LINE_LIMIT} in either direction"
        )
    if large_change_justification is not None:
        justification = validate_single_line(
            large_change_justification, "large-change justification", BODY_WIDTH
        )
        print(
            f"warning: allowing {additions} additions and {deletions} deletions: "
            f"{justification}",
            file=sys.stderr,
        )
    with tempfile.TemporaryDirectory(prefix="commit-") as directory:
        message_path = Path(directory) / "message"
        message_path.write_text(message, encoding="utf-8", newline="\n")
        result = subprocess.run(
            ["git", "commit", f"--author={author}", f"--file={message_path}", *arguments],
            check=False,
        )
    return result.returncode


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    arguments = sys.argv[1:]
    if "--" in arguments:
        separator = arguments.index("--")
        helper_arguments = arguments[:separator]
        git_arguments = arguments[separator + 1 :]
    else:
        helper_arguments = arguments
        git_arguments = []
    parser = argparse.ArgumentParser(
        description="Create a Git commit with a validated 50/72 message."
    )
    parser.add_argument("--subject", "--first-line", dest="subject", required=True)
    parser.add_argument("--body", help="Body prose; blank lines separate paragraphs.")
    parser.add_argument(
        "--message-author", required=True, help="Agent name for the message sign-off."
    )
    parser.add_argument("--author", required=True, type=parse_identity)
    parser.add_argument("--co-author", action="append", default=[], type=parse_identity)
    parser.add_argument("--designer", action="append", default=[], type=parse_identity)
    parser.add_argument("--human-initiator", required=True, type=parse_identity)
    parser.add_argument("--large-change-justification")
    return parser.parse_args(helper_arguments), git_arguments


def main() -> int:
    args, git_arguments = parse_args()
    try:
        message = format_message(
            args.subject,
            args.body,
            args.message_author,
            args.author,
            args.co_author,
            args.designer,
            args.human_initiator,
        )
        return run_commit(
            message, args.author, git_arguments, args.large_change_justification
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
