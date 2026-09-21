# PRD: The finishing move is handed off, and the loser closes the match

> **Status:** Draft · Source docs read: Tech Design.md (Online Play; The channel contract;
> Persistence and Serialization), Menus and UI.md (Game Over → Rematch; Persistence),
> Game Overview.md (Session Structure), Rules.md, Game Board Design.md, Animations.md,
> Theming.md. Parking lot (never sourced): Alternative Game Styles.md.

## Problem

Today the move that finishes an online game ends the match with Apple outright
(`GameController.sendTurn` calls `endMatch` whenever the board it is sending is no longer in
progress). Apple pushes a notification for "it's your turn" and for nothing else, so the
other player's phone stays silent: they find out they lost the next time they happen to open
the app. The winner's rematch has the mirror problem — Apple will not mint a rematch while
the finished match is still open, and the result card's rematch button has no state for
that, so the tap either fails outright or reads as a plain error.

## Goal

A finishing move is handed off as an ordinary turn carrying a message, so Apple's own "your
turn" banner tells the other player the result even with their app closed. Their phone is what
ends the match, as soon as that finished board is on their screen, and until it does the other
player's rematch button says it is waiting on them and comes back to life by itself.

## Requirements

### The finishing send

1. **A finished board is handed off with `endTurn`, not `endMatch`.** When a confirmed move
   leaves the board finished on an online game, the send hands the board off as an ordinary
   turn. Tech Design → Online Play: *"The move that finishes a game is handed off as an
   ordinary turn, carrying a message that tells the other player they lost it."*

