# PRD: The Board Screen Drives a Remote Turn

> **Status:** Draft · Source docs read: Tech Design (Online Play, Persistence and
> Serialization, Navigation, Rendering the Board, Kids Category, Open Questions), Menus and UI
> (Play Game, Play online, Game Over → Rematch, Persistence, Navigation and the Back Stack),
> Game Board Design (Move Input, Changing your mind, Taps outside the legal quadrant, Player
> Feedback, Haptic Rule), Game Overview, Rules, Animations, Theming. Code seams read on branch
> `queue/game-center-bridge-2`: `lib/state/game_controller.dart`, `lib/state/game_session.dart`,
> `lib/gamecenter/turn_event_receiver.dart`, `turn_event_outcome.dart`,
> `game_center_providers.dart`, `fake_game_center_bridge.dart`, `lib/ui/board/`,
> `lib/ui/menus/theme_snackbar.dart`.

## Problem

Everything an online turn needs exists below the board and nothing on the board uses it. A
player can open an online game and tap a cell on the opponent's turn: the engine places the
mark of whoever the current player is, so the tap places the *opponent's* mark, and the send
that follows is a board the opponent's device refuses as out of turn. Nothing says whose turn
it is, nothing says a move is being handed to Apple, a send that fails looks identical to one
that worked, and an opponent's move that has already been written to this phone's store does
not appear until the screen is left and reopened.

## Goal

An online game plays on the same board screen as a game on this phone. When it is not the
local side's turn the board takes no move and says calmly that it is waiting on the opponent;
confirming a move hands it to Game Center and says so while that is in flight; a send Apple
refused keeps the move on the board with a way to send it again and a way out; and a turn that
arrives while the screen is up replaces the board and unlocks input where it stands.

## Requirements

### The state the screen derives

1. **A session holding no match id is a local game and nothing here applies** — the screen
   behaves exactly as it does today. Presence of the online values is the only thing that tells
   an online game from a local one (Tech Design → Persistence and Serialization → *What an
   online game adds to the record*), and `GameSession.onlineMatchId` is that test on the
   session (`lib/state/game_session.dart`).

2. **The screen derives exactly one `OnlineTurnState`**, and the set is closed:
   `yourTurn`, `waitingForOpponent`, `sending`, `sendFailed`, `gameOver`. It is absent (null) on
   a local game. It is derived from the session alone, by the first branch that matches:

   | Order | Condition on the session | State |
   |---|---|---|
   | 1 | `lastSendFailed` | `sendFailed` |
   | 2 | `pendingHandoff` | `sending` |
   | 3 | `board.result` is not in progress | `gameOver` |
   | 4 | `board.currentPlayer == onlineLocalPlayer` | `yourTurn` |
   | 5 | otherwise | `waitingForOpponent` |

   Rows 4 and 5 are the doc's own definition of whose turn it is — the board's current player
   compared against the side this device plays, never a stored field and never re-derived
   (Tech Design → Persistence and Serialization → *What an online game adds to the record*).
   Row 3 sits above them because a finished board's current player is the winner rather than
   someone to move, and anything that presents a turn gates on the game-over state first (Tech
   Design → The Rules Engine → *The move that ends the game does not alternate*).

3. **`sending` and `sendFailed` outrank `gameOver`.** The move that ends the game still has to
   be handed off, and a failed send of it has to stay retryable — a failed send keeps the
   confirmed move and sending again re-sends that same board (Tech Design → Online Play; Menus
   and UI → Persistence → *When a game is written to storage*). A winning move whose send fails
   shows the retry, not only the result card.

### Input is locked when it is not your turn

4. **Only `yourTurn` accepts a move.** A tap on a cell while the state is `waitingForOpponent`
   is refused by `GameController.tapCell`, which answers a new distinct
   `TapResult.refusedNotYourTurn`. The gate lives in the state layer, not in the board: the
   board draws state and gates nothing, and what a tap means is decided in the state layer
   (Tech Design → Rendering the Board). The refusal is checked after the existing
   pending-handoff refusal and before legality, so a tap on the opponent's turn reports it
   whatever cell it lands on.

5. **The refusal applies only while the board is in progress.** On a finished board the current
   player is the winner rather than someone to move, and the legal-move set is empty exactly
   when the game is over, so every tap is already a complete no-op (Tech Design → The Rules
   Engine → *The move that ends the game does not alternate*, *The legal-move set is empty
   exactly when the game is over*).

6. **A refused tap does nothing at all** — no mark, no pending selection, no shake, no message,
   and no buzz (Game Board Design → Taps outside the legal quadrant; Haptic Rule: a buzz means
   "that registered", no buzz means "that did nothing").

7. **The lock is taps and nothing else.** While `waitingForOpponent` the board renders exactly
   as it does on the local side's turn — the forced-quadrant highlight stays drawn, the last-move
   highlight stays drawn, nothing dims and nothing is added. Drawing the quadrant the opponent
   must play in is information the player wants, and the two highlights are the board's core
   readability (Game Board Design → The Two Highlights Together). And **nothing removes or
   blocks the cells' own tap handlers to implement the lock** — no `IgnorePointer`,
   `AbsorbPointer` or omitted handler over the board. A cell with no handler of its own loses the
   tap to the tap-away surface underneath, which is the documented bug this codebase has already
   been warned about (Tech Design → Rendering the Board).

