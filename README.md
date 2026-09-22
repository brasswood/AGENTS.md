# AGENTS.md

`./AGENTS.md` is licensed under the MIT License (see `./LICENSE`)

`AGENTS-resources/commit.py` is licensed under the CC0 1.0 Universal License.

## Amp personal skill

Relevant pushes to `main` publish `AGENTS.md` and its commit helper as
the `global-guidance` Amp personal skill. One-time setup:

1. Create an access token in Amp **Personal Settings → Security** for each
   account.
2. In this GitHub repository, create these Actions repository secrets:
   - `AMP_API_KEY_GMAIL` containing the token for the Gmail account.
   - `AMP_API_KEY_UTAH` containing the token for the Utah account.
3. In Amp's web-managed **Global AGENTS.md**, add this instruction once:

   > Before starting any work, load the `global-guidance` personal skill and
   > follow all of its instructions.

New threads discover a published skill automatically. Existing threads may
need to run the `reload_skills` tool before loading the updated skill.