2. **Everything else about that send is unchanged** — the same awaiting-handoff mark while it
   is in flight, the same refusal of a second move while one is unsent, the same retry on a
   failure, the same write only on Apple's ok, under the match id chosen before the send, and
   the same answered outcomes a caller branches on. Tech Design → Online Play (*"Everything
   else about the send is unchanged"*; *"A local move is written to this device's store only
   after Game Center accepts the turn"*); Menus and UI → Persistence → When a game is written
   to storage.

3. **The hand-off carries a non-empty message naming the sender by Game Center account
   name**, read from this device's own signed-in session. Game Overview → Session Structure:
   *"That holds for every in-game message that names a player"*, using *"that player's Game
   Center account name"*. The four strings are settled:

   | Case | Message |
   |---|---|
   | The sender won | `<name> won your game.` |
   | The game was tied | `Your game with <name> ended in a tie.` |
   | Won, nickname unavailable | `Your game ended.` |
   | Tied, nickname unavailable | `Your game ended in a tie.` |

   A nickname is unavailable only when the session is not authenticated — the sending device
   always knows its own name otherwise — so the two fallbacks are an edge case rather than the
   ordinary path. The strings were settled for this feature; no design doc carries them yet
   (see Open Questions).

4. **An ordinary move carries no message.** A move that leaves the board in progress sends an
   empty or absent message, including the anonymous starter's zero-move hand-off and the
   searching screen's repeated re-sends of it. Tech Design → The channel contract: *"empty on
   an ordinary move, and carrying the result on the move that finishes a game."*

### The channel

5. **`endTurn` takes the message alongside the match id and the payload, and the native side
   makes it the match's own message before ending the turn.** Tech Design → The channel
   contract: `endTurn` *"takes those two plus the message GameKit shows in its 'your turn'
   notification"*, and *"The message it was handed becomes the match's own message, which is
   what Apple's 'your turn' banner reads on the other phone."*

6. **`endTurn`'s idempotence is unchanged and does not consider the message.** It still
   answers ok with no second platform call when this device is no longer the one to move and
   the match already holds exactly the payload being sent, so a retried finishing send never
   double-plays. Tech Design → Online Play (*"A retried send never double-plays, whichever kind
   it is"*) and → The channel contract.

7. **`endMatch` is unchanged** — same arguments, same outcome-setting, same idempotence
   against a lost reply. It keeps two callers: the opponent-left path, and R13 below. Tech
   Design → The channel contract (`endMatch` paragraph).

### Which device is Apple's to end the match — derived, never read

8. **On a finished online board, the device whose own side is the board's current player is
   the one that made the finishing move; the other device is Apple's current participant and
   therefore the one that ends the match.** The engine leaves the winner — or, on a draw,
   whoever made the final move — as the current player of a finished board, and the finishing
   hand-off passes the turn to the other phone, so the board alone answers this. Tech Design →
   The Rules Engine (*"The move that ends the game does not alternate… On a straight draw
   there is no winner to stop on, so the value stays with whoever made the final move"*), →
   Online Play (*"Apple lets only the player whose turn it is end a match, and the finishing
   hand-off is exactly what makes that the loser"*), and → Persistence and Serialization
   (*"Whose turn it is is not a stored field. It is the board's current player compared
   against the side this device plays"*). The comparison is between engine players — the
   board's current player and the side stored on the record — so the per-device icon pick
   never enters it; which mark this device draws changes nothing about which side it plays
   (Tech Design → Marks — supplied by the theme).

9. **Nothing asks Game Center which participant is current, and nothing reads a match's status
   to decide what to draw.** No Game Center read is added to opening a game, and no in-memory
   cache of match status is kept — Tech Design → Online Play: *"Opening an online game is
   playing, not entering… it makes no Game Center call."* R8 and the stored flag below are the
   whole answer; the match-ending call of R13 is the one call an open ever makes, and it draws
   nothing.

### One stored value says the match has ended

10. **An online record gains a seventh stored value, `matchEnded`** — this device's own
    knowledge that Apple has closed **the match the record currently points at**. It lives
    inside the record's `online` map beside `opponentLeft`, with exactly that shape: a yes/no
    that is **absent until it is yes**, so every record written before it existed decodes as
    no, and a value that is not a yes/no makes the record unreadable the same way
    `opponentLeft`'s does. Tech Design → Persistence and Serialization → *What an online game
    adds to the record*, whose shape this follows exactly.

11. **Two writes set it true, two clear it, and every other write preserves it.**

    - **True:** the turn-event receiver, whenever an arriving event's match status is `ended`
      and the event resolves to a record this device holds — by match id, or failing that by
      the payload's series id; and the ending device itself, when its own `endMatch` (R13)
      answers ok.
    - **Cleared:** the two writes that move a record onto a new match — the initiator's own
      next-game write, and an accepted rematch payload — which write it absent alongside the
      new match id. It is knowledge about one match, and those are exactly the two paths on
      which the match id changes (Tech Design → Persistence and Serialization: *"The match id
      changes on exactly two paths and no others"*). Without this, every series from its
      second game would hold a true flag against a freshly opened match: the device that owes
      the end would never make it, and the other would draw an ordinary rematch button whose
      tap Apple refuses.
    - **Preserved:** every other write path — a save, a rename, an applied turn, marking the
      opponent as having left, the icon pick.

    A write announces a change the same way every other record write does, so a result card
    already on screen sees it without a reload. Tech Design → The channel contract (a turn
    event's `match` map carries the match's `status`); → Persistence and Serialization
    (*"emits on the change stream"*).

12. **The receiver writes it on every outcome for a record it could identify**, not only on an
    applied turn — including a re-delivery, a rename-only event and an otherwise-ignored one.
    The ended status is the whole point of the event Apple sends when a match closes, and that
    event usually carries a board this device has already applied, so keying the write on
    "something was applied" would drop exactly the case this exists for.

### The other device ends the match

13. **A device showing a finished online board whose `matchEnded` is false, and which is not
    the device that made the finishing move (R8), ends the match.** It calls `endMatch` with
    its own outcome read off the board — `lost` when the board names the other side the
    winner, `tied` on a draw — handing Apple the board already stored, under that record's
    series id. Tech Design → Online Play: *"The losing device is what ends the match… Ending it
    sets this device's outcome to lost and the other's to won, the same call the opponent-left
    path already makes"*, and → The channel contract for the three outcome values.

14. **It fires as soon as the finished board is on this device's screen** — the screen's own
    load of the record landing, a re-read landing the finishing turn on the game already on
    screen, or the arriving-turn path putting that game on screen. The condition is the loser
    having seen the result, which is what the other player's rematch waits on — Menus and UI →
    Game Over → Rematch: *"The winner's rematch waits until the loser has seen the result."* An
    event a catch-up replays while the player is looking at something else ends no match; that
    match closes the next time the game is opened. Tech Design → Online Play (*"The losing
    device is what ends the match, the next time it opens that game"*).

15. **The device that made the finishing move never calls `endMatch` for that game**, on a won
    game and on a tie alike — Apple would refuse it, and R8 is what keeps it from trying. Tech
    Design → Online Play.

16. **The call is best-effort, silent, and one at a time per record.** It is fired without
    waiting, never shown to the player as an error or anything else, and never made twice
    concurrently for the same record. On ok, `matchEnded` is written true; on a failure nothing
    is written and the next time that board reaches the screen tries again. A stale false flag
    therefore costs one harmless extra call rather than a stuck match, because ending a match
    is idempotent — it answers ok for a match already ended with this device's outcome on it
    (R7). Tech Design → Online Play (*"It is best-effort and fired without waiting — a failure
    changes nothing"*).

### The other player's rematch waits

17. **On the device that made the finishing move, the result card shows the waiting state
    while that record's `matchEnded` is false, from the moment the card draws** — no tap
    needed to discover it, and it survives a relaunch because the value is on the record.
    Tech Design → Online Play (*"Apple refuses a rematch while the finished match is still
    open, so the winner's rematch is held rather than failed"*); Menus and UI → Game Over →
    Rematch (*"a button saying it is waiting on the other player"* which *"comes back to life
    by itself"*). A rematch Apple refuses anyway — the flag turned true a moment before the
    match actually closed — changes nothing and is reported the way any other refusal is; no
    branch anywhere reads a failure's message text (Tech Design → The channel contract).

18. **Only once the finishing hand-off has actually gone out.** While that send is in flight,
    and after one that failed, the screen shows what it shows today for those two states — the
    sending notice, and the failed send with its retry and its way out — and not "Waiting for
    `<name>`", which would otherwise tell the player they are waiting on the opponent for a
    move that never left this phone. Tech Design → Online Play: *"A send in flight and a failed
    send outrank a finished board, because the move that ends the game still has to be handed
    off and a failed send of it has to stay retryable."*

19. **The device that owes the `endMatch` never shows the waiting state** — it is not waiting
    on anybody. It draws the ordinary rematch button throughout, and a rematch Apple refuses
    there keeps today's behaviour: the card stays up and says so. Tech Design → Online Play:
    *"The loser's phone is what ends that match."*

20. **The waiting button reads "Waiting for `<name>` to see the result" and takes no tap.**
    The name is the opponent's Game Center account name, with the same fallback every other
    in-game line naming the opponent already uses. Menus and UI → Game Over → Rematch (*"a
    button saying it is waiting on the other player, 'Waiting for Sam to see the result'"*);
    Game Overview → Session Structure for the names rule.

21. **It comes back to life by itself when `matchEnded` turns true, and nothing is queued.**
    Three things flip it: GameKit's own match-ended delivery to the other participant, the
    catch-up that already runs at launch and on every resume, and a `syncMatches` re-check
    **every fifteen seconds while the waiting card is showing** — the same interval the
    searching screen already polls on, started when that card appears and stopped when it goes
    away. No rematch is sent by the transition; the player taps again. Menus and UI → Game Over
    → Rematch (*"comes back to life by itself once their phone has closed the match… The
    rematch is never queued to start on its own; the player taps it again when it does"*); Tech
    Design → Online Play (*"the rematch is asked of Apple on the tap that follows the unlock,
    never on the unlock itself"*), and → Catching up with Game Center.

### What keeps today's behaviour

22. **Both players tapping rematch at once.** The held match id is still dropped whenever a
    re-read shows the record's match id has already moved on, a second tap while a call is in
    flight still does nothing, and the first hand-off to land is still the one the series
    continues in. Tech Design → Online Play (*"Both players tapping rematch at once is
    safe"*); Menus and UI → Game Over → Rematch.

23. **The opponent having left.** The mark, the banner, the refusal of every tap, no result
    card and no rematch, and that path's own best-effort `endMatch` with a local `won` when
    this device is still current on an open match — all unchanged, and R13 never fires for a
    record whose opponent has left. Tech Design → Online Play (*"When the other player
    leaves…"*, *"If the match is still open and it is this device's turn, the app ends it"*).

24. **A match Apple has already ended** — which is what a finishing move from an opponent on a
    build that still calls `endMatch` produces. The finished board arriving as a turn is
    applied by the ordinary receive rules and the result card shows with no celebration; the
    event's `ended` status writes `matchEnded` (R11), so no `endMatch` of this device's own is
    made and the rematch button never waits. Menus and UI → Game Over → Rematch (*"A game the
    opponent ended shows the card with no celebration"*); Tech Design → Online Play → the
    receive rules.

25. **A turn event that brought the app to the foreground opens that game's board**, including
    the event carrying a finishing move — whether the record it resolved to was just created,
    just applied, or already held. Tech Design → Online Play: *"A turn event that brought the
    app to the foreground opens that game's board."*

26. **Untouched:** the payload's three keys (version, series id, board) and its encoding — the
    `matchEnded` flag is this device's own and never crosses the wire; every receive rule the
    arriving board is judged by (re-delivery, out of turn, reachability, the healing case, the
    stale match id); the per-device icon pick, asked once and kept through rematches; and how
    players are named everywhere else. Tech Design → Online Play; → Marks — supplied by the
    theme; Menus and UI → the icon pick.

## Out of Scope

- The wording of any other online message — the four on the open-games list, the two that
  arrive unasked, the failed-send message. Menus and UI → Open Questions.
- Anything the player is shown for a refused or re-delivered payload; nothing renders those
  today and this changes none of it. Tech Design → Open Questions → *Online play — what the
  player is told*.
- Local games, which have no match, no message and no rematch call.
- Notification permission, sound, or anything about how iOS presents Apple's banner beyond the
  text the match carries.

## Known limitation — a phone still on the old build

A finishing move handed to a phone running the current build leaves that match open until that
phone updates: the old build ends a match on the *sending* side and never on receipt, so it
has nothing that closes one for it. The sender's rematch button waits indefinitely, and
deleting the game is the way out (deleting resigns the match, Tech Design → Online Play).
Nothing here works around it: the app is distributed through TestFlight, so both phones update
together, and turns never time out, so nothing expires while it waits.

## Test plan

Dart-side, against the fake bridge and the in-memory store. The Swift half has no test target
and is checked by running the app on two devices signed into Game Center (Tech Design → The
channel contract).

- A confirmed move that finishes the board calls `endTurn` with a message and never
  `endMatch`; an ordinary move calls `endTurn` with no message.
- Each of the four messages in R3 — won, tied, and each with no nickname available.
- The finishing send keeps the ordinary semantics: a failure writes nothing, keeps the move on
  the board and marks the send failed; a retry re-sends the same board; ok writes the board
  under the match id captured before the send.
- The R8 derivation, from the board alone: on a finished board, the side that made the
  finishing move against each of the two `localPlayer` values, on a win each way and on a tie.
- `matchEnded` round-trips through the store; absent decodes as false; a record written before
  it existed still loads; a save, a rename, an applied turn and marking the opponent as having
  left all preserve it — the same cases `marksSwapped`'s own tests cover.
- A rematch clears it: the initiator's next-game write and an accepted rematch payload each
  leave it false alongside the new match id, including when it was true beforehand. After a
  rematch from either side, neither device holds it true.
- The receiver writes it on an arriving event whose match status is `ended`, for a record found
  by match id and for one found only by series id, and on an already-applied, rename-only or
  ignored outcome as well as an applied one; a record change is announced.
- A record whose board is finished reaching the screen — by a load, by a re-read landing the
  finishing turn on the game already on screen, and by the arriving-turn path — calls
  `endMatch` once with `lost`, and with `tied` on a drawn board, and writes `matchEnded` on ok.
- No `endMatch` call when `matchEnded` is already true, when this device made the finishing
  move (R8), when the record is marked opponent-left, when the board is still in progress, or
  on a local game. Never two calls in flight for one record.
- A failed `endMatch` writes nothing and surfaces nothing, and the board reaching the screen
  again tries once more.
- The result card on the device that made the finishing move draws the waiting button from its
  first frame while `matchEnded` is false, takes no tap, and sends no rematch; it draws the
  ordinary button once the flag is true, including after a relaunch.
- While the finishing send is in flight, and after one that failed, the screen shows today's
  sending / failed-send states rather than the waiting button.
- The device that owes the `endMatch` draws the ordinary rematch button, never the waiting one,
  and a refused rematch there shows today's failure message.
- The flag turning true while the card is up swaps the waiting button for the ordinary one and
  sends no rematch of its own.
- The fifteen-second re-check starts when the waiting card appears and is cancelled when it
  goes away, leaving no timer behind.
- The receiver's existing outcomes are unchanged for a finished board arriving as a turn, and
  the opponent-left branch still fires its own `endMatch` with `won`.
- On device: the banner text landing on a locked phone, the match closing when the loser opens
  that game, and the winner's button unlocking without a relaunch.

## Open Questions

None outstanding for this feature.

What it turns on was settled for it and is not yet written down in any design doc — this is
the close-out debt, for Tech Design → Online Play, Tech Design → Persistence and
Serialization, and Menus and UI → Game Over → Rematch:

- The four message strings (R3). Menus and UI → Open Questions → *What do the online messages
  say?* still stands for the other online messages and does not cover this banner.
- That which device ends the match is derived from the finished board rather than read from
  Apple (R8, R9).
- The record's `online` map gains a seventh value, `matchEnded`, with the same "absent until
  yes" shape as `opponentLeft`, cleared by the two writes that move the record onto a new
  match (R10–R12). Tech Design → Persistence and Serialization → *What an online game adds to
  the record* names six today, in a passage that says those key names are schema, and its
  *"A save never touches those five"* / *"The match id changes on exactly two paths"* rules
  both gain this value.
- That the match is ended as soon as the finished board reaches the screen, not only on a
  fresh open (R14). This is also the one exception to Tech Design → Online Play's *"Opening an
  online game is playing, not entering… makes no Game Center call"*, which has to be narrowed
  to say so.
- That the waiting button is driven by the stored flag from first draw rather than by a
  refused tap, and never outranks a send in flight or a failed send (R17–R19), plus the
  fifteen-second re-check (R21).
- The mixed-version limitation above, for as long as it is true.
