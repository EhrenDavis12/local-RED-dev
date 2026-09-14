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
    set time (Apple's usual default is two weeks) and hand the win to whoever is still
    playing? Cheap to change — one setting sent with each turn.
    A:
  - Q: What name is an online game listed under — the other player's Game Center
    nickname (which they chose, could be anything), or a label this player types?
    Moderate to change; the name is fixed when the game is created.
    A:
