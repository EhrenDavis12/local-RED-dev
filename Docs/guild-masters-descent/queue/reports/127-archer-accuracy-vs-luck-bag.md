# What the Archer's accuracy raise does under the Luck bag

> **Status:** Research for queue item #127, 2026-11-17. One decision for the user; nothing
> here is settled until they answer. Sources are the docs' owner's originals (`Combat.md`,
> `Individual Types.md`), EhrensDocs, and the combat engine on `queue/build` in
> `src/guildmasters-descent`.

## The conflict

`Individual Types.md`, The Archer: "Hitting the same target twice running also raises the
Archer's accuracy and its damage — a continuous percentage increase that caps at 10%. A
miss resets the streak."

`Combat.md`, Luck Checks (17 Nov): "Evasion draws from that same bag: when a member is
attacked, it pulls one token, and a True means the attack misses. That's where a member's
evasion comes from, and it needs no chance of its own — it's the bag's own density of
Trues."

A miss is now a drawn token, not a roll against a percentage, so there is no percentage
left for the Archer to take points off. The damage half of the raise is untouched; only
the accuracy half has lost its meaning. Both passages are the owner's; neither doc is
edited here.

## What the code does today

`ArcherType.cs:38-43` sets the raise to `(hits − 1) × 2%`, capped at 10, from the second
hit in a row, and passes it as `MissChanceReduction`. `Battle.cs:613-614` takes it in
points off the target's miss chance, which is still 2% per Luck capped at 50%. The Luck-bag
row (#129) replaces that miss chance with a token pull, and has to know what to do with
`MissChanceReduction` when it does.

## How much accuracy is worth under the bag

A target's evasion is its bag's share of Trues: 1 in 50 (2%) at Luck 5, 4 in 50 (8%) at
Luck 20, 7 (14%) at Luck 60, 10 (20%) at Luck 180, never reaching 25%. Under the old rule an
F-rank target at Luck 5 had a 10% miss chance and a capped streak erased it. Under the bag
the same target dodges 2% of shots, so at F rank there is almost nothing for accuracy to
raise; it only becomes felt deep into the game.

## The options

**A. Damage only.** The streak raises the Archer's damage up to 10%, and nothing about
whether a shot lands. The target's bag alone decides a miss, and a miss still resets the
streak. In the game: identical to today at F rank, where misses are already rare. The
code drops one field. **Recommended** — it is the only option that keeps Combat's "needs
no chance of its own", and it costs nothing visible now.

**B. A second chance against a True.** When a streak shot pulls a True from the target,
the Archer rolls its raise (2% up to 10%) to hit anyway. In the game: a dodge
occasionally fails against a hot Archer. It brings back a plain percentage roll beside the
bag, which is what the bag was written to replace, and the target's lucky token is spent
even when it didn't save them.

**C. A capped streak can't be dodged.** Once the raise reaches its cap, the Archer's shot
pulls no token — like Volley. In the game: a long streak becomes a sure hit, and the
target's bag keeps its token for a reset. It turns "continuous percentage" into a single
step, so it rewrites the owner's sentence more than A does.

A fourth way — thinning the target's Trues for one pull — doesn't fit a fixed bag of 50
and isn't offered.

All three are cheap to change later: one rule in the Archer's attack and one tuning line,
no save data.

## What else this touches

EhrensDocs `Individual Types.md` proposes "Accuracy is raised in points off the target's
chance to miss" and carries the open question "Is the Archer's streak raise measured in
points off the miss chance, or a share of it". Under A that question goes away; under B or
C it changes shape. The answer reaches EhrensDocs through the tidy pipeline.

## Open Questions

- When the Archer hits the same enemy twice in a row, its later shots already get up to
  10% more damage. Now that a dodge is a lucky draw from the target's bag rather than a
  percentage, should the streak (A) only raise damage, (B) also give each streak shot a
  2–10% chance to hit anyway when the target draws a dodge, or (C) make the shot impossible
  to dodge once the streak reaches its cap?
