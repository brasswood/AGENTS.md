# TODO:
- Put my own voice in AGENTS.md modifications in `c199e85423664f1c145f67bc8e9610a53f2e1c43`. Possibly reorganize around the commit script having its own section
- Diagnose why cheaper models are not using the commit helper script altogether
- Look at `85122816421b2048819df5d0e252eed07eeb60ad` in mach-6. 5.6 Terra said this commit was indivisible, I'm not sure I agree. E.g. maybe method bodies could have been filled with `todo!()` and implemented one at a time. Diagnose this and/or give this as an example option in AGENTS.md.
- change "items" to "code units" (almost certainly this was ambiguous)
- I copy/pasted prose from chat into my mach-6-paper AGENTS.md, and that was the majority of the change, yet 5.6 luna medium set the author as me when I just asked it to commit the file (which was mostly copy/pasted). I might need to add instructions to review the changes before committing so that it can tell whether it wrote the thing.
    - Update: I reset the HEAD, told it verbatim, "Whoops, I reset HEAD to the previous commit. Review the changes to AGENTS.md to determine attribution, then commit it," and it worked _flawlessly_. I will definitely add this to my global instructions now.
    - The downside is, reviewing every change will burn through tokens. Future work: make a tool that makes this easier, e.g., a review tool which somehow obtains the agents' edits and only shows the edits that the agent didn't make.
- "For this commit, an agent could still rationalize compliance by counting matches_complex_selector and matches_complex_selector_internal as the two main items, with the helper and call sites treated as collateral. But I should not have said the wording explicitly permits two behavioral changes."
    - Make clear that I mean two substantial changes followed by necessary minor collateral changes like call-site refactoring.
- "There is no required commit plan before implementation. Once the final compiling patch exists, making one commit is the easiest interpretation."
    - How should an agent do this? Codex says: it should create provisional commit plans before editing, then revise the plan as it goes.
    - Codex also says: rather than making this plan in its internal reasoning or a temporary file, publish the plan using the available task-planning mechanism.
- Add a note to apply the same method to submodules
- give concrete examples

## Done
- give more concrete tripwires (e.g. after more than 40 insertions OR 40 deletions)
- "One comprehensible thing" is definitely too subjective
- "Junior SWE two minutes" is probably too subjective
- commit messages are not doing a great job of explaining what is being done and why. Example: `5bb46af`.
    - could say that the message must ultimately convey what is being done, where in the code/what structures the thing is being done to, and why.

