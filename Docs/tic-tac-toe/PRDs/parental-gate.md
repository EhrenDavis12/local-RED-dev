# PRD: Parental Gate

> **Status:** Draft · Source docs read: [Tech Design](../Tech%20Design.md) (In-App Purchases
> and Entitlements, Kids Category, Online Play, Navigation, State Management, Project
> Structure, Testing), [Menus and UI](../Menus%20and%20UI.md) (Settings Menu → Purchases,
> Theme Selection, Main Menu, Navigation and the Back Stack),
> [Theming](../Theming.md) (Free and Paid Themes; the note that the purchases section has no
> approved screen), [Game Overview](../Game%20Overview.md) (Target Audience, Modes),
> [Rules](../Rules.md), [Game Board Design](../Game%20Board%20Design.md),
> [Animations](../Animations.md), [Alternative Game Styles](../Alternative%20Game%20Styles.md)
> (parking lot — nothing sourced from it).
>
> Existing code read for the seams this plugs into: `lib/gamecenter/`, `lib/state/`,
> `lib/navigation/`, `lib/ui/menus/`. `lib/purchase/` and `lib/entitlements/` do not exist
> yet.

## Problem

The app is going into Apple's Kids Category, which requires a grown-up check before any
purchase and — on a child's account — before entering online play
([Tech Design](../Tech%20Design.md) → Kids Category). Nothing in the app asks that question
today. The two things that need it are about to be built: the purchase flow, and the
"Play online" entry point. Built without a gate to call, each would grow its own — which is
the failure the docs name directly: *"the surfaces hosting the purchase controls implement
no gate of their own"* ([Tech Design](../Tech%20Design.md) → In-App Purchases and
Entitlements → The parental gate — a word problem, every time).

## Goal

One gate exists, callable by anything that must not be triggered by a child, and it is the
only thing that can authorise the action behind it. A purchase cannot be initiated without
passing it; a child's account cannot enter online play without passing it; an adult account
never sees it on the way into a match; and a pass authorises exactly one action and leaves
nothing behind. The purchase layer and the "Play online" button — neither of which exists
yet — call it without either of them being built or changed first.

## Requirements

### The challenge

**R1.** The gate challenges with a single arithmetic problem stated in words and answered by
entering a number — the doc's example is *"Enter the answer: seven times eight."* The problem
is **a multiplication of two whole numbers from 2 to 9**, so the smallest answer is 4 and the
largest 81. Source: [Tech Design](../Tech%20Design.md) → In-App Purchases and Entitlements →
The parental gate — a word problem, every time; the operation and the 2-to-9 range are the
user's call, 2026-09-15.

**R2.** The operands are rendered as words, never as digits, anywhere in the problem text.
This is the load-bearing part rather than a presentation choice: digits are solvable by a
child who can count, while the word form defeats pre-readers and early readers alike. Source:
same section.

**R3.** One problem per raise, and it is fixed for all three attempts — a wrong answer does
not swap the question out from under the person answering it. The next raise generates a
fresh one. Source: same section (*"The problem is randomised each time the gate is raised"*);
that it holds still across the three attempts is the user's call, 2026-09-15.

**R4.** The generator is a pure Dart unit with no Flutter import, and it takes its source of
randomness as a parameter so a seeded source pins the problem exactly in a test. The problem
it returns carries both its worded text and its correct numeric answer, so nothing re-derives
the answer by parsing words. Source: [Tech Design](../Tech%20Design.md) → Project Structure
(layer-first; `engine/` and `online/` are pure Dart, and their purity is held by an import
scan), and the tests-before-code order, which requires a test to assert an exact problem and
its exact answer.

**R5.** Consecutive raises never show the same problem: the problem a raise generates is never
the one the previous raise showed. The two operands are interchangeable for this test —
*"seven times eight"* and *"eight times seven"* are the same problem. Source: the user's call,
2026-09-15.

### Attempts, passing and dismissal

**R6.** An attempt is one submitted answer. A submitted answer that is not the correct number
is a wrong attempt. The answer is entered as a number, so the field takes digits only, caps at
two digits — R1's largest answer is 81 — and nothing is submittable until at least one digit
has been entered. Source: R1's *"answered with a number"*; the two-digit cap is the user's
call, 2026-09-15.

**R7.** A correct answer on any attempt passes the gate, and the guarded action runs. Source:
[Tech Design](../Tech%20Design.md) → In-App Purchases and Entitlements → The parental gate
(*"A pass is good for one purchase"*).

