# PRD: Settings — the three toggles, the purchases section, and both entry points

> **Status:** Draft · Source docs read: `Menus and UI.md`, `Theming.md`, `Animations.md`,
> `Game Board Design.md`, `Tech Design.md`, `Game Overview.md`, `Rules.md`.
> (`Alternative Game Styles.md` is a parking-lot doc and was not sourced.
> `design_handoff_game_ui/` is a read-only reference asset — screens `2b` and `1f` were
> read, and where the handoff and the docs disagree the disagreement is recorded under Open
> Questions rather than resolved. No requirement below is sourced from the handoff.)
>
> **Revised** after `Menus and UI.md` → Decisions → *Where the open-game slot unlock is
> sold* and `Tech Design.md` → Decisions → *Kids category* and → *Entitlements — Apple
> stores them, no backend needed* were added. Both docs were re-read in full. The screen is
> no longer only settings — see requirements 20–22.

**Wave:** P4 — the settings surface itself, once the things it switches off exist.

**Dependencies:**

- `P1-04-persistence.md` owns storing and restoring the four preferences. This PRD reads
  and writes through that layer and defines no storage of its own.
- `P1-03-theme-system.md` owns the theme object and its materialization. This PRD requires
  only that the three toggles are *not* part of it, and names the slots this surface reads.
- `P2-02-audio.md`, `P2-03-haptics.md`, `P2-04-animations.md` own the three channels —
  **the mechanism and what "off" means**. This PRD owns the player-facing switch UI for
  each and nothing about the behavior behind it. All three are wave 2, so they ship first.
- `P2-01-navigation.md` owns the two entry points as routes and the rule that reaching
  settings mid-game does not leave the game (its requirements 7 and 10). Its Out of Scope
  assigns **the exit control's own presentation** to this PRD — requirement 19.
- `P4-05-purchase-flow.md` owns the purchase surface, the restore operation, and everything
  a trigger presents, exposed as an invocable API (its requirements 5 and 10). This PRD is
  the **host** that surfaces the two controls — requirements 20–22. Same wave,
  parallel-safe: the coupling is an interface, not a screen.
- `P1-07-entitlements.md` owns what an entitlement is and how it is held. This surface
  grants nothing and stores nothing about ownership.
- `P4-01-main-menu.md` owns the Settings button on the main menu; this PRD owns what that
  button opens. Same wave, parallel-safe.
- `P3-03-scoreboard-turn-indicator.md` owns the placement of the in-game settings button in
  the scoreboard strip (its requirement 12); this PRD owns what tapping it opens. Wave 3,
  so it ships first.

> **Ownership boundary, stated once.** The three channel PRDs own each channel's behavior,
> including what happens when it is switched off. Requirements 7–10 below restate that
> behavior because a switch is not specifiable without saying what it switches — but where
> this PRD and a channel PRD describe the same behavior, **the channel PRD is the owner**
> and this one is the restatement. See Open Question 4. **The same split governs the
> purchases section:** this PRD owns the section and its entry points, `P4-05` owns what
> those entry points present.

## Problem

Sound, haptics and animations are all theme-driven or app-driven behaviors a player has no
way to stop. There is no application code yet, so today there is no settings surface at
all: no way to mute a theme (`Theming.md` → Sound Decisions → Global mute), no way to turn
off the buzz that fires on every valid tap (`Menus and UI.md` → Vibrate on Touch), and no
way to turn animations off (`Animations.md` → Decisions → Turn animations off). Worse for
the pass-and-play case, there is also no way out of a game short of finishing it — the
docs put the exit inside this same surface (`Menus and UI.md` → Decisions → How do you get
back to the main menu from a game?), so without it a player who starts a game is stuck in
it. And the $4.99 open-game-slot unlock now has a host named but not built: without this
screen the product is unbuyable, and the *Restore purchases* control Apple requires has
nowhere to live.

## Goal

A player can reach settings from two places — the main menu's Settings button and the
gameplay screen's top-right button — and from either one switch sound effects, vibrate on
touch and animations on or off. The three are global, player-owned and remembered between
sessions, so a theme can never override them; because the in-game route is a set of quick
actions that also contains "exit to main menu", a player can change a setting or walk away
mid-game without losing the game, which stays in the open-games list with its own
scoreboard; and the screen carries the purchases section that makes the slot unlock buyable
and restorable, behind the parental gate the Kids Category requires.

## Requirements

### Entry points

