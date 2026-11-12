# PRD: Save, Load, and Time Passing While Closed

> **Status:** Draft · Source docs read: `Core Concept.md`, `Guild Members.md`,
> `Equipment.md`, `Combat.md`, `The Dungeon.md`, `Specialists.md`, `Individual Types.md`
> (searched), and the change notes in `EhrensDocs/` (`Core Concept.md`, `Guild Members.md`,
> `Equipment.md`, `Combat.md`, `The Dungeon.md`, `Platform.md`); `queue/focus.md`; source
> under `src/guildmasters-descent/Assets/Scripts/Core/` and its EditMode tests.

## Problem

The guild exists only in memory. Close the app and the guild is gone, and nothing counts the
time the player was away — so an injured member never heals while the game is closed, though
`Core Concept.md` § Time says time keeps passing then.

## Goal

The player's guild survives closing the app, and the time they were away is counted on their
return: injuries heal by exactly the time that passed, once, however the time was split
between open and closed. A missing, unreadable, or newer save is reported plainly and never
destroyed. The title menu (a separate item) has a core API to call, and every rule here is
testable in EditMode with a fake clock and fake storage.

Timed missions are out of the MVP (`queue/focus.md` § Not included, user 2026-11-11), so
away-time covers injury healing and, once the board exists, the recruiting-board restock.

Requirements marked **[Provisional]** are cheap, reversible defaults chosen because no doc
settles them. Each is also listed under Open Questions for the user's word.

## Requirements

### What a save holds

1. A save holds the whole guild as the data model builds it — rank, gold, every member field,
   every stores piece field, both ID counters, and each member's weapon and armour slots — and
   loading it gives back a guild equal to the saved one, field for field.
   *Source: `queue/focus.md` § Goal ("In: … save and load"); the model in `Core/Guild/`.*
2. A save also holds a format version (this feature ships version 1) and the moment the
   guild's time was last settled (R14), as whole seconds of UTC wall-clock time. The saved
   shape still holds no floating point, as the data model's tests already require.
   *Source: build brief (versioned save); `Core Concept.md` § Time.*
3. Saves are on the device, one per slot. The number of slots is a placeholder,
   `Tuning.SaveSlotCount = 3`. *Source: build brief; `queue/focus.md` § Goal, "Missing
   details".*
4. A save never destroys the save before it. If the write fails or the app dies partway, the
   slot holds either the previous save whole or the new one whole, never a mix or a fragment.
   A failed save is reported to the caller. *Source: build brief (a wrong guess loses or
   corrupts saves).*
5. Every saved enum value — rank, tier rung, member type, gear kind — keeps its meaning in
   every later version, and a test pins today's stored values so that reordering an enum
   fails the build rather than silently changing old saves. Member types and gear kinds are
   expected to grow: the other six specialists are out of the MVP only for now, and the
   specialist list "isn't complete". *Source: `queue/focus.md` § Not included;
   `Guild Members.md` § Specialists.*

### Loading

6. Loading a slot has exactly four outcomes: **loaded**, **empty**, **corrupt**, and
   **newer version**. Only *loaded* hands back a guild. *Source: build brief.*
7. Loading never writes to, moves, or deletes the save file, whatever the outcome. A corrupt
   or newer-version save stays on the device untouched. *Source: build brief.*
