# Goal

> **What this is:** Where the project is headed right now, in your words — "get to MVP",
> "ship to the App Store". The queue's proposal engine reads this and works out what stands
> between here and there.
> **Yours.** Edit freely. Rewrite it when the goal changes; don't append a new one below.
> **Hints:** One goal at a time. List what the goal does *not* include under "Not included" —
> that list is what keeps a rejected proposal from coming back.

---

**Ship Tic-Tac-Toe-Extreme to the App Store, then start game two.**

This is game one of ten. The BHAG is ten games in a year with two developers and Claude
Code, so the point of this game is to finish it, learn what shipping actually takes, and
move on. Done beats perfect: the bar below is the whole bar, and anything past it belongs
to a later game or a later update.

The game is done when all of these are true:

- **It flows.** Every screen leads somewhere sensible and back again — main menu, new
  game, open games, the board, in-game settings, game over, rematch, theme select,
  settings, about. Nothing dead-ends and nothing dangles.
- **It plays well and it's fun.** Two people can play a full pass-and-play session — pick
  it up, understand the sending rule from the board alone, finish a game, rematch, come
  back to an open game later — without confusion or a rule that misfires.
- **It doesn't crash.** Crash reporting is wired in, and playtesting a full session on a
  phone and an iPad turns up no crash and no lost game.
- **It looks good and clean.** The Neon theme ships polished to the handoff, marks and
  animations feel finished, nothing is placeholder, and it holds together on a small
  phone and on an iPad.
- **It has a purchase.** At least one paid theme (Sewing) buys through the App Store
  behind the parental gate, restore works, and a refund takes it away again.
- **It's deployed.** A public App Store release through fastlane, with the listing, the
  privacy answers, and every submission blocker in the tech design resolved.

Order of attack: whatever unblocks deployment first. Purchases and the store listing have
the longest human lead times, so they should start early even though they land last.

## Not included

- Online play, multiplayer over a network, or any backend
- An AI opponent or single-player mode
- Android, web, or desktop builds
- New themes beyond the three in the catalog, or new theme features
- Game two's design — nothing about the next game lives in this project
- Localization beyond one locale
