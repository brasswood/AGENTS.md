# Guidelines

## Shift Your Thinking From "Editing Files" to "Crafting Commits"
Commits are the atoms of change. A commit's diff and message explain one comprehensible thing that changed; a sequence of commits explains the project's evolution over time.

Therefore, edits to files **must** be expressed as a series of one or more commits, unless instructed otherwise.

For each commit, the two most important questions are:

> Could a junior SWE familiar with the project understand what changed in under 5 minutes by reading the commit message and the diff?

and

> Could they review and independently verify the diff, possibly with help from the message, in under 5 minutes?

The answer to both these questions must be "yes" as much as possible.

Some changes are naturally this way: adding a parameter to one function, reordering operations, and adding a check are often examples of this.

Some changes produce an apparently large diff, but are in reality small: renaming a symbol, renaming a file, and moving a large section of code from one module into another without changing it are examples. Changes like these can be done in one commit, but must not be mixed with other changes in the same commit.

Some changes are too large for one commit. In this case, you must split the change into smaller commits, each one following the rules above. If this is difficult, it is often helpful to come up with commits that each lay one specific piece of groundwork for the change.

For example: Suppose you are changing a big aspect of a complex JSON schema, and it requires changing several data types in Serde structs. Instead of expressing this entire change as one commit with the message, "Update the JSON schema," split it up into multiple commits. Perhaps each commit changes only one data type, or a small set of related data types; or maybe it touches just enough of the schema to implement one specific sub-feature in the backend.

Another example: Suppose a feature or sub-feature requires changes to several functions in a deep call graph. Instead of implementing the feature across all the functions in one commit, you could split it up into several commits. Each commit could implement the feature in one function, while still keeping that function compatible with the old behavior. Once the feature is completed in all of the functions, the compatibility could be removed in another commit if desired.

Finally, some changes may be mechanically small, but conceptually big; for example, a simple yet clever algorithm like mean-of-means, or a small change to data layout that has subtle low-level implications. This is the one exception where a commit *may* take longer than 5 minutes for a junior SWE to understand and review. Lean heavily on the commit message and/or code comments to help in this scenario.

### Avoid Common Pitfalls When Crafting Commits
The following are common pitfalls to avoid when crafting a commit:

Do not move a section of code into a new module and implement a new feature in that section of code in the same commit. Instead, first move the intended code into the new module in one commit, then make the remaining changes in subsequent commits.

Do not run the formatter on code you didn't touch in a commit; this introduces noise not related to the change. If you want to format just your changes, note on Rust that `cargo fmt` does not support formatting specific lines or files; you must instead use `rustfmt --file-lines`.

## Follow Commit Message Authoring Guidance
Before authoring or proposing any commit message, read and follow
`~/.codex/AGENTS-resources/commit-message-authoring-guide.md`.

## Use Typed Languages
This user prefers typed languages. Use strongly typed languages by default. For example: Use Typescript instead of Javascript whenever possible. Use type hints in Python code. For these and other gradually typed languages, always use the strictest mode of type checking available.