### Waiting on the opponent

8. **While `waitingForOpponent` the screen shows a waiting indicator**, keyed
   `onlineWaitingKey`, naming the **side** whose turn it is — Player One or Player Two, read
   from the board's current player — and never the opponent's Game Center nickname. In game the
   players are still Player One and Player Two; the nickname titles the game in the open-games
   list and nothing else (Menus and UI → Play Game → Where It Takes You). Tests pin the key and
   which side is named; the sentence around it is copy and is not pinned.

9. **The screen needs nothing from the stored record's title**, so no session field carries it
   and no path is added to put one there. This follows from R8: the only thing that wanted the
   nickname on the board was the waiting line, and it names the side instead. The nickname
   reaches the player on the list row, which is where the docs put it (Menus and UI → Play Game →
   Where It Takes You).

10. **Nothing renames the players in game.** On `yourTurn` the turn banner and the scoreboard
    read Player One and Player Two exactly as they do on this phone — the opponent name titles
    the game in the open-games list and nothing else (Menus and UI → Play Game → Where It Takes
    You).

### Confirming sends

11. **The confirming tap makes exactly one controller call, `tapCell`.** The screen never calls
    `sendTurn` for the first send of a move: the state layer applies the move to the session,
    marks the game awaiting handoff, saves nothing and hands the encoded board to Game Center
    (Tech Design → Online Play → *A local move is written to this device's store only after
    Game Center accepts the turn*; `GameController.tapCell`).

12. **While `sending` the screen shows a sending indicator**, keyed `onlineSendingKey`, derived
    from the session rather than from a screen-local flag — so a send begun by the confirming
    tap and a send begun by a retry read identically.

13. **`GameController.sendTurn` clears `lastSendFailed` the moment it actually attempts a
    send** — past its `TurnNotOnline`, `TurnSendInFlight` and `NoPendingMove` refusals, before
    `endTurn` is called. Without it a retry sits in `sendFailed` while its own send is in
    flight, and R12 cannot hold for the retry.

14. **On `TurnSendFailed` the screen shows the failed-send state**: a message keyed
    `onlineSendFailedKey`, a retry control keyed `onlineRetrySendKey`, and a way out keyed
    `onlineSendFailedExitKey`. The confirmed move stays on the board — a send that fails keeps
    the move on screen to be sent again (Menus and UI → Persistence → *When a game is written to
    storage*; Tech Design → Online Play).

15. **The retry calls `sendTurn` with the session's record id and does nothing else.** No second
    move is applied and no new board is built: the same board goes out under the same match id —
    a retry, not a second move (Tech Design → Online Play → *While a move is awaiting handoff,
    that game refuses another one*). Assertable directly: two entries in the fake bridge's
    `endTurnCalls` carrying an identical match id and identical payload bytes.

16. **The way out of a failed send is `AppNavigator.exitGameToMainMenu()`.** Leaving a game
    takes the player to the main menu, and no navigation operation returns to the open-games
    list (Menus and UI → Navigation and the Back Stack; `lib/navigation/app_navigator.dart`).

17. **Walking away from an unsent move stores nothing.** Reopening that game from the list shows
    the board as stored, without the unsent move — which is what the opponent sees too (Tech
    Design → Online Play: *a relaunch loses an unsent move and shows the board as it stood before
    it*).

18. **`TurnSent` returns the screen to `waitingForOpponent` with no confirmation of its own**,
    and so does `TurnSentNotStored` — which offers no retry, because the opponent already holds
    the turn and it is never re-sent (Tech Design → Online Play). `TurnSendInFlight`,
    `NoPendingMove` and `TurnNotOnline` change nothing on screen; the retry control is only
    reachable in `sendFailed`, so they are unreachable from it.

### An arriving turn replaces the board

19. **The screen subscribes to the receiver's outcome stream for as long as it is mounted**,
    through a provider that reads `turnEventReceiverProvider` — call it
    `turnEventOutcomesProvider`. It never constructs a receiver of its own: one receiver
    subscribes for the app's lifetime, and a second live one would double-apply every arriving
    turn (Tech Design → Online Play → *The channel contract*). The stream is the seam the board
    screen reads (Tech Design → Online Play → *Every outcome of an arriving turn is published on
    a stream as well as answered*).

20. **It acts on exactly two outcomes: `TurnEventApplied` and `TurnEventCreated` whose
    `recordId` is the session's `gameId`.** Every other outcome changes nothing on screen — one
    for another record, a re-delivery, any refusal, and every drop. That is today's behaviour
    ("nothing renders any of them"), not an answer to what the player should be told, which
    stays open (Tech Design → Open Questions → *12. Online play — what the player is told*).

