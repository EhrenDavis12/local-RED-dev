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
  - **Assumption I'm building on (2026-09-15; reverse before merge if you disagree):**
    deleting resigns. It is also what makes a delete stick — a resigned match sends this
    phone no more turns, so the game can't quietly reappear when the opponent's next move
    arrives. The alternative would mean remembering deleted games on the phone.
    A:
  - Q: If your move can't be handed to Game Center (no signal, Apple refuses it), the app
    keeps the move on screen so you can try again. Until it goes through, the app stops
    you making another move in that game — otherwise the two phones can end up on boards
    neither can continue. Assumption I'm building on; OK?
    A:
- decide: a random-opponent online game is renamed once when the opponent joins [prd] · branch queue/game-center-bridge-1
  - Found while specifying the Game Center bridge: when a player taps Play Now, Apple hands
    back the match before anyone has joined — the opponent's name doesn't exist yet, but
    the starter has to take the first turn from the board screen, so the game must be
    saved right away. Your docs say an online game is titled with the opponent's nickname
    when the match is created and nothing ever renames it. Those two can't both hold for
    Play Now.
  - **Assumption I'm building on (reverse before merge if you disagree):** the game is
    saved with the usual placeholder name ("ItSaMeMaRiO") and renamed exactly once, to
    the opponent's Game Center nickname, when Apple reports who joined. Nothing else can
    rename an online game. Invited-friend games are never affected — the friend's name is
    known at creation. The alternative is leaving the placeholder for the life of that
    game. Cheap now; after merge it's a storage-contract change to undo.
  - Q: OK with the one rename for random-opponent games?
    A:
