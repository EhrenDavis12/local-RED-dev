**Build-readiness: 92**

# PRD: Settings — the four toggles, the purchases section, and both entry points

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Animations.md`,
> `Game Board Design.md`, `Tech Design.md`, `Game Overview.md`, `Rules.md`, `roadmap.md`.
> (`Alternative Game Styles.md` is a parking-lot doc and was not sourced.
> `design_handoff_game_ui/` is a read-only reference asset — screens `2b` and `1f` were
> read. No requirement below is sourced from the handoff.)
>
> **Revised** after two Decisions landed: `Menus and UI.md` → *What are the settings toggle
> sub-labels?* — four settled strings, quoted verbatim in requirement 18 — and `Theming.md`
> → *Do non-board controls make a sound?* — **one tap sound, everywhere**, which gives
> requirement 25 its sound half and closes `P2-02-audio.md`'s OQ-3.
>
> Earlier revisions: the fifth preference landing in `P1-04-persistence.md` (completing
> requirement 13); the purchases gap classified *ugly, not impossible*; four toggles and
> music as a theme concern; the app-wide haptic rule; the Kids Category gate; the
> pending-selection rule (closing Open Question 5); the spacing ruling (requirement 16).
>
> **Why 92.** Every control on both surfaces has a complete named write path, settled
> player-facing copy, and both feedback channels specified with assertions this PRD owns.
> **This PRD carries no open item of its own.** What remains is debt owned elsewhere and
> explicitly non-blocking: requirement 20's section ships unstyled until a Decision describes
> it, requirement 24's switch is wired to a channel nothing plays yet, and `surfaces.button.*`
> has no published sub-keys (requirement 19). None stops an agent; none is this PRD's to clear.

**Wave:** P4 — the settings surface itself, once the things it switches off exist.

**Files this PRD owns:** `lib/ui/menus/settings_screen.dart` (`SettingsScreen`) and
`lib/ui/menus/quick_actions_surface.dart` (`QuickActionsSurface`) — the two widgets
`P2-01-navigation.md` requirement 2's route table already names, at `Routes.settings`
(`/settings`) and `Routes.quickActions` (`/game/<id>/quick-actions`). `lib/ui/menus/` is
settled, not provisional: `Tech Design.md` → Decisions → Project structure — layer-first.

**Dependencies:**

- `P1-04-persistence.md` owns the settings state and its persistence, and publishes all four
  setters and all four `Provider<bool>` read points — requirement 13.
- `P1-03-theme-system.md` owns the theme object. Every value drawn here is a key path from
  its requirement 15 schema; requirement 16 tabulates them, and excepts spacing.
- `P2-02-audio.md` owns the audio layer and the `buttonTap` moment this surface fires
  (requirement 25). **It does not own music** — see requirement 24.
- `P2-03-haptics.md` owns the haptic this surface fires (requirement 25);
  `P2-04-animations.md` owns the animation channel.
- `P2-01-navigation.md` owns both entry points as routes (its requirement 10), the mid-game
  rule (its requirement 14), the exit transition (its requirement 15), dismissal (its
  requirement 5), and the structural bar on theme selection from a game (its requirement 18).
- `P3-02-move-input.md` owns the pending selection; requirement 2 states only what opening
  this surface does to it.
- `P4-05-purchase-flow.md` owns the purchase surface, the restore operation **and the
  parental gate** (its requirement 12). This PRD hosts the triggers — requirements 20–22.
- `P1-07-entitlements.md` owns what an entitlement is. This surface grants nothing.
- `P4-01-main-menu.md` owns the Settings button; `P3-03-scoreboard-turn-indicator.md`
  requirement 12 owns the in-game settings button. This PRD owns what each opens.

> **Ownership boundary, stated once.** The channel PRDs own each channel's behavior,
> including what happens when it is switched off. Requirements 7–10 restate that behavior
> because a switch is not specifiable without saying what it switches — but where this PRD
> and a channel PRD describe the same behavior, **the channel PRD is the owner**. See Open
> Question 4. The same split governs the purchases section. **Music is the one channel with
> no owning PRD at all** — requirement 24.

## Problem

Music, sound, haptics and animations are all theme-driven or app-driven behaviors a player
has no way to stop. There is no application code yet, so today there is no settings surface
at all: no way to mute a theme (`Theming.md` → Sound Decisions → Global mute), no way to
turn off the buzz that fires on every valid tap (`Menus and UI.md` → Vibrate on Touch), and
no way to turn animations off (`Animations.md` → Decisions → Turn animations off). Worse for
the pass-and-play case, there is no way out of a game short of finishing it — the docs put
the exit inside this same surface (`Menus and UI.md` → Decisions → How do you get back to
the main menu from a game?), so a player who starts a game is stuck in it. And the $4.99
open-game-slot unlock has a host named but not built: without this screen the product is
unbuyable, and the *Restore purchases* control Apple requires has nowhere to live.

## Goal

A player can reach settings from two places — the main menu's Settings button and the
gameplay screen's top-right button — and switch music, sound effects, vibrate on touch and
animations on or off. All four are global, player-owned and remembered between sessions, so
a theme can never override them; the in-game route also carries the exit, so a player can
change a setting or walk away mid-game without losing the game; and the screen carries the
purchases section that makes the slot unlock buyable and restorable, behind the parental
gate the Kids Category requires.

## Requirements

### Entry points

1. **The main menu's Settings button opens `SettingsScreen` at `Routes.settings`**, via
   `ref.read(appNavigatorProvider).openSettings()`.
   *Source: `Menus and UI.md` → Main Menu; → Settings Menu ("Reachable from two places: 1.
   The **main menu** (Settings button)"); `P2-01-navigation.md` requirements 2, 3 and 10.*

2. **The gameplay screen's settings button opens `QuickActionsSurface` at
   `Routes.quickActions`, and reaching it does not abandon or end the game in progress**,
   via `openQuickActions()`. The doc calls this the important requirement of the two:
   settings must be available mid-game.
   *Source: `Menus and UI.md` → Settings Menu ("you can get to settings without abandoning a
   game. That second one is the important requirement"); `Game Board Design.md` → Scoreboard;
   `P2-01-navigation.md` requirement 14, which makes it a child route so the game screen
   stays mounted beneath.*
   *Testable:* open the surface mid-game, dismiss it, and the board, whose turn it is, and
   the scoreboard are exactly as they were. (`P2-01` requirement 14's *Wave note* assigns
   this assertion here.)

   **A pending selection does not survive it.** Opening either surface clears a pending,
   unconfirmed move selection — not as a rule of this screen's, but as one instance of the
   single rule governing every tap off the nine quadrants.
   *Source: `Game Board Design.md` → Decisions → Does a tap outside the board clear a pending
   move? — "**Yes — any tap outside the nine quadrants clears a pending, unconfirmed
   selection.** That includes the legend/how-to-play strip, the scoreboard, the settings
   button, and opening any menu or sheet. One rule, uniformly applied."*
   *Testable:* with a pending selection active, tapping the settings button leaves no pending
   selection; dismissing returns to a board with none, and with the board, the current player
   and the scoreboard unchanged.
   *Boundary:* the pending selection is `P3-02-move-input.md`'s state (its requirement 20).
   The same Decision's near-miss consequence — the 3pt gutters and 5pt quadrant padding also
   counting as outside — is that PRD's, not this one's.

3. **The in-game entry point opens *quick actions* — a short list of things you can do
   mid-game — not just a list of toggles.**
   *Source: `Menus and UI.md` → How you reach settings from gameplay, and its **Quick
   actions contents (so far)** list: "Exit the game / back to main menu" and "The sound
   effects and vibrate toggles".*
   Requirement 6 fixes the contents of each surface.

4. **The settings button does double duty in-game: it is both the settings entry point and
   the way out of a game.** Exiting is available without finishing the game.
   *Source: `Menus and UI.md` → How you reach settings from gameplay; → Decisions → How do
   you get back to the main menu from a game?*
   *Not the only way out of a finished game:* `P3-04-game-over-rematch.md` requirement 5
   gives the result card two controls of its own and states the card is self-sufficient, so
   "a player is never dependent on the in-game settings button to leave a finished game,
   whatever that button's liveness turns out to be."

5. **Exiting from quick actions returns the player to the main menu and discards nothing.**
   The game stays in the open-games list with its own scoreboard and is resumable. The
   control calls `exitGameToMainMenu()` — requirement 19.
   *Source: `Menus and UI.md` → Leaving a game mid-play; → Decisions → What does an open
   game hold?; `Game Overview.md` → Decisions → Scoreboard lifetime.*
   *Testable:* leave mid-game, return to the open-games list, reopen the same game, and the
   board and its running series score are unchanged.
   The routing half — `go` or `pop` — is `P2-01-navigation.md` requirement 15 and its Open
   Question 2.

### The four toggles

6. **There is no *setting* on either surface beyond these four — Music, Sound effects,
   Vibrate on touch, Animations — each a plain two-state on/off. The two surfaces differ,
   and this is their shape:**

   | Surface | Toggles | Exit | Purchases |
   |---|---|---|---|
   | `SettingsScreen` (main menu) | **all four** — Music, Sound effects, Vibrate on touch, Animations | no | yes — requirement 20 |
   | `QuickActionsSurface` (in game) | Sound effects, Vibrate on touch | yes | no |

   *Source: `Menus and UI.md` → Settings Menu ("**Contents so far — four toggles**", and the
   mock drawing all four); → Decisions → What are the settings on a fresh install? ("**All
   four toggles default to on**"); → Persistence ("five persisted preferences — theme, music,
   sound, vibration, and animations"); `Theming.md` → Decisions → Do all four toggles ship,
   and is music a theme concern?*
   *Testable:* `SettingsScreen` renders exactly four switches, `QuickActionsSurface` exactly
   two; neither widget tree contains a fifth.

   **The in-game row is a fence, and the fence needs saying out loud.**
   `Menus and UI.md`'s quick-actions list names the sound effects and vibrate toggles and
   nothing else — but that list **predates the four-toggle Decision and was not updated with
   it**, so its silence on Music is not evidence any more than its silence on Animations was.
   Fenced to the two the doc names, because they are the two it names; reversible.
   `P2-01-navigation.md` requirement 2 makes reversing it a change to **widget contents
   only** — not the route table, the operation mapping, or any call site. Which of the four
   the in-game surface carries is part of Open Question 1's substance.
   *No default is resolved here.* "Nothing stored" resolves to `true` in `Settings.defaults`
   and nowhere else — `P1-04-persistence.md` requirement 26. This surface writes no `?? true`.

7. **Sound effects is a global mute for the game's one-shot sounds** — global for the whole
   game rather than per-theme, separate from the theme, and it mutes *any* theme. It is a
   different channel from Music (requirement 24): switching one off does not switch the other.
   *Source: `Theming.md` → Sound Decisions → Global mute; `Menus and UI.md` → Decisions →
   Should there be a mute button, and where does it live?; → Settings Menu, whose table
   distinguishes the two.*
   *Testable:* with sound off and music on, switch between Neon and Classic Red vs Blue and
   no sound effect plays under either, while the music channel is untouched.
   *Owner of the behavior:* `P2-02-audio.md` requirement 16. This PRD owns the switch.
   *Note:* this toggle also gates the tap sound its own row makes — requirement 25's
   `buttonTap` runs through the same mute, since `P2-02` req 16 puts the gate inside the
   layer. A player muting sound stops hearing the taps that mute it.

8. **Vibrate on touch switches the haptic on and off.** With it on, the haptic fires on
   every valid click, including the first tap of a two-tap move; with it off, no haptic
   fires anywhere.
   *Source: `Menus and UI.md` → Settings Menu table; → Vibrate on Touch;
   `Game Board Design.md` → Haptic Rule ("Subject to the vibrate-on-touch setting being
   on").*
   *Testable:* with a recording haptic double, flipping this switch off and performing a
   valid board tap records zero haptics; flipping it on and repeating records exactly one.
   *Owner of the behavior:* `P2-03-haptics.md` requirements 10–12. This PRD owns the switch.

9. **Animations off means the game does the thing instantly** — the mark simply appears, the
   quadrant is simply claimed. No animation, and no substitute effect, fade or transition
   standing in for one.
   *Source: `Animations.md` → Decisions → Animations off = instant state change; → Turn
   animations off — a global setting.*
   *Testable:* with animations off, a confirmed move produces the new board state with no
   intermediate frames and no substitute effect.
   *Owner of the behavior:* `P2-04-animations.md` requirements 19–21, whose requirement 17
   names this PRD as the owner of the switch.

10. **iOS Reduce Motion does not drive the Animations toggle.** There is exactly one control
    and the player owns it.
    *Source: `Animations.md` → Decisions → Does iOS Reduce Motion drive the animations
    toggle?*
    *Owner of the behavior:* `P2-04-animations.md` requirement 18.

11. **All four are global, player-controlled and not theme-defined.** No key in a theme file
    sets, forces or reads any of the four, and switching themes never changes their values.
    This holds for Music too: a theme supplies the music, and the player's mute of it is not
    the theme's to override.
    *Source: `Menus and UI.md` → Settings Menu ("All four are **global**,
    **player-controlled**, and **not theme-defined**"); `Animations.md` → Decisions → Turn
    animations off; `Theming.md` → Sound Decisions → Global mute; → Decisions → Do all four
    toggles ship, and is music a theme concern? `P1-03-theme-system.md` requirement 30 holds
    the same line from the schema side.*
    *Testable:* set the four toggles, switch the active theme, and all four are unchanged.

12. **The two entry points edit the same values** — one global value per toggle, because both
    surfaces read and write the same provider (requirement 13).
    *Testable:* change a toggle in `QuickActionsSurface`, exit to the main menu, open
    `SettingsScreen`, and it shows the changed value (and the reverse).

13. **Every switch writes through `SettingsNotifier`'s setters and reads through the four
    settings providers. `PreferencesRepository` is never called from this surface.**

    ```dart
    // write — the only write path for these preferences
    ref.read(settingsProvider.notifier).setMusic(value);
    ref.read(settingsProvider.notifier).setSoundEffects(value);
    ref.read(settingsProvider.notifier).setVibrateOnTouch(value);
    ref.read(settingsProvider.notifier).setAnimations(value);

    // read — Provider<bool>, synchronous, never null
    ref.watch(musicEnabledProvider);
    ref.watch(soundEffectsEnabledProvider);
    ref.watch(vibrateOnTouchEnabledProvider);
    ref.watch(animationsEnabledProvider);
    ```

    All eight symbols are declared in `lib/state/settings_providers.dart` by
    `P1-04-persistence.md` requirements 26 and 27, over a `Settings` class whose `music`
    field is backed by `ttt.pref.musicEnabled`. **This PRD is `musicEnabledProvider`'s first
    consumer** — that PRD ships it noting it has none yet.
    *Source: `P1-04-persistence.md` requirement 27 — the setters update `state` first and then
    persist, and "a caller that writes to the repository directly bypasses the provider and
    leaves the two out of step — so `P4-04-settings.md`'s switches call the setters, not the
    repository."*
    **Why this is not a detail.** Writing to the repository would still persist and still
    reload, so the switch would *look* correct — while every in-session consumer kept reading
    a stale provider. `P2-03-haptics.md` requirement 12 (a vibrate toggle flipped in quick
    actions governing the very next tap) would fail silently.
    *Testable:* a scan of `lib/ui/menus/` finds no `PreferencesRepository` and no
    `preferencesRepositoryProvider`; with a fake repository, flipping the vibrate switch makes
    `vibrateOnTouchEnabledProvider` read the new value on the next read **within the same
    frame**, and records exactly one write.

### What the toggles are, structurally

14. **Music, Sound and Animations switch off a *theme channel*; Vibrate switches off an *app
    behavior* that is never theme-defined at all.** The theme object has no haptic concept,
    and turning a theme channel off suppresses it without altering the active theme or its
    definition.
    *Source: `Theming.md` → What a Theme Does NOT Control (whose table lists Music as
    theme-controlled and haptics as not); → What Is a Theme?; `P1-03-theme-system.md`
    requirement 29.*
    *Testable:* the theme schema defines music, sound and animation values and nothing
    haptic; muting does not modify the loaded theme.

15. **Neither surface offers theme selection or a theme change**, and neither invokes
    `openThemeSelection()`.
    *Source: `Theming.md` → Decisions → Where theme selection lives; → Can you change the
    theme mid-game; `P2-01-navigation.md` requirement 18; `P4-03-theme-selection.md`
    requirement 19.*
    *Testable:* no call site in either of this PRD's files invokes `openThemeSelection()`,
    and no control on either surface changes the selected theme.

16. **Every value drawn on both surfaces comes from the theme — except spacing, which is
    code** — and both pass the hardcoded-theme-value test with the baseline at zero.

    | What | Key path (`P1-03-theme-system.md` req 15) |
    |---|---|
    | The settings card | `surfaces.settingsCard.{fill,border,radius}` |
    | A toggle row's text | `surfaces.settingsCard.toggleRow.{labelStyle,subLabelStyle}` |
    | The switch | `surfaces.settingsCard.switch.{trackOn,trackOff,knobOn,knobOff,glowOn}` |
    | The in-game sheet | `surfaces.sheet.{fill,radius}`, `surfaces.sheet.header.{titleStyle,subStyle,closeControl}` |
    | The scrim behind it | `surfaces.scrim.settings` |
    | The exit control | `surfaces.button.secondary` — requirement 19 |
    | The close control | `icons.close.{kind,set,name,path,tint,size}`, plus `icons.close.button.{fill,radius,size}` where drawn — requirement 23 |
    | The purchases section | `surfaces.settingsCard.purchases.{sectionDivider,priceRow,restoreControl}` — **`deferred`**, see requirement 20 |

    The four toggle rows are four instances of the same row keys; no per-setting key exists
    or is needed. **This screen reads no `sound` key** — the tap sound is `P2-02-audio.md`'s
    to resolve from `sound.buttonTap`, not this screen's to look up (requirement 25).
    **The spacing exception, and where the line falls.** The card's padding, the sheet's
    inset, the gap between toggle rows and every margin on both surfaces are **constants in
    this PRD's own files**, not theme lookups — and their presence in the source is not a
    violation of this requirement.
    *Source: `Theming.md` → Decisions → Does a theme control spacing and padding? — "**No.
    Spacing and layout numbers are fixed in the code, not theme-controlled — for now.**" The
    reason is enforcement: the guard "cannot catch a hardcoded gap."*
    **Classify a new key by the boundary, not by the word "padding"** — `P1-03-theme-system.md`
    requirement 15: a theme controls **the drawn geometry of a thing itself** — stroke width,
    glyph size, corner radius, glow spread — while code controls **where things sit relative
    to one another**. So `radius`, the switch's knob and track sizes and `icons.close.size`
    remain themed; `surfaces.settingsCard.padding` and `surfaces.sheet.padding` no longer
    exist, removed in schemaVersion 7 and **must not be read or re-added**.

### Text scaling

17. **This surface offers no text-size control of its own**, because Dynamic Type is not
    supported in this version.
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type?*
    *Testable:* no control on either surface changes text size.
    *Not deliverable here:* the app-wide clamp needed to make "does not scale" true is not
    this surface's, and no PRD owns it — `P4-01-main-menu.md` requirement 20 records the same
    gap. See Open Question 3.

### The surface's own controls

*Requirements 18–25 are appended rather than inserted, so numbers 1–17 stay stable —
`P1-03-theme-system.md`, `P1-04-persistence.md`, `P2-01-navigation.md`, `P2-02-audio.md`,
`P2-03-haptics.md`, `P2-04-animations.md` and `P4-03-theme-selection.md` all cite them.*

18. **Each toggle row carries its name and a sub-label, both settled copy.** The name reads
    `surfaces.settingsCard.toggleRow.labelStyle`; the sub-label reads
    `surfaces.settingsCard.toggleRow.subLabelStyle`. **The four sub-labels, verbatim:**

    | Toggle | Sub-label |
    |---|---|
    | Music | Tunes while you play |
    | Sound Effects | Buzzes, pops and splats |
    | Vibrate on Touch | A little buzz on every tap |
    | Animations | Marks that pop and glow |

    *Source: `Menus and UI.md` → Decisions → What are the settings toggle sub-labels? —
    "**Each of the four toggles carries a short playful sub-label**, matching the handoff's
    voice and the fact that children are a target audience," and closing: "**These are
    settled strings — quote them exactly, don't paraphrase.**"*
    *Testable:* one row per setting; each renders that setting's name and exactly the string
    above, character for character.
    **The Decision supersedes the handoff's sub-labels, deliberately — do not "correct" these
    back.** Three of the four differ from `design_handoff_game_ui/README.md` → `1f`, which
    draws "Background track", "A little buzz on every **valid** tap" and "Marks pop, glow
    **and jiggle**". The difference was put to the user with both sets side by side,
    including the argument that the handoff's are more literally accurate, and the strings
    above are what they chose. A future reader comparing the two will find a mismatch that
    looks like drift and is not; the Decision is the source of truth for this copy, and the
    handoff is not.

19. **Exit is one item in `QuickActionsSurface`, labelled as leaving the game and going back
    to the main menu, drawn from `surfaces.button.secondary`, calling
    `ref.read(appNavigatorProvider).exitGameToMainMenu()`.** No `go_router` symbol is
    imported or called anywhere in this PRD's files; `P2-01-navigation.md` requirement 1's
    scan fails the build if one is.
    *Source: `Menus and UI.md` → How you reach settings from gameplay; `P2-01-navigation.md`
    requirements 3 and 15, whose *Wave note* names this control as this PRD's. The two button
    tiers are the schema's shape — `P1-03-theme-system.md` requirement 15 publishes
    `surfaces.button.{primary,secondary}` as `required` — not a phrasing quoted from it.*
    *Testable:* exactly one exit affordance; activating it calls `exitGameToMainMenu()` once
    on a recording `AppNavigator` fake; a scan of `lib/ui/menus/` finds no `go_router` import.
    *Not settled — emphasis.* Whether exit warrants a **destructive** treatment is undecided
    and it cannot borrow one: `surfaces.destructive` is `required` and authored, but its two
    paths are scoped to deleting an open game (`P4-02-open-games-list.md` reqs 17, 27).
    Neither describes a menu row that ends nothing. Until decided, exit reads
    `surfaces.button.secondary`.
    *Upstream gap — the tier's own shape is unpublished.* `surfaces.button.{primary,secondary}`
    is `required` but its **sub-keys are not enumerated**, unlike `surfaces.input` or
    `surfaces.settingsCard` beside it in the same table. Three PRDs now read it — this one,
    `P4-01-main-menu.md` and `P4-02-open-games-list.md` — and none can name the members it
    resolves to. That is `P1-03`'s to close; see Open Question 3.

### The purchases section

20. **`SettingsScreen` carries a purchases section, distinct from the toggles, holding two
    items: the $4.99 open-game-slot unlock, and a global *Restore purchases* control.**
    `QuickActionsSurface` does not carry it — requirement 6's table.
    *Source: `Menus and UI.md` → Decisions → Where the open-game slot unlock is sold; → How
    many open games do we keep?*
    *Testable:* `SettingsScreen` presents a purchases section containing exactly these two
    items, distinct from the toggle rows; `QuickActionsSurface` presents neither.

    **It ships unstyled until a Decision describes it — this does not block.**
    `surfaces.settingsCard.purchases.{sectionDivider,priceRow,restoreControl}` is `deferred`
    in `P1-03-theme-system.md` requirement 15, whose triage rule classifies the absence as
    **ugly, not impossible**: *"Ugly can wait for a design pass — the feature ships, looks
    wrong, and is fixed by authoring one value later with no code change, because the key
    already exists and the consumer already reads it."* It names this section explicitly —
    *"`surfaces.settingsCard.purchases.*` is ugly — `P4-04` can render its section
    unstyled."* Contrast the trash glyph, authored immediately because with no slot and no
    permitted literal there was **no legal implementation at all**.
    So: build the section, read the keys, accept that it looks plain until values are
    authored, and **do not hardcode a substitute** — `deferred` still forbids that. What is
    missing is a Decision describing what the section *is*: `P1-03`'s *Blocking* item 6.
    *Boundary:* this PRD owns the section and the two controls, and that activating one
    invokes `P4-05-purchase-flow.md`'s API. It owns nothing they present.

21. **The purchase control invokes `P4-05-purchase-flow.md`'s gated purchase entry point, and
    this surface implements no parental gate of its own.**
    *Source: `P4-05-purchase-flow.md` requirement 12, which **is** the gate — "no purchase can
    be initiated without passing it" — and whose ownership block states that
    "`P4-04-settings.md` should defer to this requirement rather than specify a gate of its
    own." Underlying decision: `Tech Design.md` → Decisions → Kids category, scope purchases
    only.*
    *Testable:* activating the purchase control calls `P4-05`'s purchase entry point exactly
    once; a scan of this PRD's files finds no gate, challenge or age-check widget of its own.
    *Restore is not gated:* `P4-05` requirement 12 scopes the gate to the purchase operation,
    and a restore makes no charge.

22. **The *Restore purchases* control is a compliance control, not the mechanism by which
    entitlements arrive.** It is present because Apple's review guidelines require it;
    activating it invokes `P4-05-purchase-flow.md`'s restore operation (its requirement 5),
    behind which is `AppStore.sync()`. Entitlements are authoritative from
    `Transaction.currentEntitlements` and repopulate on their own.
    *Source: `Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend
    needed ("the control is a compliance requirement more than a functional one").*
    *Testable:* the control invokes the restore operation exactly once; **no
    entitlement-granting logic lives in this surface**; a fresh install signed into the same
    Apple ID holds its entitlements with this control never having been tapped.

