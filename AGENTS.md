# Guidelines

## Organize Your Work Into Commits
Commits are the atoms of change. A commit's diff and message explain one comprehensible thing that changed; a sequence of commits explains the project's evolution over time.

Therefore, edits to files **must** be expressed as a series of one or more commits, unless instructed otherwise.

Each commit must express one coherent change. A reviewer should be able to understand and verify that change independently of the other commits.

If a commit's additions or deletions exceed 40 lines, you must split it up into smaller, coherent, independently reviewable commits if at all possible. If this is difficult, it is often helpful to come up with commits that each lay one specific piece of groundwork for the overall change.

The exception to the 40-line rule is changes that are mechanically large but conceptually small. Examples of this include renaming a symbol, renaming a file, updating a function's call sites as a result of changing its signature, and moving a large section of code without otherwise changing it. Changes like these can be done in one commit even if it exceeds 40 lines, but they must not be mixed with any other change in the same commit.

### Avoid Common Pitfalls When Crafting Commits
The following are common pitfalls to avoid when crafting a commit:

Do not move a section of code into a new module and implement a new feature in that section of code in the same commit. Instead, first move the intended code into the new module in one commit, then make the remaining changes in subsequent commits.

Do not run the formatter on code you didn't touch in a commit; this introduces noise not related to the change. If you want to format just your changes, note on Rust that `cargo fmt` does not support formatting specific lines or files; you must instead use `rustfmt --file-lines`.

### Follow Commit Message Authoring Guidance
When you author a git commit message, follow the 50/72 rule:

- Keep the subject line at 50 characters or fewer.
- After the subject, optionally add a blank line and a body wrapped at 72
  characters.

Capitalize the subject line. Write it in the imperative mood.

Use no explanatory body if the subject line sufficiently explains the commit,
or if the diff itself is easy enough to read and understand. If the subject
line is not sufficient, put only enough in the body to explain the key change
or changes. Explain the motivation only when it would not be immediately
obvious to a junior SWE.

Every commit message authored by an agent must end with a blank line followed
by `Commit message authored by <AGENT>`, where `<AGENT>` is the coding agent's
name, such as `Codex` or `Claude`. Do this even when the commit would otherwise
be subject-line-only; in that case, the attribution is the only body text.

## Examples (append the required attribution to each one)

Subject-line-only:

```text
Note red flag in stylist.rs
```

A short body used because the complete explanation would exceed the subject
line limit:

```text
Add backwards compatibility and shape validation

Add backwards compatibility and shape validation to the report renderer.
```

A body with one or two concise explanatory paragraphs:

```text
Add context bars

Add greyed out context bars to show percent of all websites each website
takes. This allows the colored bars in the collapsed website view to
take the full width, making it easier to visualize the effects of
optimizations at a glance.
```

A body listing smaller changes with bullets:

```text
Use new `Optimizations` struct for `do_website`

- Create function `do_website_with_configured_optimizations` which takes
  as input struct `Optimizations`
- Make `WithIsConversion` and `WithDistribution` cases thin wrappers
  around this
- Create function `prepare_selectors`, which converts selectors
  according to input `Optimizations` and outputs a reverse map.
  Called by `do_website_with_configured_optimizations`.
```

A body combining prose with a list of smaller changes:

```text
Bring in stylo

Bring in stylo revision f319793c6989dba83994fbd10d560b21ad4a0c85.
- change selectors to path dependency in scraper and mach-6.
- update cssparser to 0.36.0 in scraper and mach-6 to avoid dependency
  conflict with stylo

Using a submodule this time because stylo is actively developed, it's
reasonably big, and it's reasonably separate from this project. I can
make it not a submodule later if it gets annoying.
```

An extensive body, for a change that needs substantial explanation:

```text
Fix the reverse function

Fix the reverse function, allowing tests to pass.

The root cause was comparing `Selector` objects after the big refactor;
converting them to strings and then comparing them allowed an entry to
be found in the `preprocessed_selector` list. The likely failure mode
was:

- Selectors contain not just their `Component`s, but also extra header
  information such as `SpecificityAndFlags`
- We build the preprocessed selectors list by modifying the `Components`
  in place, but not the extra information
- We build the `Stylist` by serializing the preprocessed selector list
  to a stylesheet, and then re-parsing it. This updates the extra
  information in `Selector`s that come from the stylist.
- We compare a new `Selector` from the `Stylist` to a `Selector` from
  the original in-place-modified list, which has the stale extra
  information. The equality check returns false.

By comparing strings, we can also now use a `HashMap` to do the reverse
lookup instead of linear searching a vector. This has caused a
noticeable speedup.
```

For each example above, finish the message with:

```text

Commit message authored by <AGENT>
```

## Use Typed Languages
This user prefers typed languages. Use strongly typed languages by default. For example: Use Typescript instead of Javascript whenever possible. Use type hints in Python code. For these and other gradually typed languages, always use the strictest mode of type checking available.
