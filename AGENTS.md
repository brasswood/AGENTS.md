# Guidelines

## Organize Your Work Into Commits
Commits are the atoms of change. A commit's diff and message explain one comprehensible thing that changed; a sequence of commits explains the project's evolution over time.

Edits to files **must** be expressed as a series of one or more commits, unless instructed otherwise.

Each commit must express one coherent change. A reviewer should be able to understand and verify that change independently of the other commits.

If a commit's additions or deletions exceed 40 lines, you must split it up into smaller, coherent, independently reviewable commits if at all possible. If this is difficult, it is often helpful to come up with commits that each lay one specific piece of groundwork for the overall change.

The main exception to the 40-line rule is a change that is mechanically large but conceptually small. Examples include renaming a symbol, renaming a file, updating a function's call sites as a result of changing its signature, and moving a large section of code without otherwise changing it. Such a change may be made in a single commit even if it exceeds 40 lines, but the commit must contain no other changes.

If splitting a commit leaves a function partially unimplemented, leave code comments at the unimplemented parts explaining clearly what is left to be implemented in later commits. These comments don't count toward the 40-line budget.

### Avoid Common Pitfalls When Crafting Commits
The following are common pitfalls to avoid when crafting a commit:

Do not move a section of code into a new module and implement a new feature in that section of code in the same commit. Instead, first move the intended code into the new module in one commit, then make the remaining changes in subsequent commits.

Do not run the formatter on code you didn't touch in a commit. This introduces noise not related to the change. If you want to format just your changes, use `rustfmt --file-lines` if working with Rust code. Note that `cargo fmt` does not support formatting specific lines or files.

### Follow Commit Message Authoring Guidance
When you author a git commit message, follow the 50/72 rule:

- Keep the subject line at 50 characters or fewer.
- After the subject, optionally add a blank line and a body wrapped at 72
  characters.

Capitalize the subject line. Write it in the imperative mood.

Every commit message you author must have a blank line after the body (or subject if no body) followed by `Commit message authored by <AGENT>`, where `<AGENT>` is your name, such as `Codex` or `Claude`:

> <your message>
>
> Commit message authored by <AGENT>

Prefer to use `~/.codex/AGENTS-resources/commit-message.py` to format and validate your message. Example:

```powershell
python commit-message.py `
  --subject "Add selector cache to matching" `
  --body "Add a selector cache to matching. This speeds up..." `
  --message-author Codex |
  git commit -F -
