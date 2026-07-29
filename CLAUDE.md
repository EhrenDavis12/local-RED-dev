# Tic-Tac-Toe-Extreme

A recursive tic-tac-toe game — a 3x3 big board where each quadrant holds its own 3x3
board. **There is no application code yet.** This repo is currently design documentation
only; the game is still being specified.

## Repo layout

- `Docs/manual-docs/` — hand-written design docs (the real content of this repo)
- `README.md` — one-line description
- `.claude/agents/` — subagent definitions, plus `README.md` (the agent roster)
- `.claude/skills/` — project skills

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
adding the agent file is not the same as installing it. There is one hook: a `SessionStart`
check (`.claude/hooks/docs-pending.sh`) that flags uncommitted changes under `Docs/`.

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

| Territory | Only writer |
|---|---|
| `Docs/manual-docs/` and other source-of-truth docs | `forge-doc-writer` |
| `Docs/{{Project}}/PRDs/` | `forge-prd-author` |
| `Docs/{{Project}}/roadmap.md` (the doc map) | `forge-doc-writer` |
| Source code | `forge-code-writer`, then `forge-code-cleaner` |
| Tests | `forge-test-author` |

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

## Tidying the docs: `forge-doc-planner` → `forge-doc-writer`

Doc cleanup is two steps, deliberately. `forge-doc-planner` decides what should change but
**cannot edit anything**; `forge-doc-writer` edits but decides nothing. The expensive, destructive
judgment — "is this question really answered?" — therefore never holds a write tool.

**Run this whenever a doc under `Docs/` is added or edited** — after your own edits, when the
user says a question has been answered, or when they've finished a brain-dump session.

```
Agent(subagent_type: "forge-doc-planner", prompt: "Docs under Docs/ were edited — plan what needs tidying.")
```

Then hand its report, verbatim, to the forge-doc-writer:

```
Agent(subagent_type: "forge-doc-writer", prompt: "<the forge-doc-planner plan>")
```

How they behave, so you know what to expect:

- `forge-doc-planner` finds changed docs itself via `git status`/`git diff -- Docs` — you don't
  need to list files. It reads *every* doc under `Docs/` for context, because a question in
  one doc is often answered by an edit in another.
- Its report is a numbered list tagged **MOVE** / **PROMOTE** / **REMOVE** / **FORMAT**, plus
  a **Needs your call** section. Pass the whole thing through unedited — `forge-doc-writer` applies the
  tagged findings literally and is instructed to ignore **Needs your call**.
- Answered questions get promoted into `## Decisions` rather than deleted, so the answer
  survives even though the question stops cluttering Open Questions. If the decision belongs
  in a different doc, it goes there with a `<!-- Resolved: ... See <Doc> → Decisions. -->`
  breadcrumb.
- Neither ever invents an answer. Anything uncertain comes back under **Needs your call**.

**Relay the Needs your call items to the user** — those are questions only they can settle.

`forge-doc-planner` runs on Opus at xhigh effort on purpose: deciding whether a question is
*really* answered, and spotting contradictions across docs, is judgment work where a wrong
call silently destroys a design decision. Don't downgrade it, and don't skip the pair to tidy
docs inline "because it's just moving a section around." `forge-doc-writer` runs on Sonnet precisely
because the thinking already happened — if you find yourself wanting it to be smarter, the
report wasn't specific enough.
