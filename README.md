# AGENTS.md

`./AGENTS.md` is licensed under the MIT License (see `./LICENSE`)

`AGENTS-resources/commit-message.py` is licensed under the CC0 1.0 Universal License.

## Amp personal skill

Relevant pushes to `main` publish `AGENTS.md` and its commit-message helper as
the `global-guidance` Amp personal skill. One-time setup:

1. Create an access token in Amp **Personal Settings → Security**.
2. In this GitHub repository, create the Actions repository secret
   `AMP_API_KEY` containing that token.
3. In Amp's web-managed **Global AGENTS.md**, add this instruction once:

   > Before starting any work, load the `global-guidance` personal skill and
   > follow all of its instructions.

New threads discover a published skill automatically. Existing threads may
need to run the `reload_skills` tool before loading the updated skill.
