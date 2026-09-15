# Ready

> **What this is:** Authorized work, in priority order. The queue takes the top line, moves
> it to Processing, and builds it.
> **Yours.** Reorder freely; the top line is what gets picked next.
> **Hints:** Lines carry `[prd|look] [S|M|L]` after triage. A line you add here yourself
> skips triage — tag it, or the queue tags it on pickup.

---
- Parental gate [prd] [M] — the Kids Category requires it before any purchase and it must be enforced at the purchase itself, so a gate that can be reached around is an App Review rejection rather than a bug.
- "Play online" on the main menu, behind the parental gate [look] [S] — the button the user asked for; depends on the "Parental gate" row already in Proposed, which is not built, and makes the menu five buttons where the docs settle four.
- Game Center bridge, part two: end a turn with the board, receive the opponent's turn, quit and resign [prd] [M] — this is the move itself crossing the wire, and a turn sent twice or applied twice leaves two phones holding different boards, which no test catches after the fact.
- The board screen drives a remote turn: input locked when it is not your turn, confirm sends, an arriving turn replaces the board [prd] [M] — decides which board wins when a remote turn lands on a local pending selection, and getting it wrong overwrites a player's move or corrupts the saved series.
- Online games in the Open Games list: your turn, waiting on them, and which games are online [look] [M] — a player cannot open a game they cannot play without knowing why, and the list is the only place an invited match first appears.
- Game over online: report the outcome, end the match, and make the rematch button start the next match in the same series [prd] [M] — Apple's rematch mints a new match id, so whether the scoreboard survives is persistence semantics, and a wrong guess silently resets a series players have been running for days.
- The network scan the tech design claims, with StoreKit and GameKit as the two sanctioned paths, and the doc's "not built" prose revised [look] [S] — the scan does not exist in the suite at all, so the rule the docs call checked is currently only asserted in prose.
- Play a full online game between two real devices on a child account [look] [S] — sign-in, find, take turns, the your-turn notification and a rematch; nothing above produces that evidence and the sandbox does not reproduce a restricted child account.
- Entitlements and store gateway: the app reads what the Apple ID owns at launch and on demand, caches it, and drives the open-games limit from it — plugin, entitlement state, store gateway with a test fake, launch wiring; no buy button and no purchase UI [prd] [M]
