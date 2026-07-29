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
