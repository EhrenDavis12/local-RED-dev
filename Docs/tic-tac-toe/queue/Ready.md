# Ready

> **What this is:** Authorized work, in priority order. The queue takes the top line, moves
> it to Processing, and builds it.
> **Yours.** Reorder freely; the top line is what gets picked next.
> **Hints:** Lines carry `[prd|look] [S|M|L]` after triage. A line you add here yourself
> skips triage — tag it, or the queue tags it on pickup.

---
- Game over online: report the outcome, end the match, and make the rematch button start the next match in the same series [prd] [M] — paused 2026-09-17 until online play is tested on two real phones
- The network scan the tech design claims, with StoreKit and GameKit as the two sanctioned paths, and the doc's "not built" prose revised [look] [S] — the scan does not exist in the suite at all, so the rule the docs call checked is currently only asserted in prose.
- Entitlements and store gateway: the app reads what the Apple ID owns at launch and on demand, caches it, and drives the open-games limit from it — plugin, entitlement state, store gateway with a test fake, launch wiring; no buy button and no purchase UI [prd] [M]