### Leaving the surface

23. **Both surfaces present one dismiss control — a close control reading `icons.close`, and
    on the in-game sheet positioned per `surfaces.sheet.header.closeControl` — calling
    `ref.read(appNavigatorProvider).dismissCurrent()`.**
    *Source: `P2-01-navigation.md` requirements 5 and 14; `P1-03-theme-system.md`
    requirement 15, whose `icons.close` slot is `required` and cited to this PRD.*
    *Testable:* exactly one dismiss affordance per surface; activating it calls
    `dismissCurrent()` once on a recording fake; from `/game/abc/quick-actions` the player
    lands back on `/game/abc`.
    **This is a fence, not a Decision** — `P2-01-navigation.md` → Open Question 9 records the
    gap. If the answer is a back affordance, `icons.chevronLeft` is the provisioned
    alternative and the call is unchanged.

### The Music toggle, and the layer it does not have

24. **The Music switch is a global mute for the theme's background music, on the same terms
    as the other three: global, player-controlled, not theme-defined, persisted, defaulting
    to on.**
    *Source: `Theming.md` → Decisions → Do all four toggles ship, and is music a theme
    concern?; `Menus and UI.md` → Settings Menu ("**Music** — Global mute toggle for
    background music. Separate from the theme — mute any theme's music"); → Persistence; →
    What are the settings on a fresh install?*

    **The switch is fully wired; what it controls does not exist yet.** Only the second half
    is outstanding:

    - **Wired.** `P1-04-persistence.md` publishes `ttt.pref.musicEnabled`, the `music` field,
      `setMusic` and `musicEnabledProvider` — requirement 13 calls them. The row renders,
      flips, persists and reloads today.
    - **Not played.** No PRD plays music. `P2-02-audio.md` owns one-shot effects; its
      `SoundMoment` enum has five members and no music among them, and it scopes a music
      layer as a **sibling rather than an extension of itself** — looping, lifecycle across
      screens and ducking are a different problem from fire-and-forget. That layer is unowned.
    - **The theme key exists; its shape does not.** `sound.music` is a placeholder Neon ships
      as an explicit `null`. `P1-03-theme-system.md` records music as `deferred` rather than
      adding a key, because the shape turns on the open per-screen question; its *Blocking*
      item 1 writes out both candidates without picking one. There is a confirmed consumer of
      the **setting** — this toggle — and none of the **asset**.

    *Testable, in two parts.* **Now:** `SettingsScreen` renders the Music row, and flipping it
    persists and reloads like the other three. **When a music layer exists:** with Music off,
    no music plays under any theme, and the Sound effects toggle does not change that either
    way.
    *Not answered here, and not to be answered by an implementer:* whether a theme's music
    loops, whether it differs by screen, and where the audio comes from — all three are open
    in `Theming.md` → Open Questions.

### Feedback on this surface's own controls

25. **Every control on both surfaces fires both feedback channels on activation — the haptic
    and the tap sound.** The six are the four switches, the exit control and the dismiss
    control; on `QuickActionsSurface` the two switches, exit and dismiss.

    ```dart
    ref.read(hapticServiceProvider).validAction();
    ref.read(audioLayerProvider).play(SoundMoment.buttonTap);
    ```

    *Source — haptics: `Game Board Design.md` → Decisions → Does the haptic fire on non-board
    controls? — "**Yes — every valid tap buzzes, anywhere in the app.** Menu buttons, theme
    rows, settings toggles, the game-over card's controls, the settings gear — not only board
    cells."*
    *Source — sound: `Theming.md` → Decisions → Do non-board controls make a sound? — "**Yes
    — one tap sound, everywhere.** Every button, row and toggle plays the same short tap
    sound: menu buttons, theme rows, settings toggles, the game-over card's two controls, the
    trash button and the modal's Yes and No," which the same Decision frames as restoring
    symmetry with the haptic rule "rather than one buzzing where the other is silent."*
    **`buttonTap` is one moment and one sound file, not a family** — `P2-02-audio.md`
    requirement 6. This surface names the moment and nothing else: no asset path, no player,
    no await, and it reads no `sound` key.
    **Both gates live inside their layers, not here.** The haptic is gated on vibrate-on-touch
    (requirement 8) and the sound on sound-effects (requirement 7); this surface calls both
    unconditionally. One consequence worth naming: muting sound effects silences the tap of
    the switch that mutes them.
    *Testable — and it is this PRD's to write, not the layers':* `P2-02-audio.md` requirement
    6 states that a control's tap reaching `play` exactly once is "a **call-site fact, owned
    by each calling PRD**", naming this requirement for the four toggles, exit and dismiss;
    `P2-03-haptics.md` says the same for `validAction()`. So: activating any of the six
    records exactly one `validAction()` and exactly one `play(SoundMoment.buttonTap)` on
    recording fakes — never zero, never twice — and with the respective setting off, that
    channel records zero while the other still records one.
    *Owners of the behavior:* `P2-03-haptics.md` and `P2-02-audio.md`. This PRD owns only the
    call sites and their counts.

## Out of Scope

- **Storing the preferences and resolving the fresh-install default**:
  `P1-04-persistence.md`, including all four setters and read points.
- **The haptic mechanism and its gate**: `P2-03-haptics.md`. **The audio layer, the mute
  gate, and resolving `sound.buttonTap`**: `P2-02-audio.md`. Requirement 25 names call sites
  and counts only.
- **Music playback** — no owner at all; requirement 24.
- **Whether a theme's music loops, differs by screen, or where it comes from**:
  `Theming.md` → Open Questions.
- **The animations system, the instant-state-change path, and the Reduce Motion rule**:
  `P2-04-animations.md`.
- **Everything the purchase and restore controls present**, including the parental gate:
  `P4-05-purchase-flow.md`.
- **What an entitlement is and what happens when one lapses**: `P1-07-entitlements.md`.
- **The open-games list's behavior at the cap and the delete action**:
  `P4-02-open-games-list.md`.
- **The result card's own controls**, and whether this screen's entry button is live over it:
  `P3-04-game-over-rematch.md` req 5.
- **The routing layer**: `P2-01-navigation.md`.
- **The main menu and the in-game settings button themselves**: `P4-01-main-menu.md`,
  `P3-03-scoreboard-turn-indicator.md` req 12.
- **The pending move selection itself**: `P3-02-move-input.md`.
- **Theme selection and the theme system**: `P1-03-theme-system.md`,
  `P4-03-theme-selection.md`. **Enumerating `surfaces.button.*`'s sub-keys** is `P1-03`'s —
  requirement 19.
- **The read-only "Theme — Picked from the main menu" card — declined, not accepted.**
  `P4-03-theme-selection.md` hands `2b`'s read-only theme display here. This PRD does not
  specify one, because no design doc names it — it exists only in the handoff. Requirement
  6's "no fifth setting" is *not* the reason: a read-only display is not a setting, and
  requirement 15 forbids only *changing* the theme. The card has no owner — a visible gap
  rather than a silent one. See Open Question 3.
- **A confirmation prompt on exit.** Unsettled — Open Question 2.

## Open Questions

### 1. Is quick actions the same screen as the main menu's settings, or a trimmed-down version?

As worded in `Menus and UI.md` → How you reach settings from gameplay:

> Undecided: whether quick actions is the *same* settings screen as the main menu's, or a
> trimmed-down in-game version with the exit option added.

**Still formally open — fenced, not answered**, and the four-toggle Decision sharpened what
the question contains: **which of the four the in-game surface carries.** Requirement 6
fences it to Sound effects and Vibrate on touch — the two the doc's quick-actions list names
— while noting that list predates the four-toggle Decision, so its silence on Music is not
evidence any more than its silence on Animations was. A fence is not an answer.

If the "same screen" reading lands, three things arrive in-game together: the Animations row,
the Music row, and the purchases section with its parental gate. The last is the one worth
deciding deliberately rather than inheriting.

Also carried by `P2-01-navigation.md` → Open Question 7.

### 2. Does leaving a game still need a confirmation prompt?

As worded in `Menus and UI.md` → Leaving a game mid-play:

> Whether leaving still needs a confirmation prompt is undecided; the original reason for
> one ("Leave game? Your score will be lost") no longer applies.

Also carried by `P2-01-navigation.md` → Open Question 6.

### 3. Gaps found while writing this PRD (flagged by the PRD author, not asked by the docs)

**Mine to carry: none.** Every item this PRD raised as its own has been answered — the
sub-label copy (requirement 18) was the last, and the Music-versus-three-toggles
disagreement, the parental-gate duplication and the pending-selection question before it.

**Debt owned elsewhere, non-blocking:**

- **What the purchases section *is*** (requirement 20) — `P1-03-theme-system.md` *Blocking* 6.
  Classified *ugly, not impossible*: the section ships unstyled.
- **`surfaces.button.*` publishes no sub-keys** (requirement 19). The key is `required` and
  its two tiers are real, but nothing enumerates what a tier contains — no fill, border,
  radius or label style — while neighbouring entries in the same table do. Three consumers
  read it: this PRD, `P4-01-main-menu.md` and `P4-02-open-games-list.md`. `P1-03`'s to close,
  and its own triage rule decides whether that counts as *ugly* or *impossible*.
- **Nothing plays music** (requirement 24) — unowned; `P2-02-audio.md` scopes it as a sibling
  layer. **The `sound.music` key's shape** — `P1-03` *Blocking* item 1.
- **Whether the exit control is a destructive treatment** (requirement 19).
- **The read-only Theme card has no owner** — declined above; `P4-03` still points here.
- **Dynamic Type has no owner at the app level** (requirement 17); `P4-01-main-menu.md`
  requirement 20 records the same gap.

**Stale cross-references in sibling PRDs, routed and not fixed here:**

- **`P2-04-animations.md` requirement 17** — "sits alongside the sound-effects and vibrate
  toggles in the Settings menu" is requirement 6's territory, and numerically stale: four
  toggles, not three.
- **`P2-01-navigation.md` → Open Question 11** should be retired; the pending-selection
  question it records as disputed is closed.
- **`P4-05-purchase-flow.md`'s host question** is closed but its preamble still reads open.

### 4. Where does the switch end and the behavior begin?

The channel PRDs own what "off" means; requirements 7–10 restate it and each names its owner.
If an implementer finds the two disagreeing, the channel PRD wins. Requirements 20–22 follow
the same rule with `P4-05-purchase-flow.md`, and requirement 25 with `P2-02-audio.md` and
`P2-03-haptics.md` — where this PRD owns the call sites and their counts, and neither layer
owns whether its own control fired. **Requirement 24 is the exception that proves it:** the
Music switch has no channel PRD to defer to, which is why it is written as a gap.

### 5. Does opening this surface clear a pending move selection? — CLOSED

**Answered: yes.** `Game Board Design.md` → Decisions → *Does a tap outside the board clear a
pending move?*:

> **Yes — any tap outside the nine quadrants clears a pending, unconfirmed selection.** That
> includes the legend/how-to-play strip, the scoreboard, the settings button, and opening any
> menu or sheet. One rule, uniformly applied.

Applied in requirement 2, which now asserts it rather than declining to.

**Kept as a numbered stub, with the reason it mattered.** Before the Decision, four PRDs
touched this and none owned it: `P3-02-move-input.md` → OQ-1 held it open, while
`P3-05-how-to-play.md` requirement 15 asserted as a testable that a tap on its strip clears a
pending selection *"exactly as a tap on any other non-board area does"* — and
`P3-03-scoreboard-turn-indicator.md` requirement 12 puts the settings button in exactly such
an area. `P3-05` ships in wave 3 and this PRD in wave 4, so the question would have been
answered a wave early by a requirement whose author was describing a legend. The settled
answer matches what that PRD asserted — but it is now settled deliberately, from one Decision
all four cite, rather than inherited as a side effect of someone else's generality.