21. **On one of those two the screen calls `GameController.reloadFromStore(recordId)`**, which
    re-reads the record and replaces the session's board and its three online values — and does
    **not** raise `isLoading`. The load-before-draw gate exists because a board drawn
    before the read lands is the *previous* game's position (Tech Design → Rendering the Board →
    *The screen loads its game before it draws one*); that risk belongs to the first read of a
    screen, not to a refresh of the game already on it, and blanking the board to a spinner on
    every opponent move would be a new defect rather than that rule being honoured.

22. **The reload clears the pending, unconfirmed selection and its preview.** A selection is not
    a move (Game Board Design → Changing your mind), and one computed against the board that was
    just replaced breaks `GameSession`'s own invariant — a pending selection is always a legal
    move on the current board, with the preview being that move applied.

23. **The reload also clears `pendingHandoff` and `lastSendFailed`**, the stored board being
    authoritative once a turn has arrived for it. The combination is unreachable in practice —
    the opponent cannot move on a board this device never handed off — which is exactly why it
    is stated rather than left to whoever writes the method.

24. **Nothing else runs on an arriving turn.** After the reload the state falls out of R2 with no
    extra step: input unlocks because the board's current player is now the local side. A reload
    is a plain re-read and is safe to run repeatedly, including one landing while the screen's
    own first load is still in flight.

### Game over on an online game

25. **The result card appears on a finished online game exactly as on a local one** — the
    bottom-anchored panel, after the win celebration, naming what happened, the running score
    and who goes first next time (Menus and UI → Game Over → Rematch → The result card).

26. **On an online game the card's rematch control is not rendered**; the exit-to-main-menu
    control stays, so the card still carries its own way out and nobody is stranded on a
    finished board (Menus and UI → Game Over → Rematch → The result card: *the card is
    self-sufficient*). Hidden rather than disabled because no doc defines a disabled-control
    treatment and a hidden control needs no new theme value. It is hidden because the local
    rematch would advance the board and write it under the *finished* game's match id, which is
    the state the single write of *Advancing to the next game and pointing the record at the new
    match is one write* exists to make impossible (Tech Design → Persistence and Serialization).
    The online rematch belongs to the "Game over online" queue row; this PRD only keeps the
    wrong one from being reachable in between. The two controls take keys —
    `resultCardRematchKey` and `resultCardExitKey` — so absence is assertable.

### Opened from the list, or from a notification

27. **Opening an online game shows the current stored board and nothing more.** The screen makes
    no Game Center call, raises no sign-in and raises no parental gate: opening an online game
    that already exists — from the open-games list or from a "your turn" notification — is
    playing, not entering (Tech Design → Kids Category). Whatever the receiver wrote before the
    screen mounted is already in the record it loads; anything that lands afterwards arrives
    through R19–R21.

**Test seams.** Every requirement above is reachable with the fakes that already ship as app
code: `FakeGameCenterBridge` (`pushSession` to reach an authenticated session — `endTurn`
refuses otherwise; `scriptEndTurnResult` for a failure; `holdNextEndTurn`/`finishHeldEndTurn` to
hold a send in flight for R12; `pushTurnEvent` to originate an arriving turn; `endTurnCalls` for
R15) and `InMemoryGameRepository` for the store, with `turnEventReceiverProvider` reached
through its provider so one receiver routes the pushed event exactly as it does in the app. No
golden or pixel assertion: this project's testing preferences rule them out, and everything here
is pinned by key, by controller call, or by stored state.

## Out of Scope

- **The Open Games list** — which rows are online, whose turn each is, and how an invited match
  first appears there. That is the next queue row.
- **Game over online** — ending the match with Apple, the rematch that mints a new match id, and
  what the opponent's device is told. Its own queue row and its own PRD; R26 only hides the
  control that would otherwise do the wrong thing before it lands.
- **All message wording.** Tests pin structure by key, never copy — which is also what keeps the
  unsettled questions below cheap to answer later.
- **Any new treatment for the locked board.** R7 settles that it renders unchanged, so there is
  no dimming, no veil and no online-only highlight to design.
- **The how-to-play strip's content** in any online state.
- Notifications themselves, sign-in, the matchmaker, and the parental gate.

## Open Questions

- **Should a re-delivered identical board be visible to the player at all, or silently ignored?**
  (Tech Design → Open Questions → 12.) R20 builds today's silence and answers nothing.
- **What does the player see for a move Game Center would not take, and for a GameKit error the
  bridge reports?** (Tech Design → Open Questions → 12.) R14 gives the failure a keyed message,
  a retry and a way out; what that message says is unsettled.
- **What does the how-to-play strip say in the waiting, sending and failed states?** Already open
  as *"Which strip content belongs to which board state, and is the set of states exactly the
  three the handoff draws?"* (Menus and UI → Open Questions), with online adding three more.
- **Do things the player didn't tap buzz?** (Game Board Design → Open Questions.) An opponent's
  turn arriving on screen is exactly such an event; this PRD plays no sound and fires no haptic
  for one.
