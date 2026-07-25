# Guidelines

## Make Discrete, Defensible Changes
This user generally wants to review changes. As such, you are encouraged to make an incremental change that justifies a single commit, pause to let the user review and commit, then continue. This is unless the user instructs otherwise in a project-level `AGENTS.md`, or above all, in chat.

One example of where this matters: Suppose that while you're working, some functionality in `lib.rs` has gotten so big that you now want to separate it into its own module. Instead of moving to a module and making major changes all in one commit, do the following: make some changes, allow the owner to review and commit, move to a new module, allow the owner to review and commit, then continue with your changes. In this example, you could also move to a new module before applying any changes; it's whatever disrupts your workflow less. The important thing is that a file move is one change that isn't mixed with a bunch of changes to the new file.

Another example: Don't mix a formatter run (such as `cargo fmt`) with another change. This includes localized formatter runs on just the files you touched, since these can still introduce noise not related to the change, e.g., if other parts of the files are not well-formatted. Generally, a formatter run should be its own commit. Don't worry much about running the formatter; it's trivial for the user to just run it themself.

## Follow Commit Message Authoring Guidance
Before authoring or proposing any commit message, read and follow
`~/.codex/AGENTS-resources/commit-message-authoring-guide.md`.

## Use Typed Languages
This user prefers typed languages. Use strongly typed languages by default. For example: Use Typescript instead of Javascript whenever possible. Use type hints in Python code. For these and other gradually typed languages, always use the strictest mode of type checking available.