```

This will validate the subject length, wrap the body, and append the signature.

Commit messages must, at minimum, convey:

- What the commit introduces/changes (e.g., "Use a stack-allocated buffer...")
- Where the commit affects the code (e.g., "...in the CSS parser")

Insufficient:

> Expose parsed selector CSS strings

Sufficient:

> Expose parsed selector CSS strings
>
> Expose parsed selector CSS strings from selector parsing functions in
> `SelectorList`.

(If the entire sentence had fit in the subject line, no body would have been used.)

Additionally, if the commit is one out of several working toward an end goal, then the commit message must state the end goal and convey how it fits into that end goal.

Example (the end goal was, "Make the prefix interner so that it uses the CSS string that was just parsed, instead of re-serializing it"):

> Expose parsed selector CSS strings
>
> Expose parsed selector CSS strings from selector parsing functions in
> `SelectorList`. These will eventually be passed to the selector prefix
> interner to avoid expensive re-serialization of parsed `Selector`s.

After meeting the above requirements, if the commit's patchset remains abstruse, needs further justification, or uses a nonstandard approach, then elaborate even further.

Example:

> Fix the reverse function in the main module
>
> Fix the reverse function in the main module, allowing tests to pass.
>
> The root cause was comparing `Selector` objects after the big refactor;
> converting them to strings and then comparing them allowed an entry to
> be found in the `preprocessed_selector` list. The likely failure mode
> was:
>
> - Selectors contain not just their `Component`s, but also extra header
>   information such as `SpecificityAndFlags`
> - We build the preprocessed selectors list by modifying the `Components`
>   in place, but not the extra information
> - We build the `Stylist` by serializing the preprocessed selector list
>   to a stylesheet, and then re-parsing it. This updates the extra
>   information in `Selector`s that come from the stylist.
> - We compare a new `Selector` from the `Stylist` to a `Selector` from
>   the original in-place-modified list, which has the stale extra
>   information. The equality check returns false.
>
> By comparing strings, we can also now use a `HashMap` to do the reverse
> lookup instead of linear searching a vector. This has caused a
> noticeable speedup.

#### Give Proper Attribution
Each commit has one Author, zero or more Co-authors, zero or more Designers, and one Human Initiator. These must be attributed in the commit, independently of attributing the author of the commit _message_, so that others can determine provenance of the code.

First, use the following rules to determine who is what. Here, "change" means the change(s) to the file(s) introduced by the commit, not the commit message. A "party" could be you, the user, or someone else.

| Attribution | Definition |
| ----------- | ---------- |
| Author | The party that wrote the majority[^ties] of the change's _substantive text[^substantive]_ |
| Co-author | Any party other than the Author that wrote 25% or more of the change's substantive text |
| Designer | Any party that introduced a substantial part of the change's implementation solution[^implementation-solution], whether they supplied it in pseudocode, English, literal text, or another form |
| Human Initiator | The human collaborating with the agent, or the human at the beginning of a subagent chain, that ultimately instigated the work leading to change |

[^ties]: Ask the user to break ties.

[^substantive]: Substantive text is literal text that expresses the change's implementation solution, rather than ancillary text that merely supports it.

[^implementation-solution]: The implementation solution is the particular set of tools, techniques, and procedures, together with how they are used. Constraints count as part of the implementation solution only when they directly prescribe specific tools, techniques, or procedures **and** substantially determine how they are used.

Once you have determined who gets what attributions, record them in the commit in order from top to bottom as follows:

| Attribution | When to record | Method |
| ----------- | -------------- | ------ |
| Author | Always | Git commits' built-in author field (e.g., `git commit --author=<AUTHOR>`) |
| Co-author | Record all Co-authors | `Co-authored-by: <CO-AUTHOR>` commit message trailers, in descending order of how much substantive text each Co-author wrote |
| Designer | Record all Designers when any are different from the Author or when there are any Co-authors | `Designed-by: <DESIGNER>` commit message trailers, in descending order of how much of the implementation solution each Designer introduced |
| Human Initiator | Only exclude when the same as the Author and no Co-authors or Designers are recorded | `Initiated-by: <HUMAN-INITIATOR>` commit message trailer |

Name parties using Git's standard `Name <email>` format. The user's name and email are the ones configured globally in Git. You should know your name and email.

> <your message>
>
> Commit message authored by Codex
>
> Co-authored-by: Codex <noreply@openai.com>



Prefer to use `~/.codex/AGENTS-resources/commit-message.py` to add the Co-author trailer. Example:

```powershell
python commit-message.py `
  --subject "Add selector cache to matching" `
  --body "Add a selector cache to matching. This speeds up..." `
  --message-author Codex `
  --co-author-name Codex `
  --co-author-email noreply@openai.com |
  git commit -F -
```

#### Mind PowerShell Newlines
In PowerShell, do not use `\n` to represent line breaks in strings: this gets stored as the literal characters `\` and `n`. For a multiline string, use a PowerShell here-string with actual newlines or `` `n `` in an expandable string.

Since backtick is the escape character in PowerShell, escape it with another backtick when you want to write a literal backtick in an expandable string.

## Use Typed Languages
This user prefers typed languages. Use strongly typed languages by default. For example: Use Typescript instead of Javascript whenever possible. Use type hints in Python code. For these and other gradually typed languages, always use the strictest mode of type checking available.
