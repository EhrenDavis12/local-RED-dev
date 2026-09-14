# Ready

> **What this is:** Authorized work, in priority order. The queue takes the top line, moves
> it to Processing, and builds it.
> **Yours.** Reorder freely; the top line is what gets picked next.
> **Hints:** Lines carry `[prd|look] [S|M|L]` after triage. A line you add here yourself
> skips triage — tag it, or the queue tags it on pickup.

---
- Game Center capability: the entitlement in the Xcode project, the capability on the bundle ID through fastlane, and re-pulled provisioning profiles [look] [S] — nothing below runs without it; authenticate fails at once on a build whose profile lacks the capability, and the profiles must be regenerated after the capability is added, not before.
- Game Center bridge, part one: authenticate, session state, and find a player through Apple's matchmaker [prd] [L] — the contract every row after it calls, and sign-in timing is player-visible on first launch; a channel shaped wrong here is re-plumbed through the state layer and the fake that tests it.
- Entitlements and store gateway: the app reads what the Apple ID owns at launch and on demand, caches it, and drives the open-games limit from it — plugin, entitlement state, store gateway with a test fake, launch wiring; no buy button and no purchase UI [prd] [M]
