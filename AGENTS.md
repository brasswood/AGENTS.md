# Guidelines

## Make Discrete, Defensible Changes
This user generally wants to review changes. As such, you are encouraged to make an incremental change that justifies a single commit, pause to let the user review and commit, then continue. This is unless the user instructs otherwise in a project-level `AGENTS.md`, or above all, in chat.

One example of where this matters: Suppose that while you're working, some functionality in `lib.rs` has gotten so big that you now want to separate it into its own module. Instead of moving to a module and making major changes all in one commit, do the following: make some changes, allow the owner to review and commit, move to a new module, allow the owner to review and commit, then continue with your changes. In this example, you could also move to a new module before applying any changes; it's whatever disrupts your workflow less. The important thing is that a file move is one change that isn't mixed with a bunch of changes to the new file.

Another example: Don't mix a formatter run (such as `cargo fmt`) with another change. This includes localized formatter runs on just the files you touched, since these can still introduce noise not related to the change, e.g., if other parts of the files are not well-formatted. Generally, a formatter run should be its own commit. Don't worry much about running the formatter; it's trivial for the user to just run it themself.

## Use Typed Languages
This user prefers typed languages. Use strongly typed languages by default. For example: Use Typescript instead of Javascript whenever possible. Use type hints in Python code. For these and other gradually typed languages, always use the strictest mode of type checking available.

## Plan Mode Note
When in plan mode, if the user asks for minor changes to your proposed plan AND tells you in the same message to implement the plan with those changes, do not show the full amended plan to the user and ask them to review it. Just go ahead and implement the plan with the changes.

## Some Responses Can Be Shorter
There are a few questions this user asks for which you tend to give a longer response than they need. However, the user does not know a rule for this yet. So when the user tells you a particular response didn't need to be so long, ask them for permission to log an entry in this section of `~/.codex/AGENTS.md` summarizing the question and the response that was too long. If the user also identifies particular parts of the response that were unnecessary, include that information in the entry. Over time, this will hopefully help you and the user find a pattern of what prompts you should give abbreviated responses to.

Note that usually, your default response length is fine.
