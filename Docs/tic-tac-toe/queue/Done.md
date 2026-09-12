# Done

> **What this is:** What shipped in the last 30 days — when, how long it took, the commit,
> and a Grafana link to that item's agent runs and cost.
> **The queue's.** Rows older than 30 days are pruned each tick; `git log` keeps the rest.
> **Hints:** The Grafana link needs the OTEL stack running (`.claude/otel/OTEL-ReadMe.md`),
> and only shows data if the session that did the work had telemetry on.

---
- 2026-09-12 · Research: Supabase as a backend for user accounts, saved user data, and purchase records — what would it take, what does it cost, and what does it change for this app? [research] · 0h 4m · 4ecc507 · http://localhost:3000/d/claude-agents?from=1789157928000&to=1789158185000
  - A: Not needed if the two real needs behind it are solved without it — (1) knowing
    which themes were paid for, which Apple's own purchase records cover, and (2) online
    player-vs-player. Both are now their own research items in Ready; Supabase comes
    back only if that research says nothing else works. (relayed from the user, 2026-09-12)
