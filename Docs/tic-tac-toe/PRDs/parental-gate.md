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
entering a number — the doc's example is *"Enter the answer: seven times eight."* Source:
[Tech Design](../Tech%20Design.md) → In-App Purchases and Entitlements → The parental gate —
a word problem, every time.

**R2.** The operands are rendered as words, never as digits, anywhere in the problem text.
This is the load-bearing part rather than a presentation choice: digits are solvable by a
child who can count, while the word form defeats pre-readers and early readers alike. Source:
same section.

**R3.** A problem is generated afresh every time the gate is raised. Nothing caches or
reuses the previous one. Source: same section (*"The problem is randomised each time the gate
is raised"*).

**R4.** The generator is a pure Dart unit with no Flutter import, and it takes its source of
randomness as a parameter so a seeded source pins the problem exactly in a test. The problem
it returns carries both its worded text and its correct numeric answer, so nothing re-derives
the answer by parsing words. Source: [Tech Design](../Tech%20Design.md) → Project Structure
(layer-first; `engine/` and `online/` are pure Dart, and their purity is held by an import
scan), and the tests-before-code order, which requires a test to assert an exact problem and
its exact answer.

### Attempts, passing and dismissal

**R5.** An attempt is one submitted answer. A submitted answer that is not the correct number
is a wrong attempt. The answer is entered as a number, so the entry takes digits only and
nothing is submittable until at least one digit has been entered. Source: R1's *"answered
with a number"*.

**R6.** A correct answer on any attempt passes the gate, and the guarded action runs. Source:
[Tech Design](../Tech%20Design.md) → In-App Purchases and Entitlements → The parental gate
(*"A pass is good for one purchase"*).

**R7.** Three wrong attempts dismiss the gate and the guarded action never runs — for a
purchase, *"without ever reaching the store"*; for online entry, without entering online
play. Source: same section.

**R8.** Each raise starts clean: a new problem (R3) and the attempt count back to zero.
Nothing in the docs imposes a cooldown after three wrong attempts, so a dismissed gate may be
raised again immediately, and that raise gets its own three attempts. Source: same section
(*"randomised each time the gate is raised"*, and *"the next purchase raises the gate
again"*).

### What a pass is worth

**R9.** A pass authorises exactly the one action the gate was raised for, and nothing after
it. Source: same section (*"A pass is good for one purchase and nothing else. There is no
remembered pass — the next purchase raises the gate again, immediately after a passed one
included"*).

**R10.** The gate publishes no pass value that any caller can hold, store, inspect or pass
along, and no entry point accepts an assurance that a gate was passed somewhere else. The
only way to get past the gate is to hand it the action. Source: same section (*"Moving the
challenge out to the caller and passing an assurance inward would weaken the guarantee from
enforced to conventionally observed, which is the whole thing the gate exists for"*).

**R11.** Nothing about a pass is persisted, and no notion of "session" is defined anywhere in
this feature — not cold launch, not foreground return, not dismissing a surface. Source: same
section.

**R12.** Restore purchases is never gated. Source: same section (*"Restore is not gated.
Restore spends no money."*).

### The service and its provider

**R13.** One gate service, reached through a Riverpod provider and by no other means — no
singleton and no global instance — declared as a plain `Notifier`/`NotifierProvider` or
`Provider` without Riverpod codegen. Source: [Tech Design](../Tech%20Design.md) → State
Management; the provider-as-injection-point reasoning in → Navigation → The layer is reached
through a provider; and the existing `gameCenterSessionProvider` and `appNavigatorProvider`
shapes in the code.

**R14.** The gate is its own layer folder under `lib/`, not a file inside `purchase/`, since
purchases and online entry both call it and neither owns it. The pure generator (R4) lives
there with it. Source: [Tech Design](../Tech%20Design.md) → Project Structure (one folder per
layer; *"File names inside each are not this doc's to decide"*) and → Kids Category (the gate
has two callers).

### Guarding a purchase

**R15.** `guardPurchase` takes the action to perform and runs it only after a pass. It
returns nothing a caller can branch on to learn whether the player passed. Source:
[Tech Design](../Tech%20Design.md) → In-App Purchases and Entitlements → The parental gate
(*"The gate is enforced at the purchase itself, not by whatever raises it"*), plus R10.

**R16.** The call site is the purchase layer's own initiate-a-purchase path — the function
that starts a StoreKit purchase wraps itself in the gate. The Settings screen's purchases
section, and any locked theme row that gains a price action later, call that function and
implement no gate of their own. Source: same section, plus
[Menus and UI](../Menus%20and%20UI.md) → Settings Menu → Purchases (*"it keeps one parental
gate in one place"*) and → Theme Selection (*"Nothing on this overlay is buyable, and no
purchase or restore control lives here"*).

**R17.** The gate is raised before a purchase is initiated, and is not raised again when a
purchase that ended `pending` later resolves. A parent approving out of band, minutes or days
later, reaches the player without a second challenge. Source: same section (*"No purchase can
be initiated without passing it"*) and → Buying ends one of four ways, and one of them ends
later.

### Guarding entry to online play

**R18.** `guardOnlineEntry` takes the current Game Center session and the action, and decides
from the session value it is handed. It never authenticates on the caller's behalf and sends
no platform call. Source: [Tech Design](../Tech%20Design.md) → Online Play (*"Game Center
sign-in happens when the player first enters online play"* — so the session is already known
by the time this is called) and → The channel contract (*"Neither the matchmaker nor a match
load signs the player in on the caller's behalf"*), which is the established shape for this
layer.

**R19.** On a `GameCenterRestricted` session the gate is not raised and the action does not
run. Apple has said multiplayer is not allowed for that account, so there is nothing to
enter. Source: [Tech Design](../Tech%20Design.md) → Online Play (*"When Apple reports
multiplayer is not allowed for the account, online play is not offered"*). This is the narrow
reading of "not offered" — see Open Questions.

**R20.** On every other session, the gate is raised **only** when the session reports the
account is a child's (`isUnderage`, carried on `GameCenterAuthenticated`). An adult account
is never gated on the way into a match, and an unauthenticated or in-flight session raises
nothing either — Apple has reported no child account, and the app imposes no restriction
Apple has not. When the gate is not raised, the action runs immediately with nothing on
screen. Source: [Tech Design](../Tech%20Design.md) → Kids Category (*"Entering online play
raises it only when Apple reports the signed-in account is a child's —
`GKLocalPlayer.isUnderage` — so an adult account is never gated on the way into a match"*) and
→ Online Play (*"it never imposes a restriction Apple has not"*).

**R21.** The call sites are the deliberate entry steps only: tapping **Play online** to find
or invite an opponent, and accepting an invitation. Opening an online game that already
exists — from the open-games list, or from a "your turn" notification — is playing rather
than entering, and never calls the gate. Source:
[Tech Design](../Tech%20Design.md) → Kids Category.

### The surface

**R22.** The gate's surface reaches the screen only through the navigation layer, as a route
declared as a child of whatever raised it, so that surface stays mounted and visible beneath
it. Nothing outside the navigation layer puts it on screen. Source:
[Tech Design](../Tech%20Design.md) → Navigation → Nothing outside the layer puts a surface on
screen, and → Surfaces that stay on top of something are nested.

**R23.** The surface performs the guarded action itself; the navigation layer never learns
what the player answered. The pending action is held by the gate service (R13) and read from
there by the surface. Source: [Tech Design](../Tech%20Design.md) → Navigation → No operation
reports an outcome back (*"the surface acts on the state itself"*) — the same shape
`DeleteGameConfirmationOverlay` already uses for its own Yes.

**R24.** The gate can be abandoned without answering. Abandoning runs nothing, spends no
attempt, and leaves no pass. Source: the app's standing convention that a surface can always
be left without acting — [Menus and UI](../Menus%20and%20UI.md) → Theme Selection (*"The
overlay can also be closed without changing anything"*) and → Deleting an open game (*"On no
exit the modal"*). No design doc states it of the gate specifically; the control's wording is
an Open Question below.

### The double

**R25.** A fake gate ships as app code behind the same interface, drivable to pass, to run
out of attempts, and to stay open, so every caller's tests exercise a guarded path without
driving the real surface. It holds no shortcut the real one could not honour — in particular
it reports no pass as a value (R10). Source: the established precedent for this kind of
double in [Tech Design](../Tech%20Design.md) → Online Play (*"A fake bridge ships as app code
rather than test code… behind the same interface, because it is the double every other layer
tests against"*).

## Out of Scope

- **The purchase flow itself** — StoreKit, the plugin, prices, the four purchase endings,
  Restore, and the Settings purchases section. This feature defines the API that flow calls
  (R15, R16) and nothing else.
- **Entitlement state** and the open-game cap reading from it.
- **The "Play online" button, Apple's matchmaker, and accepting an invitation.** This feature
  defines the API those call (R18–R21). Where "Play online" lives on the main menu is an open
  question in [Menus and UI](../Menus%20and%20UI.md) and is not settled here.
- **What a restricted account is shown** in place of online play — the *"calm, kid-facing
  message"* of [Tech Design](../Tech%20Design.md) → Online Play belongs to the entry point,
  not to the gate.
- **Outbound links.** The game has none today, so the gate ships with two callers. A link
  added later needs the gate ([Tech Design](../Tech%20Design.md) → Kids Category).
- **The age-rating questionnaire, the privacy policy, and anything else on the Kids Category
  submission checklist.**

## Open Questions

- **What is the arithmetic, exactly?** The docs give one example — *"seven times eight"* —
  and settle only that it is arithmetic, worded, and answered with a number. Nothing states
  the operations or the operand range, and a test written before the code has to assert an
  exact problem. Concrete options: (a) multiplication only, both operands single digits, as
  the example reads; (b) multiplication only, operands up to twelve; (c) a mix of
  multiplication and addition. Each needs a word list covering its range.
- **What does the gate say?** No design doc and no approved handoff screen writes the gate's
  copy — the prompt line, whether it frames itself as a question for a grown-up, the entry's
  label, what is said when three attempts run out, or the label on the way out (R24). The
  handoff draws no gate at all, the same gap [Theming](../Theming.md) notes for the settings
  purchases section.
- **Does one pass cover one entry into online play?** *"A pass is good for one purchase and
  nothing else"* settles purchases and says nothing about online entry. The user's own
  earlier question — *"How often is the grown-up maths question asked for online play — every
  new online game, only the first time ever, or once per app open?"* — was answered with
  *"Ask the grown-up question to enter multiplayer — but only when it has to be asked: skip
  it when no parental controls apply"*, which settles **who** is asked and not **how often**.
  R9 currently reads it the same way as a purchase: every deliberate entry raises it.
- **Is R19 the intended reading for a restricted account?** [Online Play](../Tech%20Design.md)
  says online play is not offered at all to that account, so R19 has the guard refuse without
  raising the gate. The alternative is to treat restricted exactly like any other session and
  gate on `isUnderage` — which only matters if an entry point is ever reachable on a
  restricted account, which the same section says it is not.
