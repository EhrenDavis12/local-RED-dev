# Proposed

> **What this is:** What the AI thinks is missing between the current state and the Goal.
> Written by the queue from `forge-queue-planner`'s report. Nothing is ever built from here.
> **The queue's.** Promote a row by moving it to Inbox or Ready. Reject it by deleting the
> line — and add a word to Goal's "Not included" if it should stay gone.
> **Hints:** Rows are ordered by what unblocks the most. `[prd]` means a wrong guess is
> expensive and it gets specified first; `[look]` means it gets built and looked at.

---
- App Store Connect account, agreement and product records — Paid Applications Agreement, banking and tax, the two product identifiers, age rating questionnaire, privacy label, content rights, price and territory, App Review contact, support URL [prd] [M] — longest human lead time in the whole goal and it gates every other purchase row, and a product identifier is permanent: a wrong one has to be abandoned rather than corrected.
- Entitlements layer — last-known-plus-refresh provider, local cache store, one commit path for memory and disk [prd] [L] — every purchase row and the open-game cap read it, and a wrong guess drops what a player bought with no error in any log.
- Parental gate [prd] [M] — the Kids Category requires it before any purchase and it must be enforced at the purchase itself, so a gate that can be reached around is an App Review rejection rather than a bug.
- Purchase flow — Settings purchases section, Restore purchases, Sewing locked behind its product, the open-game slot unlock [prd] [L] — the goal's purchase bullet, and a purchase left pending on a parent's approval that never reaches the child is money taken for nothing.
- Crash reporting — catch, build the report object, centralized console log, bounded in-memory retention [prd] [M] — the goal's no-crash bullet, and a report that renders a board position or a typed opponent name is a 4+ privacy problem rather than a debugging inconvenience.
- Neon's sound set [look] [M] — Neon's sound slots are literal `TODO` strings and only Sewing ships audio, so the default theme and Classic are silent and the Music and Sound effects toggles do nothing.
- iPad and small-phone layout pass [look] [M] — the submitted build is universal and the goal requires it to hold together on both, and nothing has been checked past the handoff's 402pt phone frame.
- decide: what the main-menu logo actually is [look] [S] — the menu ships an 81-dot dashed-border placeholder and the goal's bar is nothing placeholder; no doc states the logo's subject.
- decide: what the About Us screen says [look] [S] — the screen ships with an empty content region, the one place the flow still dangles; the handoff draws team photos and where those come from is not decided.
- App Store screenshots at Apple's iPhone and iPad sizes [look] [S] — a required listing field, the screenshots folder is empty, and the release lane already uploads whatever is there.
- Release lane runs flutter analyze and flutter test before it builds [look] [S] — the tech design makes the release run the only automated gate, and the `release` lane today runs neither check before it uploads.
- Full-session playtest on a phone and an iPad [look] [S] — the goal states its no-crash, no-lost-game bar as a playtest outcome and no other row produces that evidence.
- The online-game record: match id, which participant is Player One, whose turn it is, online-vs-local, alongside GameRecord [prd] [M] — on-disk schema plus the board payload both devices exchange, so a wrong guess is a migration on records players already hold and a series that desynchronises between two phones with no error anywhere.
- "Play online" on the main menu, behind the parental gate [look] [S] — the button the user asked for; depends on the "Parental gate" row already in Proposed, which is not built, and makes the menu five buttons where the docs settle four.
- Game Center bridge, part two: end a turn with the board, receive the opponent's turn, quit and resign [prd] [M] — this is the move itself crossing the wire, and a turn sent twice or applied twice leaves two phones holding different boards, which no test catches after the fact.
- The board screen drives a remote turn: input locked when it is not your turn, confirm sends, an arriving turn replaces the board [prd] [M] — decides which board wins when a remote turn lands on a local pending selection, and getting it wrong overwrites a player's move or corrupts the saved series.
- Online games in the Open Games list: your turn, waiting on them, and which games are online [look] [M] — a player cannot open a game they cannot play without knowing why, and the list is the only place an invited match first appears.
- Game over online: report the outcome, end the match, and make the rematch button start the next match in the same series [prd] [M] — Apple's rematch mints a new match id, so whether the scoreboard survives is persistence semantics, and a wrong guess silently resets a series players have been running for days.
- The network scan the tech design claims, with StoreKit and GameKit as the two sanctioned paths, and the doc's "not built" prose revised [look] [S] — the scan does not exist in the suite at all, so the rule the docs call checked is currently only asserted in prose.
- Play a full online game between two real devices on a child account [look] [S] — sign-in, find, take turns, the your-turn notification and a rematch; nothing above produces that evidence and the sandbox does not reproduce a restricted child account.
