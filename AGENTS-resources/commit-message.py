#!/usr/bin/env python3
"""Generate a commit message that follows the 50/72 formatting rule with sign-off."""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path

SUBJECT_WIDTH = 50
BODY_WIDTH = 72
AUTHOR_PREFIX = "Commit message authored by "


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


def format_message(subject: str, body: str | None, author: str) -> str:
    subject = validate_single_line(subject, "subject", SUBJECT_WIDTH)
    author = validate_single_line(author, "author", BODY_WIDTH - len(AUTHOR_PREFIX))
    parts = [subject]
    if body and body.strip():
        parts.extend(("", wrap_body(body)))
    parts.extend(("", f"{AUTHOR_PREFIX}{author}"))
    return "\n".join(parts) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 50/72 commit message without committing."
    )
    parser.add_argument("--subject", "--first-line", dest="subject", required=True)
    parser.add_argument("--body", help="Body prose; blank lines separate paragraphs.")
    parser.add_argument("--author", required=True, help="Agent name for the required sign-off.")
    parser.add_argument("--output", type=Path, help="Write the message to this UTF-8 file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        message = format_message(args.subject, args.body, args.author)
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
