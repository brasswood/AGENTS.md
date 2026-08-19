#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Generate a commit message that follows the 50/72 formatting rule with sign-off."""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

SUBJECT_WIDTH = 50
BODY_WIDTH = 72
AUTHOR_PREFIX = "Commit message authored by "
IDENTITY_PATTERN = re.compile(r"(?P<name>[^<>]+?) <(?P<email>[^<>\s]+@[^<>\s]+)>")


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
    change_author: Identity,
    co_authors: list[Identity],
    designers: list[Identity],
    human_initiator: Identity,
) -> list[str]:
    if change_author in co_authors:
        raise ValueError("the change author cannot also be a co-author")
    if len(set(co_authors)) != len(co_authors):
        raise ValueError("co-authors must not contain duplicates")
    if len(set(designers)) != len(designers):
        raise ValueError("designers must not contain duplicates")
    if co_authors and not designers:
        raise ValueError("at least one designer is required when co-authors are recorded")

    record_designers = bool(co_authors) or any(
        designer != change_author for designer in designers
    )
    trailers = [f"Co-authored-by: {co_author}" for co_author in co_authors]
    if record_designers:
        trailers.extend(f"Designed-by: {designer}" for designer in designers)
    if human_initiator != change_author or trailers:
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
    author: str,
    change_author: Identity,
    co_authors: list[Identity],
    designers: list[Identity],
    human_initiator: Identity,
) -> str:
    subject = validate_single_line(subject, "subject", SUBJECT_WIDTH)
    author = validate_single_line(author, "author", BODY_WIDTH - len(AUTHOR_PREFIX))
    parts = [subject]
    if body and body.strip():
        parts.extend(("", wrap_body(body)))
    parts.extend(("", f"{AUTHOR_PREFIX}{author}"))
    trailers = format_attribution_trailers(
        change_author, co_authors, designers, human_initiator
    )
    if trailers:
        parts.extend(("", *trailers))
    return "\n".join(parts) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 50/72 commit message without committing."
    )
    parser.add_argument("--subject", "--first-line", dest="subject", required=True)
    parser.add_argument("--body", help="Body prose; blank lines separate paragraphs.")
    parser.add_argument("--author", required=True, help="Agent name for the message sign-off.")
    parser.add_argument("--change-author", required=True, type=parse_identity)
    parser.add_argument("--co-author", action="append", default=[], type=parse_identity)
    parser.add_argument("--designer", action="append", default=[], type=parse_identity)
    parser.add_argument("--human-initiator", required=True, type=parse_identity)
    parser.add_argument("--output", type=Path, help="Write the message to this UTF-8 file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        message = format_message(
            args.subject,
            args.body,
            args.author,
            args.change_author,
            args.co_author,
            args.designer,
            args.human_initiator,
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if args.output:
        args.output.write_text(message, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