1. **The main menu's Settings button opens the settings surface.**
   *Source: `Menus and UI.md` → Main Menu ("**Settings** — opens the settings menu");
   → Settings Menu ("Reachable from two places: 1. The **main menu** (Settings button)");
   → Screens (so far) #6.*

2. **The gameplay screen's settings button opens the settings surface too, and reaching it
   does not abandon or end the game in progress.** The doc calls this the important
   requirement of the two: settings must be available mid-game.
   *Source: `Menus and UI.md` → Settings Menu ("2. The **gameplay screen** — you can get to
   settings without abandoning a game. That second one is the important requirement");
   → How you reach settings from gameplay; `Game Board Design.md` → Scoreboard.*
   *Testable:* open the surface mid-game, dismiss it, and the board, whose turn it is, and
   the scoreboard are exactly as they were.
   *Deliberately not asserted:* what happens to a **pending (selected-but-unconfirmed)
   move** while the surface is up. An earlier draft of this requirement asserted as
   testable that the pending selection survives; that is not settled by any design doc, and
   `P3-02-move-input.md` → OQ-1 carries it as an open question. It is demoted here to Open
   Question 5 rather than decided in either direction.

3. **The in-game entry point opens *quick actions* — a short list of things you can do
   mid-game — not just a list of toggles.** Contents so far: exit the game / back to the
   main menu, plus the sound effects and vibrate toggles.
   *Source: `Menus and UI.md` → How you reach settings from gameplay ("Tapping it opens
   **quick actions** — a short list of things you can do mid-game, including **exit the
   game** back to the main menu"), and its **Quick actions contents (so far)** list.*
   *Note:* whether the Animations toggle also appears here follows from Open Question 1 —
   the doc's quick-actions list names only sound and vibrate, while the Settings Menu
   section names three toggles. Requirement 6 is scoped accordingly, and requirement 20
   carries the same open scoping for the purchases section.

4. **The settings button does double duty in-game: it is both the settings entry point and
   the way out of a game.** Exiting is available without finishing the game.
   *Source: `Menus and UI.md` → How you reach settings from gameplay ("So the settings
   button does double duty in-game"); → Decisions → How do you get back to the main menu
   from a game? ("It opens quick actions, which include exiting the game. You don't have to
   finish a game to leave it").*

5. **Exiting from quick actions returns the player to the main menu and discards nothing.**
   The game stays in the open-games list with its own scoreboard and is resumable.
   *Source: `Menus and UI.md` → Leaving a game mid-play ("going back to the main menu
   doesn't discard anything — the game stays in the open-games list with its own
   scoreboard, and you can pick it up again"); → Decisions → What does an open game hold?;
   `Game Overview.md` → Decisions → Scoreboard lifetime.*
   *Testable:* leave mid-game, return to the open-games list, reopen the same game, and the
   board and its running series score are unchanged.
   The routing half — whether this pops to an existing main menu or pushes a fresh one — is
   `P2-01-navigation.md` requirements 11 and 12, and its Open Question 2. The control the
   player taps to trigger it is requirement 19 below.

### The three toggles

6. **There is no *setting* on either surface beyond these three — Sound effects, Vibrate on
   touch, Animations — and each is a plain two-state on/off.** Scoped, because the two
   surfaces are not settled to be the same thing:
   - **The main-menu surface draws all three.** *(`Menus and UI.md` → Settings Menu:
     "Contents so far — three toggles".)*
   - **How many of the three the in-game quick-actions surface draws is not settled.** The
     doc's quick-actions list names only the sound effects and vibrate toggles
     (requirement 3); whether the Animations toggle joins them follows from Open
     Question 1, and this PRD does not decide it.
   - **Neither surface gains a fourth setting**, whichever way Open Question 1 falls. This
     is unaffected by requirement 20: a purchase item is **not a setting**, so the
     purchases section does not make a fourth. What it does change is that the screen is no
     longer *only* settings — see requirement 20, and the title of this PRD.
   *Source: `Menus and UI.md` → Settings Menu; → How you reach settings from gameplay
   (**Quick actions contents (so far)**); → Persistence (the persisted preferences are
   theme, sound, vibrate, animations — "So there are four persisted preferences").*
   *Note:* the handoff draws a fourth toggle, **Music**, in both `2b` and `1f` — see Open
   Question 3.

7. **Sound effects is a global mute.** It is global for the whole game rather than
   per-theme, it is separate from the theme, and it mutes *any* theme.
   *Source: `Theming.md` → Sound Decisions → Global mute ("**Global for the whole game**,
   not per-theme"); `Menus and UI.md` → Decisions → Should there be a mute button, and
   where does it live? ("it mutes any theme").*
   *Testable:* with sound off, switch between Neon and Classic Red vs Blue and no sound
   plays under either.
   *Owner of the behavior:* `P2-02-audio.md` requirement 16. This PRD owns the switch.

8. **Vibrate on touch switches the haptic on and off.** With it on, the haptic fires on
   every valid click, including the first tap of a two-tap move; with it off, no haptic
   fires anywhere.
   *Source: `Menus and UI.md` → Settings Menu table ("Haptic feedback on tap. Fires on
   every *valid* click. On/off"); → Vibrate on Touch; `Game Board Design.md` → Haptic Rule
   ("Subject to the vibrate-on-touch setting being on").*
   *Owner of the behavior:* `P2-03-haptics.md` requirements 10–12. This PRD owns the switch.

9. **Animations off means the game does the thing instantly** — the mark simply appears,
   the quadrant is simply claimed. No animation, and no substitute effect, fade or
   transition standing in for one. The game stays fully playable and fully readable in this
   mode.
   *Source: `Animations.md` → Decisions → Animations off = instant state change; →
   Decisions → Turn animations off — a global setting.*
   *Testable:* with animations off, a confirmed move produces the new board state with no
   intermediate frames and no substitute effect.
   *Owner of the behavior:* `P2-04-animations.md` requirements 19–21, whose own requirement
   17 names this PRD as the owner of the switch. This PRD owns the switch.

10. **iOS Reduce Motion does not drive the Animations toggle.** There is exactly one
    control and the player owns it; Reduce Motion being on does not change what the game
    does.
    *Source: `Animations.md` → Decisions → Does iOS Reduce Motion drive the animations
    toggle? ("no lets leave this as a game setting for user to command").*
    *Testable:* with Reduce Motion on at the OS level and the Animations toggle on,
    animations still play.
    *Owner of the behavior:* `P2-04-animations.md` requirement 18, including the
    platform-flag half of that testable. This PRD owns the switch.

11. **All three are global, player-controlled and not theme-defined — a theme cannot
    override them.** No key in a theme file sets, forces or reads any of the three, and
    switching themes never changes their values.
    *Source: `Menus and UI.md` → Settings Menu ("All three are **global**,
    **player-controlled**, and **not theme-defined** — a theme can't override them");
    `Animations.md` → Decisions → Turn animations off ("it is **not theme-defined**");
    `Theming.md` → Sound Decisions → Global mute ("Muting is a player setting, not a theme
    property").*
    *Testable:* set the three toggles, switch the active theme, and all three values are
    unchanged; a theme file carrying keys with these names changes nothing.

12. **The two entry points edit the same values.** There is one global value per toggle —
    not a main-menu copy and an in-game copy.
    *Source: `Menus and UI.md` → Settings Menu ("All three are **global**"); → How you
    reach settings from gameplay.*
    *Testable:* change a toggle in-game, exit to the main menu, open Settings there, and it
    shows the changed value (and the reverse).

13. **All three are remembered between sessions, in whatever state they were left**, read
    back on launch through the persistence layer rather than any store of this feature's
    own.
    *Source: `Menus and UI.md` → Settings Menu ("All three are **remembered between
    sessions**"); → Persistence (table); `Theming.md` → Sound Decisions → Global mute
    ("**Remembered between sessions**"); `Tech Design.md` → Decisions → Persistence package.*

### What the toggles are, structurally

14. **Sound and Animations switch off a *theme channel*; Vibrate switches off an *app
    behavior* that is never theme-defined at all.** The three look alike in the UI, but
    only two of them correspond to something a theme defines. Concretely: the theme object
    has no haptic concept, and turning sound or animations off suppresses a theme-supplied
    channel without altering the active theme or its definition.
    *Source: `Theming.md` → What a Theme Does NOT Control ("Haptics are **not**
    theme-driven. Vibration lives at the **application setting level** ... two of them
    switch off a theme channel and one switches off an app behavior"); → What Is a Theme?
    (sound and animations are pillars of a theme).*
    *Testable:* the theme schema defines sound and animation values and defines nothing
    haptic; muting does not modify the loaded theme.

15. **Neither entry point offers theme selection or a theme change.** Theme selection lives
    on the main menu, and the theme cannot be changed mid-game.
    *Source: `Theming.md` → Decisions → Where theme selection lives ("Not buried in a
    settings screen"); → Decisions → Can you change the theme mid-game ("**No** — leave it
    out for now. Theme changes happen from the main menu only"); `Menus and UI.md` → Theme
    Selection.*
    *Testable:* no control on either surface changes the selected theme.
    `P2-01-navigation.md` requirement 14 and `P4-03-theme-selection.md` requirement 19 hold
    the same constraint from the routing and screen sides. Whether the surface may
    *display* the active theme read-only is a separate question — see Out of Scope.
    *Not disturbed by requirement 20:* hosting the slot-unlock purchase is not hosting theme
    selection. No theme is bought, browsed or applied from this surface.

16. **Both surfaces are theme-driven — no hardcoded colors, backgrounds, fonts or motion
    values**, and both pass the hardcoded-theme-value test. The slots they read are the
    **Settings card** and **Sheets** entries in `P1-03-theme-system.md` requirement 15,
    plus the button tier named in requirement 19.
    *Source: `Theming.md` → Architectural Rule ("No hardcoded colors, backgrounds, fonts,
    piece styles, sounds, or animations anywhere in the code"); `Menus and UI.md` → Main
    Menu ("The entire main menu is itself theme-driven ... No hardcoded styling here
    either"); `Tech Design.md` → Decisions → Do we add a test that fails on hardcoded theme
    values?*
    *Gap this opens:* `P1-03-theme-system.md` requirement 15 provisions no slot for a
    purchases section, a price row or a restore link. See Open Question 3.

### Text scaling

17. **This surface offers no text-size control of its own**, because Dynamic Type is not
    supported in this version.
    *Source: `Menus and UI.md` → Decisions → Do we support Dynamic Type? ("**Not for now.**
    *'Lets not do this as of yet.'*").*
    *Testable:* no control on either surface changes text size.
    *Not deliverable here:* the app-wide half of that decision — that the app does not
    scale its text to the iOS Dynamic Type setting — is **not this surface's to
    implement**, and an earlier draft of this requirement asserted it as though it were.
    Flutter's default behavior follows the OS text-scale factor, so "does not scale" needs
    a clamp at the app root. No PRD owns that. See Open Question 3.

### The surface's own controls

*Appended after requirement 17 rather than inserted above, so requirement numbers 1–17 stay
stable — `P1-03-theme-system.md`, `P2-01-navigation.md`, `P2-04-animations.md` and
`P4-03-theme-selection.md` all cite them. Requirements 20–22 are appended for the same
reason.*

18. **Each toggle row is labelled with its setting's name as the design doc names it** —
    *Sound effects*, *Vibrate on touch*, *Animations* — and the control on each row is the
    on/off switch of requirement 6.
    *Source: `Menus and UI.md` → Settings Menu (the three-toggle table naming each setting,
    and the mock drawing one labelled row per setting).*
    *Testable:* the surface renders exactly one row per setting, each carrying that
    setting's name.
    *Not settled — the sub-label.* `P1-03-theme-system.md` requirement 15 provisions a
    theme slot for *"the toggle row, its sub-label"*, citing this PRD's requirements 6 and
    16 — but no design doc asks for a sub-label. The explanatory second lines exist only in
    the handoff (`1f`/`2b`: "Buzzes, pops and splats", "A little buzz on every valid tap",
    "Marks pop, glow and jiggle"). This PRD does not specify sub-label copy; if that slot is
    to be filled, the copy needs a decision. See Open Question 3.

19. **Exit is presented as one item in the quick-actions list, labelled as leaving the game
    and going back to the main menu, and it is the control that triggers requirement 5.**
    `P2-01-navigation.md` → Out of Scope assigns the exit control's own presentation here;
    that PRD owns only the transition it invokes (its requirement 11).
    *Source: `Menus and UI.md` → How you reach settings from gameplay — quick actions is "a
    short list of things you can do mid-game", whose listed contents begin "Exit the game /
    back to main menu".*
    *Testable:* the in-game surface presents exactly one exit affordance, and activating it
    performs requirement 5.
    *Slot:* per requirement 16 its styling is theme-driven, reading the **secondary button
    tier** provisioned in `P1-03-theme-system.md` requirement 15 (*"Two button tiers, not
    one"*).
    *Not settled — emphasis.* Whether exiting warrants a **destructive** treatment is
    nowhere decided, and it cannot borrow one: `P1-03-theme-system.md` requirement 15
    scopes its destructive-action slot to *deleting an open game* (citing
    `P4-02-open-games-list.md` requirement 7). Leaving a game destroys nothing
    (requirement 5), which argues against it — but that is an inference, not a Decision.
    See Open Question 3.

### The purchases section

20. **The settings surface carries a purchases section, distinct from the toggles, holding
    two items: the $4.99 open-game-slot unlock, and a global *Restore purchases* control.**
    *Source: `Menus and UI.md` → Decisions → Where the open-game slot unlock is sold ("**The
    Settings screen.** The Settings screen gains a purchases section holding the $4.99
    open-game-slot unlock and a global **Restore purchases** control" — and, in the same
    Decision, "the Settings screen now carries more than the three toggles specified in
    **Settings Menu** above"); → Decisions → How many open games do we keep? ("**3 by
    default** ... a **$4.99 in-app purchase raises the cap to 100 open game slots**").*
    *Testable:* the main-menu surface presents a purchases section containing exactly these
    two items, distinct from the toggle rows.
    Scoped like requirement 6, because the two surfaces are not settled to be the same
    thing:
    - **The main-menu surface carries it.** The Decision names "the Settings screen", which
      is unambiguously the main-menu route.
    - **Whether it also appears in the in-game quick-actions surface is not settled** — see
      Open Question 6. This PRD does not decide it, and builds neither reading into the
      in-game surface.
    *Boundary:* this PRD owns the section, the two controls, and the fact that activating
    one invokes `P4-05-purchase-flow.md`'s API (its requirements 5 and 10). It owns nothing
    the controls then present — not the product, its type, the price display, the store
    query, the purchase sheet, or what restore does. `P4-05`'s own preamble anticipates
    exactly this arrangement: *"The winning host adds one control that invokes it and owns
    nothing else."*
    *Not a fourth setting:* see requirement 6's third bullet.

21. **The purchase control does not reach the purchase flow unless the parental gate has
    been passed.** The app is listed in Apple's Kids Category, which requires a parental
    gate before any purchase flow; the gate's scope is purchases only.
    *Source: `Tech Design.md` → Decisions → Kids category ("A **parental gate** is required
    before any purchase flow and before any link that leaves the app"; "**The parental
    gate's scope is purchases only.** The game has no outbound links today — no in-app
    support URL, no social links, no advertising").*
    *Testable:* activating the purchase control with the gate not passed does not invoke
    `P4-05`'s purchase API; the invocation happens only on the gate's success path.
    **Where the line is drawn** — the doc leaves this to a PRD (*"What the gate looks like
    and how it challenges is a PRD's job, not this doc's"*), so: this PRD requires **that**
    the gate precedes the purchase, because the trigger is this surface's. It does **not**
    design the challenge — what it asks, how it validates, how failure and retry behave —
    which belongs with everything else the trigger presents, in `P4-05-purchase-flow.md`.
    That is the same split as requirement 20 and the boundary block above, and it is the
    cleaner one: a gate designed here would be a second thing to keep in sync with the flow
    it guards.
    *Gap this names:* `P4-05-purchase-flow.md` has **no parental-gate requirement today** —
    its requirement 10 runs a purchase straight to a store outcome, and
    `P5-03-release-fastlane.md` had already flagged that nothing in the pipeline owns this.
    Requirement 21 pins the *ordering* to this surface; the challenge itself still has no
    owner. Routed, not fixed — see Open Question 3.
    *Restore is not gated:* the Decision names purchases as the trigger, and a restore makes
    no charge. No doc states that restore needs the gate, so nothing here requires it.

22. **The *Restore purchases* control is a compliance control, not the mechanism by which
    entitlements arrive.** It is present because Apple's review guidelines require it;
    activating it invokes `P4-05-purchase-flow.md`'s restore operation (its requirement 5),
    behind which is `AppStore.sync()`. Entitlements are authoritative from StoreKit's
    `Transaction.currentEntitlements` and repopulate on their own — signing in on a new
    device restores a non-consumable without the player ever touching this control.
    *Source: `Tech Design.md` → Decisions → Entitlements — Apple stores them, no backend
    needed ("Restore for non-consumables is largely automatic: signing in on a new device
    repopulates entitlements without the player doing anything. The visible **Restore
    purchases** control is still required by Apple's review guidelines, and
    `AppStore.sync()` is the explicit call behind it — so the control is a compliance
    requirement more than a functional one"); `Menus and UI.md` → Decisions → Where the
    open-game slot unlock is sold, which places the control here and calls it global.*
    *Testable:* the control is present and invokes the restore operation; **no
    entitlement-granting logic lives in this surface**; and a fresh install signed into the
    same Apple ID holds its entitlements with this control never having been tapped.
    *Why worded this way:* built as though it were the mechanism, this control becomes a
    step the player is expected to complete, and the "I paid and it's gone" path gets built
    around a button instead of around `currentEntitlements`.

## Out of Scope

- **Storing and restoring the four preferences**, including first-launch behavior on an
  empty store: `P1-04-persistence.md`.
- **The haptic mechanism, and what "vibrate off" means** — how the buzz is produced, how
  subtle it is, and the gating rule: `P2-03-haptics.md`.
- **Audio playback, and what "sound off" means** — the audio layer, the five sound moments
  and how muting is implemented: `P2-02-audio.md`.
- **The animations system, and what "animations off" means** — the vocabulary, where
  animations fire, durations, the one-at-a-time and don't-block-input rules, the
  instant-state-change path, and the Reduce Motion rule: `P2-04-animations.md`.
- **Everything the purchase and restore controls present** — the product definition and its
  type, price display and localization, the store query, the purchase sheet, offline and
  failure behavior, and what a restore does: `P4-05-purchase-flow.md`. This PRD hosts the
  entry points and owns nothing behind them.
- **The parental gate's challenge design** — what it asks, how it validates, retry and
  failure: `P4-05-purchase-flow.md`, per requirement 21. This PRD requires only that the
  gate precede the purchase.
- **What an entitlement is, how it is held, and what happens when one lapses**:
  `P1-07-entitlements.md`.
- **The open-games list's behavior at the cap**, including any upsell shown there and the
  delete action that frees a slot: `P4-02-open-games-list.md`.
- **The routing layer** — the two entry points as routes, whether a sheet is a route, and
  what the dismiss control is: `P2-01-navigation.md`. Requirement 19 covers the exit
  control's presentation only, which that PRD assigns here.
- **The main menu itself**, including the Settings button's own styling and placement:
  `P4-01-main-menu.md`.
- **The in-game settings button's placement in the scoreboard strip**:
  `P3-03-scoreboard-turn-indicator.md` requirement 12.
- **The pending move selection and the two-tap gesture**: `P3-02-move-input.md`. Whether
  opening this surface clears a pending selection is that PRD's open question, restated
  here as Open Question 5.
- **Theme selection and the theme system**: `P1-03-theme-system.md` and
  `P4-03-theme-selection.md` — and per requirement 15, theme selection is deliberately
  absent from both surfaces.
- **The read-only "Theme — Picked from the main menu" card — declined, not accepted.**
  `P4-03-theme-selection.md` → Out of Scope hands `2b`'s read-only theme display to this
  PRD. This PRD **does not specify one**, because no design doc names it: it exists only in
  the handoff, and `Menus and UI.md` → Settings Menu lists this surface's contents as three
  toggles. Requirement 6's "no fourth setting" is *not* the reason — a read-only display is
  not a setting, and requirement 15 forbids only *changing* the theme here. The effect is
  that the handoff's card currently has no owner, which is a visible gap rather than a
  silent one. See Open Question 3.
- **A Music toggle.** `Theming.md` → Sound Decisions → One-shot sound effects only, for now
  rules out background music in this version, and `Menus and UI.md` → Persistence lists
  four persisted preferences with no music among them. The handoff draws one anyway — see
  Open Question 3.
- **A confirmation prompt on exit.** Unsettled — see Open Question 2. Nothing here designs
  one, and nothing here rules one out.
- **What else quick actions might eventually hold.** The doc says "contents (so far)"; this
  PRD builds the listed contents and nothing more.

## Open Questions

### 1. Is quick actions the same screen as the main menu's settings, or a trimmed-down version?

As worded in `Menus and UI.md` → How you reach settings from gameplay:

> Undecided: whether quick actions is the *same* settings screen as the main menu's, or a
> trimmed-down in-game version with the exit option added.

The handoff draws them as two different things — `2b — Settings page (from the main menu)`
is a full screen and `1f — Modal: in-game settings / quick actions` is a bottom sheet, with
`2b`'s own text saying "1f stays the trimmed in-game version with the exit action." That is
*an* answer, but it is the handoff's, and no Decision in the docs takes it. It also decides
requirement 6's second bullet — whether the Animations toggle appears in quick actions —
and it now feeds Open Question 6. Also carried by `P2-01-navigation.md` → Open Question 7.

### 2. Does leaving a game still need a confirmation prompt?

As worded in `Menus and UI.md` → Leaving a game mid-play:

> Whether leaving still needs a confirmation prompt is undecided; the original reason for
> one ("Leave game? Your score will be lost") no longer applies.

Also carried by `P2-01-navigation.md` → Open Question 6.

### 3. Gaps found while writing this PRD (flagged by the PRD author, not asked by the docs)

Each of these is something an implementer of this surface would otherwise have to guess.
None is resolved here.

- **The handoff draws four toggles, the docs settle three.** `1f` and `2b` both include a
  **Music** row (drawn `off` in `1f`), but `Theming.md` → Sound Decisions → One-shot sound
  effects only, for now says there is no background music in this version, and
  `Menus and UI.md` → Persistence lists exactly four persisted preferences with no music
  key. Requirement 6 follows the docs. Same conflict already flagged by
  `P1-04-persistence.md` and `P2-02-audio.md`.
- **First-launch defaults for the three toggles.** The docs settle that all three are
  remembered between sessions, but no Decision says what they read as before anything has
  been written. The mock in `Menus and UI.md` → Settings Menu draws all three as `[ON]`,
  which is a drawing, not a decision.
- **When a toggle change takes effect.** "Global" and "player-controlled" are settled;
  whether flipping a toggle applies to the running game the moment it is flipped, or only
  on the next launch, is not stated anywhere. The in-game entry point only makes sense
  under the first reading, but that is inference, not a Decision. Note `P2-03-haptics.md`
  requirement 12 states the mid-game-change rule for haptics specifically; nothing states
  it for sound or animations.
- **How the in-game surface is dismissed back to the game.** Requirement 2 settles that
  getting to settings does not abandon the game, but no doc names the control that returns
  you to it. The handoff gives `1f` a close button and a "Back to the game" action; the
  docs give it neither. Also carried by `P2-01-navigation.md` → Open Question 9.
- **Toggle sub-label copy** (requirement 18). `P1-03-theme-system.md` requirement 15
  provisions a theme slot for a sub-label, citing this PRD — but no design doc asks for
  one, and the copy exists only in the handoff. Either the copy gets decided or that slot
  goes unused.
- **Whether the exit control is a destructive action** (requirement 19). No slot covers it;
  `P1-03-theme-system.md`'s destructive-action styling is scoped to deleting an open game.
- **No theme slot exists for the purchases section** (requirements 16 and 20).
  `P1-03-theme-system.md` requirement 15 provisions a **Settings card** — card fill,
  border, radius, the toggle row, its sub-label, and the switch's track and knob — and
  nothing for a purchases section, a price row, or a restore link. Requirement 16 forbids
  hardcoding, so as the two PRDs stand this section cannot be styled. That PRD's slot list
  is explicitly "not closed" and is derived from what screens consume, so this is a slot to
  add rather than a contradiction — but nobody has added it, and this PRD may not.
- **`P4-05-purchase-flow.md` has no parental-gate requirement** (requirement 21). Its
  requirement 10 runs a purchase straight to a store outcome. `Tech Design.md` → Decisions
  → Kids category now settles that the gate is required before any purchase flow, and
  `P5-03-release-fastlane.md` had already flagged that no PRD owns it. Requirement 21 pins
  the ordering to this surface; the challenge itself remains unowned.
- **`P4-05-purchase-flow.md`'s host question is now closed, and its preamble is stale.** It
  is written around "Only *which screen hosts the entry point*" being open, listing the
  settings screen as one candidate among several. `Menus and UI.md` → Decisions → Where the
  open-game slot unlock is sold now answers it. The screen-agnostic API design still holds
  and nothing needs rebuilding — but that PRD's framing should be updated so nobody reads
  the question as live.
- **The read-only Theme card has no owner.** `P4-03-theme-selection.md` hands `2b`'s
  "Theme — Picked from the main menu" display to this PRD, which declines it above for want
  of any doc naming it. If it is wanted, it needs a Decision and a theme slot; if it is
  not, `P4-03`'s Out of Scope should stop pointing here.
- **Dynamic Type has no owner at the app level** (requirement 17). `Menus and UI.md` →
  Decisions settles that the app does not scale its text, but delivering that means a clamp
  at the app root, and no PRD delivers it — several restate the negative and none owns it.
  `P1-01-app-scaffold.md` is the plausible home; it does not claim it today.
- **`P2-04-animations.md` requirement 17 states where the animations toggle lives** — that
  it "sits alongside the sound-effects and vibrate toggles in the Settings menu" — which is
  requirement 6's territory, not that PRD's. It is the exact mirror of the location claim
  already removed from `P2-02-audio.md`. Flagged for the coordinator; not fixed here, since
  this PRD may not edit another.
- **`P2-01-navigation.md` → Open Question 11 is stale.** It records this PRD and
  `P3-02-move-input.md` as *disagreeing about the status* of the pending-selection
  question, quoting a testable from requirement 2 that no longer exists. See Open
  Question 5.
- **`Menus and UI.md` → Open Questions reads stale.** Its first entry — "Future menu items
  to consider later: Rules/How to Play, Settings, vs. AI, Online" — lists Settings as a
  future item, while the same doc's Main Menu section and Decisions treat the Settings
  button as settled, and now give that screen a purchases section too. Worth a doc pass;
  not this PRD's to fix.

### 4. Where does the switch end and the behavior begin? (raised by the renumbering pass)

The dependency block above now says this PRD owns the switch UI and the three channel PRDs
own what "off" means — a correction, because both sides previously claimed the behavior.
Requirements 7–10 still *describe* that behavior, because a switch cannot be specified
without saying what it switches, and each now names its owner. If an implementer finds the
two descriptions disagreeing, the channel PRD wins. Nobody has drawn the line more
precisely than that. Requirements 20–22 follow the same rule with `P4-05-purchase-flow.md`.

### 5. Does opening this surface clear a pending move selection?

As worded in `P3-02-move-input.md` → OQ-1:

> whether opening the in-game settings / quick-actions modal (`1f`) clears a pending
> selection or leaves it standing when the modal is dismissed.

No design doc addresses it. An earlier draft of requirement 2 asserted as a testable that
the pending selection is preserved; that assertion has been removed, because it decided a
question the owning PRD holds open.

**Four PRDs touch this, and they do not agree.** An earlier revision of this section
claimed they did; that claim was wrong and is withdrawn.

- **`P3-02-move-input.md` → OQ-1** holds it open. It is the owner.
- **`P3-05-how-to-play.md` requirement 15 answers it by implication, in the opposite
  direction, and with a testable:** *"a tap landing on the hint or the legend is a tap
  outside the grid, and therefore clears any pending selection, **exactly as a tap on any
  other non-board area does**."* `P3-03-scoreboard-turn-indicator.md` requirement 12 puts
  the settings button at the top right of the game screen alongside the scoreboard — a
  non-board area. So an implementer building `P3-05` requirement 15 as written clears the
  pending selection when the settings button is tapped, having settled this question
  without ever reading it. The generality of that rule, not its author's intent, is the
  risk.
- **`P2-01-navigation.md` → Open Question 11** records the two PRDs as disagreeing about
  the *status* of the question, quoting requirement 2's since-removed testable. Its wording
  is stale, and it is not evidence of agreement in either direction.
- **This PRD** takes no side, per requirement 2.

Nothing settles it. It needs a decision, and until there is one, `P3-05` requirement 15's
"any other non-board area" is the wording most likely to decide it by accident.

### 6. Does the purchases section appear in quick actions, or only on the main-menu surface?

`Menus and UI.md` → Decisions → Where the open-game slot unlock is sold names "**The
Settings screen**" and says the placement "keeps one parental gate in one place." It does
not say whether the in-game quick-actions surface *is* that screen or a different one —
which is Open Question 1 again. If quick actions turns out to be the same screen, the
purchases section arrives mid-game by default, without anyone having chosen that.

**Omission does not settle it.** The quick-actions list in `Menus and UI.md` is headed
"Quick actions contents (**so far**)", and this PRD relies on that non-exhaustiveness
elsewhere — Out of Scope's last bullet reads the same "(so far)" as leaving the list open.
Treating the absence of a purchases entry as a decision would be reading one document's
silence two different ways in one PRD. So it is raised, not decided.

*Author's observation, not a requirement and not a Decision:* a purchase prompt behind a
parental gate is an odd thing to meet in the middle of someone else's turn, and
main-menu-only is the narrower reading. Recorded so the tradeoff is visible when this is
answered.
