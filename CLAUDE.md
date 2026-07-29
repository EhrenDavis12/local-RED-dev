# local-RED-dev

The local development mono repo for RED. It holds several projects: hand-written design docs
under `Docs/<project>/`, and their source under `src/<repo>/` as git submodules.

**One project is active at a time**, and **one agent system is active at a time.** The project
decides *what* gets worked on; the system decides *how*. This file holds only what is true
regardless of which system is running — the system's own rules arrive through the import line at
the bottom, and swapping systems means swapping that line. See `.claude/systems/README.md`.

Today the only project is `tic-tac-toe` (Tic-Tac-Toe-Extreme, a recursive tic-tac-toe game — a
3x3 big board where each quadrant holds its own 3x3 board). It has **no application code yet**;
it is design documentation only, and the game is still being specified.

## `srcRoots` are git submodules

A `git diff` from the repo root shows only a **changed submodule pointer**, never the code
change inside it. Anything that scopes itself by diff must use `git -C <srcRoot> diff`. Getting
this wrong produces an empty diff and a confident "nothing to do" — a bug this repo has already
shipped once.

## The active project

Two files carry the scope, and every agent reads them before doing anything:

| File | Holds |
|---|---|
| `.claude/project/active.json` | `{ "project": "<slug>" }` — the pointer, nothing else |
| `Docs/<project>/project.json` | the manifest: `name`, `title`, `summary`, `docsRoot`, `prds`, `roadmap`, `srcRoots` (array), and optional `aliases`, `stack` and `parkingLotDocs` |

Every manifest path is repo-relative and already joined, so nothing downstream constructs a
path. **Design docs are every `.md` directly under `docsRoot`**, excluding `PRDs/`,
`roadmap.md`, and `project.json` — docs are flat there by convention.

Switch or register a project with **`/set-project`**. It validates the manifest before
activating it and echoes the resolved scope, which matters because hooks load at session start:
without that echo a mid-session switch would be invisible until restart.

A manifest may declare `aliases` — short forms that also activate it, so `/set-project ttt`
works as well as `/set-project tic-tac-toe`. **Aliases are resolved only by that command and are
never written to the pointer**, which always holds the canonical `name`. Everything downstream
matches on `name` alone and never sees an alias; that is what keeps the abbreviation a typing
convenience rather than a second identity to keep in sync.

An agent that cannot find the pointer or manifest **stops and says to run `/set-project`**
rather than guessing a path. That is deliberate — a silent fallback is how this pipeline
previously came to point at a directory that did not exist.

`project.json` is configuration, not a design doc. It belongs to `/set-project`; nothing that
edits docs touches it.

`.claude/hooks/repo-context.sh` (`SessionStart`) injects the active project and its resolved
paths, or says plainly that none is set. It is repo-level and **never gated on the active
system** — every system needs to know which project it is pointed at. It also checks that the
import line and `settings.json` still agree.

## Documentation conventions

These docs are living brain dumps. The user writes them by hand and edits them over time.
When you edit or add any doc under `Docs/`, match the existing house style:

1. `# Title`
2. `> **Status:** ...` blockquote
3. Content sections (`##`)
4. `## Decisions` — settled items, one `### sub-heading` each, answer stated in **bold**
5. `## Open Questions` — **always the last section in the file**

Other standing rules for these docs:

- **Never answer an open question yourself.** Unanswered questions stay in Open Questions,
  worded exactly as the user wrote them. Don't guess, infer, or soften a question into a
  statement.
- **Preserve the user's voice.** Don't tighten prose, fix informal phrasing, or make it
  sound more professional. Typos are fine to fix; nothing else.
- Contradictions between docs are expected and OK — flag them, don't resolve them.
- Prose wraps around column 90. Preserve existing wrapping.

These are properties of the docs, not of whichever system happens to be editing them. They hold
whether an agent writes the doc or you do. Never edit docs belonging to a project that is not
active; if they need work, switch with `/set-project` first.

## Agents

The cross-system doctrine lives at `.claude/agents/README.md` — positions, naming, wiring tiers,
and the overlap rules. Read it before proposing any new agent. Which agents exist *right now* is
a property of the active system: see its `SYSTEM.md`.

Every new or changed agent goes through the `/agent-creator` skill
(`.claude/skills/agent-creator/`). It gates on overlap with existing agents, a justified
model/effort tier, and one job per agent, and it handles installation.

An agent that is neither named in the active system's `SYSTEM.md` nor backed by a hook will not
reliably run — so adding the agent file is not the same as installing it.

### Batch and resume

This is a harness property, true of any agent including the built-in `Explore` and `Plan`.

A subagent cannot ask a question mid-run. So agents are instructed to finish what they can,
settle anything the spec or the code already answers, and return their genuine questions in one
batch rather than guessing. When one comes back blocked:

1. **Answer what you can yourself** — from the spec, the docs, or the code. Most returned
   "questions" are research, and doing that research is your job, not the user's.
2. **Batch the rest into one ask.** Only questions needing the user's intent or preference
   reach them.
3. **Resume the same agent with `SendMessage`** — refer to it by name. This restores its
   transcript, so it keeps its partial work and its reasoning.

```
SendMessage(to: "<agent-name>", message: "<the answers>")
```

**Never re-dispatch with `Agent` to continue blocked work.** A fresh agent re-reads everything
and throws away what the first run figured out — you pay full price twice and lose the partial
result.

If an agent returns questions it could have answered by reading, say so when you resume it.
Over-asking is the failure mode that makes this loop expensive.

## The active system

Everything below this line comes from the system named here. Swapping systems means changing
this one line — and running `/set-system`, which also rewrites the `settings.json` half.

@.claude/systems/forge/SYSTEM.md
