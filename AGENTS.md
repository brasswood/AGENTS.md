# Guidelines

## Make Discrete, Defensible Changes
This user generally wants to review changes. As such, you are encouraged to make an incremental change that justifies a single commit, pause to let the user review and commit, then continue. This is unless the user instructs otherwise in a project-level `AGENTS.md`, or above all, in chat.

One example of where this matters: Suppose that while you're working, some functionality in `lib.rs` has gotten so big that you now want to separate it into its own module. Instead of moving to a module and making major changes all in one commit, do the following: make some changes, allow the owner to review and commit, move to a new module, allow the owner to review and commit, then continue with your changes. In this example, you could also move to a new module before applying any changes; it's whatever disrupts your workflow less. The important thing is that a file move is one change that isn't mixed with a bunch of changes to the new file.

Another example: Don't mix a formatter run (such as `cargo fmt`) with another change. This includes localized formatter runs on just the files you touched, since these can still introduce noise not related to the change, e.g., if other parts of the files are not well-formatted. Generally, a formatter run should be its own commit. Don't worry much about running the formatter; it's trivial for the user to just run it themself.

## Be Descriptive in Commit Messages
When you author a git commit message, follow the 50/72 rule:

- Keep the subject line at 50 characters or fewer.
- After the subject, optionally add a blank line and a body wrapped at 72
  characters.

Use no explanatory body if the subject line sufficiently explains the commit,
or if the diff itself is easy enough to read and understand. If the subject
line is not sufficient, put only enough in the body to explain the key change
or changes. Explain the motivation only when it would not be immediately
obvious to a junior SWE.

Every commit message authored by an agent must end with a blank line followed
by `Commit message authored by <AGENT>`, where `<AGENT>` is the coding agent's
name, such as `Codex` or `Claude`. Do this even when the commit would otherwise
be subject-line-only; in that case, the attribution is the only body text.

### Examples from this repository (append the required attribution to each one):
Subject-line-only:

```text
note red flag in stylist.rs
```

A short body used because the complete explanation would exceed the subject
line limit:

```text
add backwards compatibility and shape validation

Add backwards compatibility and shape validation to the report renderer.
```

A body with one or two concise explanatory paragraphs:

```text
add context bars

Add greyed out context bars to show percent of all websites each website
takes. This allows the colored bars in the collapsed website view to
take the full width, making it easier to visualize the effects of
optimizations at a glance.
```

A body listing smaller changes with bullets:

```text
use new `Optimizations` struct for `do_website`

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
bring in stylo

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
fix the reverse function

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

## Plan Mode Note
When in plan mode, if the user asks for minor changes to your proposed plan AND tells you in the same message to implement the plan with those changes, do not show the full amended plan to the user and ask them to review it. Just go ahead and implement the plan with the changes.
