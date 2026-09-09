# local-RED-dev

The local development mono repository for RED. Design docs in `Docs/<project>/`, source in
`src/<repo>/` as git submodules.

## Two switches

**Project** — what you're working on. **System** — how Claude works on it. One of each is active
at a time.

```
/set-project              show projects, pick one
/set-project ttt          switch (aliases work)

/set-system               show systems, see which is active
/set-system forge         the agent pipeline
/set-system direct        no pipeline — Claude works inline
```

**Only you can flip these.** Both are commands, not skills — Claude cannot run them, and is
told not to edit the underlying files instead. If it thinks a switch is needed it asks and
stops. Changing the active project also triggers a permission prompt, so nothing moves without
you seeing it.

**Restart Claude Code after `/set-system`.** Agents, skills, and hooks load at session start.
`/set-project` takes effect immediately.

## The systems

| System | What happens |
|---|---|
| `forge` | Claude coordinates; 10 agents do the writing. Design docs → PRD → code → tests. |
| `direct` | No agents. Claude writes everything itself. |

Under `forge`, say what you want and Claude dispatches the right agent. To tidy docs after a
brain-dump session: `/forge-tidy-docs`.

## Adding a project

```
/set-project <new-name>
```

It offers to scaffold `Docs/<name>/` with a `project.json` manifest. Answer its questions — it
won't create anything silently.

## Clone

```bash
git clone --recurse-submodules git@github.com:EhrenDavis12/local-RED-dev.git

# already cloned without --recurse-submodules?
git submodule update --init --recursive

# add a new submodule
git submodule add git@github.com:EhrenDavis12/Tic-Tac-Toe-Extreme.git src/Tic-Tac-Toe-Extreme
git submodule add git@github.com:EhrenDavis12/privacy-policy-standalone.git src/privacy-policy-standalone
```

## Where things live

```
CLAUDE.md                    repo rules; last line imports the active system
.claude/systems/             forge/ and direct/ — the swappable rule sets
.claude/project/active.json  which project is active
Docs/<project>/project.json  that project's paths
```

If a session opens complaining about a half-finished swap or a missing system, re-run
`/set-system <name>` and restart.

## New feature workflow

Once the docs for a feature are ready to build from:

1. Start a fresh Claude Code terminal.
2. `/set-system forge` — usually already set; check once if unsure.
3. `/set-project ttt` — same, usually already set.
4. `/model` and `/effort` — pick what fits the work (Opus high is the usual).
5. Optionally Shift+Tab into plan mode — forge handles planning already, so this is extra.
6. Drag and drop the feature's docs into the prompt.
7. Ask Claude to build the feature those docs describe.

