# Guidelines

## Organize Your Work Into Commits
Commits are the atoms of change. A commit's diff and message explain one comprehensible thing that changed; a sequence of commits explains the project's evolution over time.

Record all file edits in one or more commits. If the project is not a Git repository, initialize one before editing files. Fully reproducible generated artifacts may remain untracked, as described below.

Each commit must express one coherent change. A reviewer should be able to understand and verify that change independently of the other commits.

Limit each commit to at most 40 added lines and at most 40 deleted lines, subject to the exceptions below. Split larger changes into smaller, coherent, independently reviewable commits. Meeting this limit takes priority over keeping intermediate revisions compiling and working.

For example, if making `A` call a new function `B` and implementing `B` would exceed the limit, first commit the changes to `A` with a stub for `B` (e.g., `todo!()`). Implement `B` in later commits, keeping each commit within the limit.

If a commit leaves a definition (such as a function, struct, or trait) stubbed out or partially implemented, comment each unfinished section to explain the work deferred to later commits. This requirement applies only to definitions already introduced, not to definitions planned for future commits.

Prefer to implement features from the outside in. Order commits to begin with user-facing code or higher-level callers, depending on the context, then work progressively inward toward supporting code or lower-level callees.

### Exceptions to Tracking and the 40-Line Limit
Generated artifacts may remain untracked if they can be fully reproduced from tracked sources.

Exclude the following additions and deletions when applying the 40-line limit:

- Changes to tracked generated artifacts that can be fully reproduced from tracked sources, provided the artifact changes result from source changes that comply with the 40-line rule.
- Comments explaining work deferred at unfinished definitions, as required above.

The following changes may exceed the 40-line limit. Make each such change in its own commit, with no other changes:

- Rename a symbol.
- Change a function's signature and update its call sites accordingly.
- Move a section of code without modifying it or changing its behavior, such as moving a function to another module.

These are the only exceptions to the 40-line rule. If a proposed commit would exceed the limit and does not clearly qualify for an exception above, discuss it with the user before proceeding.

### Avoid Common Pitfalls When Crafting Commits
If you move a section of code for organizational purposes, do not make any other changes to the repository in the same commit.

Do not rename a file and modify its contents in the same commit.

Do not run the formatter on code you didn't touch in a commit. This introduces noise not related to the change. If you want to format just your changes, use `rustfmt --file-lines` if working with Rust code. Note that `cargo fmt` does not support formatting specific lines or files.

### Create Commits with `commit.py`

Prefer the bundled `commit.py` helper for creating commits. When loaded from
the `global-guidance` skill, resolve `scripts/commit.py` relative to the skill
directory. Otherwise, use
`<AGENT_GLOBAL_CONFIG_DIR>/AGENTS-resources/commit.py`.

Stage the exact contents first, then invoke the helper. Example:

```powershell
python commit.py `
  --subject "..." `
  --body "..." `
  --message-author agent `
  --author agent `
  --human-initiator user
