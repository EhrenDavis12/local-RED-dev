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

**`/set-project` and `/set-system` are commands, not skills — you cannot run either.** Both
switches belong to the user alone. If one needs to change, say so and stop; do not switch, and
do not reach around the command by editing `.claude/project/active.json` or the import line
yourself. The reason is context integrity: a switch you initiated would leave the user
reasoning about one project or rule set while you work under another, and the mismatch is
invisible to them. Being told to wait is cheap; a session spent under false context is not.

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
4. `## Open Questions` — **always the last section in the file**

Other standing rules for these docs:

- **Revise in place; never keep a decision log.** When something is settled, rewrite the prose
  so it states the new answer, and delete what it replaced. Never add a "we used to do X, we
  now do Y" entry, and never leave X standing elsewhere in the doc. A design doc says what is
  being built, in the present tense, and says nothing about how it got that way.
- **Git is the audit trail.** `git log -p <doc>` already records when X became Y. A
  hand-maintained decisions section duplicates that, drifts from it, and turns every settled
  question into a contradiction someone has to keep reconciling — the docs here reached 89%
  decision-log before this rule existed. Where a rejected alternative is genuinely
  load-bearing, because knowing it prevents a regression, state the reason inline in present
  tense ("marks are drawn in code, not theme, because theme packs cannot ship layout") in the
  section it governs. That is a reason, not a ledger entry.
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

Changes to how agents work *together* — a pipeline stage, a document type, the flow itself —
start at the `/agent-builder` skill (`.claude/skills/agent-builder/`). It is the design record:
the three layers, what each agent is for, and a log of what each hard-won rule cost to learn.
Read it before proposing a flow change; `/agent-creator` then builds whatever survives. Both
are repo-level and outlive any one system.

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
   reach them — and rewrite each one so it stands alone, per "Asking the user a question"
   below. An agent's wording is addressed to you, never to the user.
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

## Talking to the user

**Default to short.** The user reads slowly and iterates fast; a wall of text gets skimmed, and
skimmed text is where things get missed. Length is a cost paid on their behalf, so spend it only
where it buys understanding. This governs conversation with the user, never project artifacts —
docs, PRDs, code, and tests keep their own conventions, and nothing here licenses shortening
the user's prose in a doc.

Brevity is a property of the answer, not of the work behind it. Do the full research, read every
file it takes, then report the conclusion. Short built on thorough is the goal; short built on a
quick look is the failure this rule must never cause.

What gets cut and what never does:

- **Lead with the answer** — the recommendation, the finding, the number, in the first line.
  Reasoning after it, and only as much of it as changes what the user would do.
- **Recommend; don't survey.** If four options were weighed and three lost, name the winner and
  say what it beats. The losers get a clause, not a paragraph each.
- **Keep every reason.** Cut hedging, preamble, restating the question, and options you won't
  pursue — never the *why*. An unexplained claim is shorter but not faster, because it costs a
  follow-up.
- **Say the bad news plainly.** Risk, breakage, "this won't work", "the tests still fail" — each
  fits in a sentence, and none of them is ever what gets trimmed.
- **End on the next decision**, worded as one question, per the section below.

**Expand when asked.** "Explain it like I'm five", "walk me through it", "more detail" — these
mean drop the compression, not say the summary again louder. Assume the user wants the short
form until they ask otherwise.

## Momentum — never stop to ask "continue?"

When the next step is already defined — by the pipeline, by a plan the user approved, or by
an agent's report — take it in the same turn. Ending a turn to announce the next step and
wait for "please continue" is the failure mode: naming the step that precisely proves you
had everything needed to take it, so the announcement cost a round trip and bought nothing.
Report progress *while* moving, in a line or two, not as a stopping point.

A turn ends only when one of these is true:

- The next step needs the user's **intent or preference** — a real question, per the
  section below. Ask it and keep working on whatever doesn't depend on the answer.
- The next action is **expensive or irreversible** and the user hasn't already authorized
  it, in this session or durably.
- **The requested work is done.** Report the outcome. Suggest what's next if useful, but as
  a recommendation you'd act on with a word — never as a menu waiting for a selection.
- You are **genuinely blocked** and research cannot unblock you.

"Shall I proceed?" against a step the user already asked for is never one of them.

## Asking the user a question

Every question put to the user must be answerable **without opening a single file.** This
applies to questions you thought of yourself and to ones relayed from an agent — and relaying
is where it usually breaks, because an agent's report is written for you, not for the user.

**Translate before you ask. Never forward a reference the user has no way to resolve.**

- No identifiers of any kind: no `R3`, `C1`, `requirement 54`, `P3-01`, `OQ-2`, no
  `board.ext:88`, no section or heading names. The user does not hold these in their head and
  should not have to go looking.
- **State the situation in terms of the thing itself** — what happens on screen, what the
  player does, what gets saved. Not what the document says about it.
- **Give the concrete options**, and say what each one would actually mean in the app.
- **Say how hard it is to change later.** Cheap and reversible, say so — that licenses a quick
  gut call instead of a careful one. Expensive or irreversible, say that too, and say why.
- One question is one question. If answering needs three decisions, ask three.

The test: could someone who has never read these docs answer it correctly? If not, rewrite it.

Worked example. An agent reports:

> **Needs your call:** C1 — R3 and R19 conflict on highlight persistence.

What reaches the user:

> When a player takes a square, it gets highlighted so you can see the last move. When that
> player moves again, should the older highlight disappear, or stay so both are visible?
> (Easy to change later — a quick call is fine.)

**Agents keep their references.** Requirement numbers and `file:line` are precise and cheap for
you to act on, and stripping them from agent reports would cost you accuracy. The translation
happens at the boundary where a human is on the other side — which is you, every time.

## The active system

Everything below this line comes from the system named here. Swapping systems means changing
this one line — and running `/set-system`, which also rewrites the `settings.json` half.

@.claude/systems/forge/SYSTEM.md