8. A save whose version is above the game's own is *newer version*, not *corrupt*. A save
   that can't be parsed, has no readable version, or holds a value the model gives no meaning
   to (a member type that doesn't exist) is *corrupt*. Version 1 is the first, so there is
   nothing older to migrate and no migration is built now. *Source: build brief.*
9. A slot's status — which of the four outcomes a load would give — can be read without
   bringing the guild into play, and reading it changes nothing. The title menu uses this to
   decide which buttons to show. *Source: build brief (core API for the title menu).*

### Checking a loaded save

10. **ID counters.** If a counter is not above every ID of its kind in use, the guild could
    hand out an ID twice. **[Provisional]** The counter is raised to one above the highest ID
    in use, and the load still succeeds. *Source: build brief (guild data model follow-ups);
    `Guild.cs` ("an ID is never reused").*
11. **Equipped slots.** A slot is bad when it names no piece in the stores, names a piece of
    another combat type's kind or the wrong half (armour in the weapon slot), sits on a
    specialist (a specialist has no equipment), or names a piece another member also holds.
    **[Provisional]** A bad slot is emptied and the piece, if it exists, stays in the stores;
    a piece held twice stays with the member with the lower ID. The load still succeeds.
    *Source: build brief; `Equipment.md` § Assignment.*
12. **[Provisional]** Two members sharing an ID, two pieces sharing an ID, or any ID below 1
    (0 is the empty-slot marker) makes the save *corrupt* — no repair can tell which one a
    slot meant. *Source: build brief; `Member.cs` (`EmptySlot = 0`).*
13. A load that repaired anything under R10 or R11 says so in its result, so the repair can
    be logged. *Source: build brief.*

### Time while away

14. **Settling** advances the guild to *now*: elapsed time is *now* minus the saved
    last-settled moment, in whole seconds; every time-driven part of the guild advances by
    that much; then last-settled becomes *now*. A load settles after the checks above and
    before handing the guild back. *Source: `Core Concept.md` § Time; `queue/focus.md` §
    Goal.*
15. Every second counts exactly once. Settling in pieces gives the same guild as settling
    once over the same span, including across a save and a load; settling twice at the same
    *now* is the same as settling once. Nothing advances injury time (or, later, restock
    time) except through settling — anything that did would leave last-settled behind, and
    the next load would count that time again. *Source: `Core Concept.md` § Time.*
16. Settling advances each member's injury by the elapsed time, the free, slow recovery
    `Core Concept.md` § Missions describes. It touches nothing else on a member — in
    particular not health, whose behaviour back in the hall is unsettled (`EhrensDocs/Guild
    Members.md`, "Every member starts with 10 health"). *Source: `Core Concept.md` § Time,
    § Missions.*
17. **Recruiting board hook.** The board isn't in the code yet. Settling gives the board the
    same thing it gives injuries — the elapsed seconds — under the same once-only rule (R15),
    so a restock is neither lost nor doubled across a save and a load. The board's own state,
    including its progress toward the next restock, is saved with the guild when the board
    lands. This feature builds no board and no restock rule. *Source: `Core Concept.md` §
    The Recruiting Board ("restocks over time").*
18. Time is UTC wall-clock time, so a time-zone change or daylight-saving shift neither adds
    nor removes away-time. *Source: `Core Concept.md` § Time ("real time").*
19. **Clock going backwards. [Provisional]** If *now* is earlier than last-settled, elapsed
    is zero and last-settled stays where it was — it never moves backwards. The guild's
    clocks stand still until the device clock passes the saved moment again. This blocks
    "set the clock back, then forward" from granting time twice. *Source: build brief.*
20. **No cap on away-time. [Provisional]** All of the elapsed time counts, however long the
    player was away, and there is no defence against the device clock being set forward. No
    doc names a cap. *Source: `Core Concept.md` § Time.*
21. Returning to the app from the background settles exactly as a load does. On the iPhone a
    backgrounded app is often never closed, and the away-time must still count.
    *Source: `Core Concept.md` § Time; `EhrensDocs/Platform.md` § Orientation (iPhone).*

### New game, saving, and the seams

22. **New game** makes a guild exactly as the data model makes a new one — today, starting
    gold and nothing else — sets last-settled to *now*, and saves it to the chosen slot.
    **[Provisional]** New game into an occupied slot (including a corrupt or newer-version
    one) is refused unless the caller explicitly asks to overwrite; the core never replaces a
    save by default. *Source: `queue/focus.md` § Goal ("new game"); build brief.*
23. **[Provisional]** The game saves by itself: the loaded guild is saved to its slot when the
    app goes to the background or quits. There is no Save button. On the iPhone a
    backgrounded app can be killed with no warning, so a guild saved only on request would
    lose play. *Source: `EhrensDocs/Platform.md` § Orientation (iPhone); build brief.*
24. The clock and the save storage are injected. Every rule above lives in the Core assembly,
    which stays engine-free (`CoreAssemblyTests`), and is tested in EditMode with a fake clock
    and in-memory storage — no real disk, no real time. The device's real clock and file
    storage live in the Game layer. Core can't reach `JsonUtility`, so the serializer is either
    pure C# in Core or handed in from Game. *Source: build brief;
    `GuildMastersDescent.Core.asmdef` (`noEngineReferences`).*

### Placeholder numbers

| Number | Value | Where | Note |
|---|---|---|---|
| `SaveSlotCount` | 3 | new in `Tuning.cs` | R3 |
| `InjuryDurationSeconds` | 1800 | already in `Tuning.cs` | how long a new injury lasts; settling uses it unchanged |
| Restock interval, board size | — | not added | they belong to the recruiting board; a placeholder with no reader would be dead code |

## Out of Scope

- Mission timers. `Core Concept.md` § Time says missions complete while the player is away;
  timed missions are out of the MVP (`queue/focus.md` § Not included, § Later).
- The recruiting board itself, its candidates, and its restock rule — only the hook (R17).
- Paying gold to speed up healing (`Core Concept.md` § Missions) — the Dorms and roster item.
- Health changing over time in the hall.
- The title menu and its screens; settings and where they are stored.
- A dive in progress — the dive isn't built, so there is nothing of it to save yet.
- Anything the guild doesn't hold yet: the starting dungeon (`EhrensDocs/The Dungeon.md`),
  dive records. Each joins the save when its feature lands.
- Cloud sync, backups beyond R4, and protection against a player editing the save file.

## Open Questions

From the design docs, worded as they are:

- Does a new guild start with any members or gear, or only gold? (`EhrensDocs/Core
  Concept.md`) — *Not blocking:* new game uses whatever the model's new guild is (R22).

Raised by this PRD (the author's, not the docs'):

- What happens to a dive in progress when the app is closed or killed — is it saved and
  resumed, lost, or something else? *Not blocking this feature; blocks the dive's save shape,
  and it decides whether closing the app mid-battle can dodge a death.*
- Should a load also check the data model's other rules — gold below zero, a roster over the
  cap, durability outside 0 to its maximum, a negative injury time — and if so, repair or
  refuse? *Not blocking.*

Provisional defaults awaiting the user's word (each cheap to change; none alters the saved
shape):

- R10, R11 — a broken ID counter or equipped slot is repaired on load rather than the save
  being refused.
- R12 — duplicate or zero IDs make the save corrupt.
- R19 — a clock set backwards freezes the guild's clocks until real time catches up.
- R20 — no cap on how much away-time counts.
- R22 — new game never replaces an existing save unless asked to explicitly.
- R23 — the game saves itself on backgrounding and quit; no Save button.
- R3 — three save slots.