**R8.** Three wrong attempts dismiss the gate and the guarded action never runs — for a
purchase, *"without ever reaching the store"*; for online entry, without entering online
play. The guard answers `failedAttempts` (R15). Source: same section.

**R9.** Each raise starts clean: a new problem (R3) and the attempt count back to zero.
Nothing in the docs imposes a cooldown after three wrong attempts, so a dismissed gate may be
raised again immediately, and that raise gets its own three attempts. Source: same section
(*"randomised each time the gate is raised"*, and *"the next purchase raises the gate
again"*).

### What a pass is worth

**R10.** A pass authorises exactly the one action the gate was raised for, and nothing after
it. One pass covers **one purchase**, or **one entry into online play** — one deliberate
start, invite or accept (R26) — and nothing is cached across either. Source: same section
(*"A pass is good for one purchase and nothing else. There is no remembered pass — the next
purchase raises the gate again, immediately after a passed one included"*); that online entry
is worth exactly one pass the same way is the user's call, 2026-09-15.

**R11.** The gate publishes no pass value that any caller can hold, store or present back to
it, and no entry point accepts an assurance that a gate was passed somewhere else. The only
way to get past the gate is to hand it the action. The outcome a guard returns (R15) is a
report of what already happened, not an authorisation: nothing accepts it as an argument, and
holding one gets a caller nothing. Source: same section (*"Moving the
challenge out to the caller and passing an assurance inward would weaken the guarantee from
enforced to conventionally observed, which is the whole thing the gate exists for"*).

**R12.** Nothing about a pass is persisted, and no notion of "session" is defined anywhere in
this feature — not cold launch, not foreground return, not dismissing a surface. Source: same
section.

**R13.** Restore purchases is never gated. Source: same section (*"Restore is not gated.
Restore spends no money."*).

### The service, its provider, and what a guard answers

**R14.** The gate is an abstract `ParentalGate` — the interface every caller depends on —
reached through a `Provider<ParentalGate>` and by no other means: no singleton, no global
instance, no Riverpod codegen. A test substitutes `FakeParentalGate` (R32) by overriding that
provider. The real implementation holds its pending state internally; nothing outside it can
read or set what is pending. This mirrors `GameCenterBridge` and `gameCenterBridgeProvider`
exactly. Source: [Tech Design](../Tech%20Design.md) → State Management; the
provider-as-injection-point reasoning in → Navigation → The layer is reached through a
provider; and the existing `gameCenterBridgeProvider` / `FakeGameCenterBridge` shape in the
code. Confirmed by the user, 2026-09-15.

**R15.** A guarded action is a `Future<void> Function()`, and a guard answers
`Future<GateOutcome>` — a sealed value with exactly six cases:

| Outcome | Means |
|---|---|
| `ran` | The action ran, either after a pass or because no gate was owed |
| `refused` | The guard refused without asking; the action did not run (R24) |
| `notSignedIn` | No resolved Game Center session to decide from; the action did not run (R25) |
| `busy` | A raise was already pending; nothing happened (R16) |
| `abandoned` | The gate was left without answering; the action did not run (R18) |
| `failedAttempts` | Three wrong attempts; the action did not run (R8) |

The returned future completes when the gate closes — after the action has run, for `ran` —
and completes immediately for the outcomes that put nothing on screen. Six distinct values
rather than one flag or a failure carrying a message, for the reason the Game Center bridge
gives for its own: a caller that cannot tell a refusal from a cancel cannot behave
differently on them. Source: [Tech Design](../Tech%20Design.md) → Online Play → The channel
contract (*"Each is a distinct value the caller can branch on rather than one failure carrying
a message"*); the six cases are the user's call, 2026-09-15.

**R16.** A raise while one is already pending answers `busy` and does nothing at all: no
second surface, no second problem, and the pending action is never replaced. Source: the
user's call, 2026-09-15; the same shape as the bridge refusing a second matchmaker
presentation ([Tech Design](../Tech%20Design.md) → Online Play).

**R17.** The pending action is consumed before it is run, in one step, so a second submit
arriving while the first is still resolving runs nothing — the action runs exactly once per
raise. The surface closes once the action's future completes. If the action throws, the
pending action has already been cleared, the gate still closes, and the error propagates to
the guard's caller through the returned future rather than being swallowed. Source: the
user's call, 2026-09-15.

**R18.** Abandoning the gate — the way-out control, a tap on the scrim, or the platform
back-swipe — drops the pending action, runs nothing, spends no attempt, and answers
`abandoned`. The surface's disposal calls the service's abandon, so a gate swiped away by the
platform rather than closed by a control cannot leave a stale action pending behind it.
Source: the user's call, 2026-09-15. The failure this closes is the one
[Tech Design](../Tech%20Design.md) → Navigation records for the back-swipe generally:
*"Neither scan sees a gesture… the hole it closes is the absence of a call."*

**R19.** The gate is its own layer folder under `lib/`, not a file inside `purchase/`, since
purchases and online entry both call it and neither owns it. The pure generator (R4) lives
there with it. Source: [Tech Design](../Tech%20Design.md) → Project Structure (one folder per
layer; *"File names inside each are not this doc's to decide"*) and → Kids Category (the gate
has two callers).

### Guarding a purchase

**R20.** `guardPurchase` takes the action to perform and runs it only after a pass, answering
`ran` when it does and the matching outcome when it does not (R15). Source:
[Tech Design](../Tech%20Design.md) → In-App Purchases and Entitlements → The parental gate
(*"The gate is enforced at the purchase itself, not by whatever raises it"*), plus R11.

**R21.** The call site is the purchase layer's own initiate-a-purchase path — the function
that starts a StoreKit purchase wraps itself in the gate. The Settings screen's purchases
section, and any locked theme row that gains a price action later, call that function and
implement no gate of their own. Source: same section, plus
[Menus and UI](../Menus%20and%20UI.md) → Settings Menu → Purchases (*"it keeps one parental
gate in one place"*) and → Theme Selection (*"Nothing on this overlay is buyable, and no
purchase or restore control lives here"*).

**R22.** The gate is raised before a purchase is initiated, and is not raised again when a
purchase that ended `pending` later resolves. A parent approving out of band, minutes or days
later, reaches the player without a second challenge. Source: same section (*"No purchase can
be initiated without passing it"*) and → Buying ends one of four ways, and one of them ends
later.

### Guarding entry to online play

**R23.** `guardOnlineEntry` takes an **already-resolved** `GameCenterSession` and the action.
Authenticating is the entry point's job and happens first — that is the "Play online" item's
work, not this one's — and the guard is called with whatever session that produced. The guard
itself never authenticates, holds no bridge, and sends no platform call. The action it guards
is therefore the post-sign-in half of entering: presenting Apple's matchmaker, or accepting
the invitation. Source: [Tech Design](../Tech%20Design.md) → Online Play (*"Game Center
sign-in happens when the player first enters online play"*) and → The channel contract
(*"Neither the matchmaker nor a match load signs the player in on the caller's behalf"*),
which is the established shape for this layer; the split is the user's call, 2026-09-15.

**R24.** On a `GameCenterRestricted` session the guard refuses without asking: nothing is put
on screen, the action does not run, and the outcome is `refused`. Apple has said multiplayer
is not allowed for that account, so there is nothing to enter, and `isUnderage` — which that
state also carries — is never consulted, because the refusal comes first. Source:
[Tech Design](../Tech%20Design.md) → Online Play (*"When Apple reports multiplayer is not
allowed for the account, online play is not offered"*), confirmed as the intended reading by
the user, 2026-09-15.

**R25.** The other three session states resolve like this:

| Session | What happens | Outcome |
|---|---|---|
| `GameCenterAuthenticated`, `isUnderage` true | The gate is raised | per the answer: `ran`, `failedAttempts`, `abandoned` |
| `GameCenterAuthenticated`, `isUnderage` false | The action runs immediately, nothing on screen | `ran` |
| `GameCenterUnauthenticated` or `GameCenterAuthenticating` | Nothing on screen, the action does not run; the caller must authenticate first and call again | `notSignedIn` |

An adult account is never gated on the way into a match, and the gate never stands in for
sign-in. Source: [Tech Design](../Tech%20Design.md) → Kids Category (*"Entering online play
raises it only when Apple reports the signed-in account is a child's —
`GKLocalPlayer.isUnderage` — so an adult account is never gated on the way into a match"*) and
→ Online Play (*"it never imposes a restriction Apple has not"*); the `notSignedIn` answer is
the user's call, 2026-09-15.

**R26.** The call sites are the deliberate entry steps only: tapping **Play online** to find
or invite an opponent, and accepting an invitation. Opening an online game that already
exists — from the open-games list, or from a "your turn" notification — is playing rather
than entering, and never calls the gate. Source:
[Tech Design](../Tech%20Design.md) → Kids Category.

### The surface

**R27.** The gate's surface reaches the screen only through the navigation layer, as a
**top-level route pushed over whatever is currently on screen** rather than a child of any
one parent — the gate is raised from the main menu, from Settings, and from wherever the
purchase flow later lives, so it can have no single parent, and pushing leaves what raised it
mounted and visible beneath. It is pushed, never `go`-ed, so nothing is replaced and the
player lands back where they were. Source: [Tech Design](../Tech%20Design.md) → Navigation →
Nothing outside the layer puts a surface on screen, and → Surfaces that stay on top of
something are nested; the top-level-push shape is the user's call, 2026-09-15.

**R28.** The navigation layer gains a second small interface alongside `GameLaunchNavigator`,
reached through its own provider — show the gate, dismiss the gate, and nothing else — and the
gate service depends on it through that provider. `AppNavigator`'s fixed operations are not
touched, for the same reason `GameLaunchNavigator` was kept off them. A recording fake
implementing this interface is what a test asserts the gate was shown through. Source:
[Tech Design](../Tech%20Design.md) → Navigation → The layer is reached through a provider
(*"under a singleton… 'this screen invoked that navigation exactly once' could not be asserted
at all"*), and the existing `GameLaunchNavigator` precedent in `lib/navigation/`; the user's
call, 2026-09-15.

**R29.** The surface reports its outcome to the **gate service**, never back through the
navigator — no navigation operation reports an outcome, so the answer cannot travel that way.
The service holds the pending action (R14), runs it on a pass (R17), and dismisses the surface
through R28's interface. Source: [Tech Design](../Tech%20Design.md) → Navigation → No
operation reports an outcome back (*"the surface acts on the state itself"*) — the same shape
`DeleteGameConfirmationOverlay` already uses for its own Yes.

**R30.** On the third wrong answer the surface stops asking: it shows the out-of-attempts line
and the way-out control alone — no problem, no answer field, no submit — and closes when that
control is tapped, answering `failedAttempts` (R8). Source: the user's call, 2026-09-15.

**R31.** The screen carries six things, each under a named widget key so a test can find it:
a prompt addressed to a grown-up, the worded problem (R1, R2), a numeric answer field (R6), a
submit, the out-of-attempts line (R30), and the way out (R18). **Tests pin that structure —
each element present or absent, the submit enabled or not, the attempt counting — and never
the wording.** The wording is the screen's own, chosen when it is built and checked by running
the app. Source: the user's call, 2026-09-15; the six elements follow R1, R2, R6, R18 and R30.

### The double

**R32.** `FakeParentalGate` ships as app code behind the same `ParentalGate` interface (R14),
drivable to every outcome R15 names, so every caller's tests exercise a guarded path without
driving the real surface. It holds no shortcut the real one could not honour — in particular
it reports no pass as a value (R11). Source: the established precedent for this kind of
double in [Tech Design](../Tech%20Design.md) → Online Play (*"A fake bridge ships as app code
rather than test code… behind the same interface, because it is the double every other layer
tests against"*).

## Out of Scope

- **The purchase flow itself** — StoreKit, the plugin, prices, the four purchase endings,
  Restore, and the Settings purchases section. This feature defines the API that flow calls
  (R20, R21) and nothing else.
- **Entitlement state** and the open-game cap reading from it.
- **The "Play online" button, Apple's matchmaker, and accepting an invitation** — including
  the Game Center sign-in that has to happen before the guard is called (R23). This feature
  defines the API those call (R23–R26). Where "Play online" lives on the main menu is an open
  question in [Menus and UI](../Menus%20and%20UI.md) and is not settled here.
- **What a restricted account is shown** in place of online play — the *"calm, kid-facing
  message"* of [Tech Design](../Tech%20Design.md) → Online Play belongs to the entry point,
  not to the gate.
- **Outbound links.** The game has none today, so the gate ships with two callers. A link
  added later needs the gate ([Tech Design](../Tech%20Design.md) → Kids Category).
- **The age-rating questionnaire, the privacy policy, and anything else on the Kids Category
  submission checklist.**

## Open Questions

- **No design doc describes the gate's surface.** [Menus and UI](../Menus%20and%20UI.md)
  lists no gate among its screens, and the approved handoff draws none — the same gap
  [Theming](../Theming.md) records for the settings purchases section. R27 and R31 settle
  where it sits and what it carries for the purpose of building it; where the gate belongs
  among the app's screens, and the wording it ends up with, are a design-doc question rather
  than this PRD's.