```

The helper accepts:

- `--subject` (also `--first-line`)
- `--body`
- `--message-author agent|user`
- `--author agent|user`
- repeatable `--co-author agent|user`
- repeatable `--designer agent|user`
- `--human-initiator agent|user`
- `--large-change-justification`
- additional Git options after `--`

The helper reads the agent's Git identity from the environment variables `AGENT_NAME` and `AGENT_EMAIL`. It reads the user's identity from global Git configuration (`user.name` and `user.email`). Do not set any of these values yourself. If the helper fails because some of them are not set, ask the user to set them.

The helper rejects content-selection arguments such as `--all` and pathspecs
so that it can check the staged index. It refuses a commit with more than 40
additions or deletions. If that numerical check exceeds the limit but this
guidance still permits the commit, pass `--large-change-justification` with a
concise reason. The helper records that reason in the commit message. Do not
use the override merely because a larger change has already been written.

Arguments after `--` are forwarded to `git commit`. Do not forward content
selection, author, or message-source options; the helper supplies or validates
those concerns. For `--amend`, the helper measures the complete replacement
commit against its first parent.

The following sections explain message formatting and attribution. Much of this, but not all of it, is handled by the helper.

### Follow Commit Message Authoring Guidance
When you author a git commit message, keep the subject line at 50 characters
or fewer.

Write the subject in the imperative mood and capitalize it.

Commit messages must, at minimum, convey:

- What the commit introduces/changes (e.g., "Use a stack-allocated buffer...")
- Where the commit affects the code (e.g., "...in the CSS parser")

Insufficient:

> Expose parsed selector CSS strings

Sufficient:

> Expose parsed selector CSS strings
> 
> Expose parsed selector CSS strings from selector parsing functions in `SelectorList`.

(If the entire sentence fits in the subject line, no body is needed.)

Additionally, if the commit is one out of several working toward an end goal, then the commit message must state the end goal and convey how it fits into that end goal.

Example (the end goal was, "Make the prefix interner so that it uses the CSS string that was just parsed, instead of re-serializing it"):

> Expose parsed selector CSS strings
>
> Expose parsed selector CSS strings from selector parsing functions in `SelectorList`. These will eventually be passed to the selector prefix interner to avoid expensive re-serialization of parsed `Selector`s.

After meeting the above requirements, if the commit's patchset remains abstruse, needs further justification, or uses a nonstandard approach, then elaborate even further.

Example:

> Fix the reverse function in the main module
>
> Fix the reverse function in the main module, allowing tests to pass.
>
> The root cause was comparing `Selector` objects after the big refactor; converting them to strings and then comparing them allowed an entry to be found in the `preprocessed_selector` list. The likely failure mode was:
>
> - Selectors contain not just their `Component`s, but also extra header information such as `SpecificityAndFlags`
> - We build the preprocessed selectors list by modifying the `Components` in place, but not the extra information
> - We build the `Stylist` by serializing the preprocessed selector list to a stylesheet, and then re-parsing it. This updates the extra information in `Selector`s that come from the stylist.
> - We compare a new `Selector` from the `Stylist` to a `Selector` from the original in-place-modified list, which has the stale extra information. The equality check returns false.
>
> By comparing strings, we can also now use a `HashMap` to do the reverse lookup instead of linear searching a vector. This has caused a noticeable speedup.

#### Give Proper Attribution
Each commit has one Author, zero or more Co-authors, zero or more Designers, and one Human Initiator. These must be attributed in the commit, independently of attributing the author of the commit _message_, so that others can determine the provenance of the change.

First, use the following rules to determine who is what. Here, "change" means the change(s) to the file(s) introduced by the commit, not the commit message. A "party" could be you, the user, or someone else. A party "wrote" text when they introduced that literal text to the collaboration, regardless of who entered it into the change.

| Attribution | Definition |
| ----------- | ---------- |
| Author | The party that wrote the majority[^ties] of the change's _substantive text[^substantive]_ |
| Co-author | Any party other than the Author that wrote 25% or more of the change's substantive text |
| Designer | Any party that introduced a substantial part of the change's _implementation solution[^implementation-solution]_, whether they supplied it in pseudocode, English, literal text, or another form |
| Human Initiator | The human collaborating with the agent, or the human at the beginning of a subagent chain, that ultimately instigated the work leading to change |

[^implementation-solution]: The implementation solution is the specific set of internal tools, techniques, procedures, and structures that constitute the change, even when they are not code.

[^substantive]: Substantive text is literal text that expresses the change's implementation solution, rather than ancillary text that merely supports it.

[^ties]: Ask the user to break ties.

Once you have determined who gets what attributions, provide those roles to
`commit.py`. For example:

```powershell
python commit.py `
  --subject "Add selector cache to matching" `
  --body "Add a selector cache to matching. This speeds up..." `
  --message-author agent `
  --author agent `
  --co-author user `
  --designer agent `
  --designer user `
  --human-initiator user
```

#### Mind PowerShell Newlines
In PowerShell, do not use `\n` to represent line breaks in strings: this gets stored as the literal characters `\` and `n`. For a multiline string, use a PowerShell here-string with actual newlines or `` `n `` in an expandable string.

Since backtick is the escape character in PowerShell, escape it with another backtick when you want to write a literal backtick in an expandable string.

## Use Typed Languages
This user prefers typed languages. Use strongly typed languages by default. For example: Use Typescript instead of Javascript whenever possible. Use type hints in Python code. For these and other gradually typed languages, always use the strictest mode of type checking available.

## Write Technical Prose with Progressive Elaboration
Use the inverted-pyramid, or progressive-elaboration, principle when writing technical prose: lead with the main purpose, conclusion, or actionable instruction, then provide the explanation needed to understand or apply it. Put supporting rationale, background, caveats, examples, and implementation details after the material they explain, so a reader can stop early and still retain the essential point.

Organize information by the reader's needs and by conceptual dependency, not by the order in which you discovered or generated it. Introduce a concept before discussing its mechanics or exceptions, and keep qualifications near the claims they qualify. Before finalizing, check each paragraph's placement: move it later if it explains material introduced later, and move it earlier if readers need it to interpret an earlier point.
