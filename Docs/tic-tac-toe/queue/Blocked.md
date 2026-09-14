# Blocked

> **What this is:** Work waiting on you. Each item lists the questions the queue could not
> answer by reading, and where its partial work lives.
> **Shared.** The queue writes the item and its `Q:` lines; you write the `A:` lines.
> **Hints:** Answer under the question, in plain words. If an answer is a design decision, it
> lands in the design docs before the work resumes. An item with every `A:` filled in returns
> to the top of Ready on the next tick.

---
- decide: online play — six decisions the multiplayer build needs [prd] · branch none
  - The user asked on 2026-09-14 to build online play over Game Center: setup, a "Play
    online" button, and match creation (Apple's matchmaker provides find-a-player and
    friend invites). The eleven-row plan is in Proposed (three rows already in Ready).
    Rows that store data or fix the game's shape wait on these:
  - Q: The written goal says the App Store release does not include online play. Does
    the release now wait for online play, or does it go out first and online ships as
    an update? (Goal.md is yours to edit either way.)
    A:
  - Q: Do online games count toward the same three-open-games limit as games on this
    phone? If yes, a kid with three games going cannot accept a friend's invite until
    they delete one. Hard to change later — it's written into how games are stored.
    A:
  - Q: When should the game ask Apple who the player is? At launch shows every player a
    Game Center welcome banner the first time, even if they never play online; the first
    tap on "Play online" keeps it away from one-phone players. Cheap to change.
    A:
  - Q: How often is the grown-up maths question asked for online play — every new online
    game, only the first time ever, or once per app open? And is it asked when accepting
    a friend's invite, or only when starting one? Cheap to change.
    A:
  - Q: If the other player never takes their turn, wait forever or end the game after a
    set time? Apple's default is one week and a week is the shortest it honours in
    practice. And when it ends: the waiting player wins by forfeit, or the game ends
    with no winner? Cheap to change.
    A:
  - Q: What name is an online game listed under — the other player's Game Center
    nickname (which they chose, could be anything), or a label this player types?
    Moderate to change; the name is fixed when the game is created.
    A:
- Confirm Game Center turn-based play works on an under-13 Family Sharing account, and that a Kids Category app may ship it [research] [S] · branch none
  - **What was found (checked 2026-09-14):** yes on both counts. A child Apple Account
    can sign in to Game Center and play turn-based games; Apple lists multiplayer as a
    parent-*restrictable* feature (Allow / Friends only / Don't allow), not a disabled
    one, and Game Center enforces the friends-only choice itself — the app only has to
    notice "don't allow" and hide online play with a calm message. Nothing in the App
    Review guidelines or Apple's kids-apps page bars Game Center in a Kids Category app:
    Game Center is Apple, not a third party, so the "no data collected" privacy answer
    holds. No Kids Category game was found shipping Game Center turn-based play, so it
    is unproven rather than prohibited. Children get Apple's safety rails for free: no
    voice, no typed messages, preset invite text only, and the app never sends anything
    but the board.
  - **What Apple's system does for "find a player":** its own sheet lists the player's
    current matches, offers Play Now (random opponent) and Invite Friends (Game Center
    friends and contacts, including sending the invite through Messages). Apple sends
    the "your turn" notification itself. A turn that isn't taken passes after a
    timeout (default one week, and in practice a week is the shortest Apple honours —
    a shorter "abandon" rule would be the app's own logic).
  - **Plan corrections:** the "invite link" API the plan named doesn't exist — Messages
    invites already come free with Apple's sheet, so nothing is lost. The bridge must
    not force "random opponent only" mode (it throws for a friends-only child); it
    uses Apple's default mode and lets the sheet show what's allowed. No Flutter
    package wraps turn-based matches, so the Swift bridge stands.
  - Q: For children, should the app itself refuse random-opponent matching and only
    allow friends, or trust the parent's Game Center setting as Apple designed it
    (parents choose everyone / friends only / off)? Cheap to change later.
    A:
