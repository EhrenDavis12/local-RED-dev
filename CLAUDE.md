# local-RED-dev

The local development mono repo for RED. It holds several projects: hand-written design docs
under `Docs/<project>/`, and their source under `src/<repo>/` as git submodules.

**One project is active at a time.** Every `forge-*` agent resolves its paths from that
project's manifest rather than from anything hardcoded — see **The active project** below.

Today the only project is `tic-tac-toe` (Tic-Tac-Toe-Extreme, a recursive tic-tac-toe game —
a 3x3 big board where each quadrant holds its own 3x3 board). It has **no application code
yet**; it is design documentation only, and the game is still being specified.

## The active project

Two files carry the scope, and every forge agent reads them before doing anything:

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

A manifest may declare `aliases` — short forms that also activate it, so
`/set-project ttt` works as well as `/set-project tic-tac-toe`. **Aliases are
resolved only by that command and are never written to the pointer**, which always holds the
canonical `name`. Everything downstream matches on `name` alone and never sees an alias; that
is what keeps the abbreviation a typing convenience rather than a second identity to keep in
sync.

An agent that cannot find the pointer or manifest **stops and says to run
`/set-project`** rather than guessing a path. That is deliberate — a silent fallback is
how this pipeline previously came to point at a directory that did not exist.

`project.json` is configuration, not a design doc. It belongs to `/set-project`;
`forge-doc-writer` and `forge-doc-planner` both leave it alone.

When you dispatch a forge agent, state the resolved paths in the prompt. The agent reads the
manifest itself and that read is authoritative — passing them just saves it a round trip.

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

## Agents

The roster lives at `.claude/agents/README.md` — read it before proposing any new agent.

Every new or changed agent goes through the `/agent-creator` skill
(`.claude/skills/agent-creator/`). It gates on overlap with existing agents, a justified
model/effort tier, and one job per agent, and it handles installation.

An agent that is neither named in this file nor backed by a hook will not reliably run — so
adding the agent file is not the same as installing it. There are two `SessionStart` hooks:

- `.claude/hooks/repo-context.sh` — injects the active project and its resolved paths,
  or says plainly that none is set.
- `.claude/hooks/docs-pending.sh` — flags uncommitted design-doc changes in the active
  project's `docsRoot`. It skips `PRDs/`, `roadmap.md`, and `project.json`, which are not
  `forge-doc-planner`'s territory.

### Pure delegation — you coordinate, agents produce

**You never produce or modify a project artifact.** Every change to source, tests, design
docs, or PRDs goes through the agent that owns that territory. You coordinate and hold the end
goal — the one thing no subagent can do, and the thing that degrades as your context fills
with implementation detail.

The line is **produce/modify vs. read/decide**. You decide what happens next, dispatch agents,
read their reports, research answers to their questions, and talk to the user. Read whatever
you need. Just don't write.

Three carve-outs, because they aren't project artifacts:

- **`.claude/**` and `CLAUDE.md`** — the agent system itself, via `/agent-creator`. Delegating
  it would need an agent to build agents.
- **Git operations** — commits and branches are coordination, not authorship.
- **Anything the user explicitly asks you to do inline** — their call overrides this.

Neither ambiguity nor tight iteration is a reason to keep work inline anymore: the first is
handled by batch-and-resume below, the second by `SendMessage` resuming an agent with its
context rather than restarting it.

**The trivial change is the trap.** Delegating a one-line fix costs one dispatch; doing it
inline costs the boundary. "I'll just do this one" is how you drift back into being an
forge-code-writer, and you won't notice until your context is already full.

### Batch and resume

Agents are instructed to finish what they can, settle anything the spec or code already
answers, and return their genuine questions in one batch rather than guessing. When one comes
back blocked:

1. **Answer what you can yourself** — from the PRD, the design docs, or the code. Most
   returned "questions" are research, and doing that research is your job, not the user's.
2. **Batch the rest into one ask.** Only questions needing the user's intent or preference
   reach them.
3. **Resume the same agent with `SendMessage`** — refer to it by name. This restores its
   transcript, so it keeps its partial work and its reasoning.

```
SendMessage(to: "forge-code-writer", message: "<the answers>")
```

**Never re-dispatch with `Agent` to continue blocked work.** A fresh agent re-reads the PRD,
re-reads the code, and throws away everything the first run figured out — you pay full price
twice and lose the partial result.

If an agent returns questions it could have answered by reading, say so when you resume it.
Over-asking is the failure mode that makes this loop expensive.

### The write boundary

Judgment and write access are held by different agents on purpose. One writer per territory:

Paths below are manifest keys, resolved per active project.

| Territory | Only writer |
|---|---|
| Design docs — `.md` directly under `docsRoot` | `forge-doc-writer` |
| `prds` | `forge-prd-author` |
| `roadmap` (the doc map) | `forge-doc-writer` |
| Source code under `srcRoots` | `forge-code-writer`, then `forge-code-cleaner` |
| Tests under `srcRoots` | `forge-test-author` |
| `project.json` | `/set-project` (configuration, not a doc) |

Five agents are read-only and report instead. When adding an agent, default to read-only —
write access has to be argued for.

Two separations are load-bearing and must not be collapsed for convenience: `forge-code-writer`
never writes tests (an author's own tests assert what was built, not what was specified), and
`forge-test-author` never edits source (fixing the code to pass your own test destroys the signal).

### The feature pipeline

```
forge-prd-author → forge-prd-reviewer → forge-code-writer → forge-code-cleaner → forge-code-reviewer
                                ↕                        forge-prd-alignment
                          forge-test-author → forge-test-auditor
```

Don't skip `forge-prd-reviewer`. Everything downstream treats the PRD as its specification, so an
ambiguity there gets copied into every agent that reads it — and none of them can ask you
about it.

## Tidying the docs

**Run the `forge-tidy-docs` skill whenever a design doc is added or edited** — after your own
edits, when the user says a question has been answered, or when they've finished a brain-dump
session. It runs `forge-doc-planner` (decides, cannot edit) and then `forge-doc-writer`
(edits, decides nothing), and explains what to expect from each.

## Docs conventions and the active project

The house style above applies to the design docs of whichever project is active. `roadmap.md`
is generated by `forge-doc-writer` and does not follow it — it is an index of where things
live, not a doc to hand-edit. Never edit docs belonging to a project that is not active; if
they need work, switch with `/set-project` first.
