# Blocked

> **What this is:** Work waiting on you. Each item lists the questions the queue could not
> answer by reading, and where its partial work lives.
> **Shared.** The queue writes the item and its `Q:` lines; you write the `A:` lines.
> **Hints:** Answer under the question, in plain words. If an answer is a design decision, it
> lands in the design docs before the work resumes. An item with every `A:` filled in returns
> to the top of Ready on the next tick.

---
- decide: what deleting an online game does for the other player [prd] · branch none
  - Turns never time out (your answer), and a player who wants out deletes the game like any
    other open game. That leaves one thing unsaid, and the bridge's quit/resign work needs
    it. Cheap to change later.
  - Q: When a player deletes an online game, should the other player's copy end too (the
    delete resigns the match, so they see "game over" instead of waiting forever), or
    should it only leave this phone (their copy keeps waiting for a turn that never comes,
    until they delete it as well)? Resigning is the kinder default.
    A:
