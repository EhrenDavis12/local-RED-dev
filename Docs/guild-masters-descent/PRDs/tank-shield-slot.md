# PRD: The Tank's Swappable Shield Slot

> **Status:** Draft · Source docs read: Equipment.md, Combat.md, Individual Types.md, Guild
> Members.md, Specialists.md, Core Concept.md, The Dungeon.md, and in EhrensDocs/ the change
> notes against each of those plus Look and Feel.md and Platform.md. A change note that
> revises a passage of an original is what gets built. The one exception: where the other dev
> has edited the original after our change note and the two now disagree, the original wins
> (user, 2026-11-12, in the queue Focus: "the main documents win we need to convert any
> changes that those main documents decided over what we had in the EhrenDocs"). No
> requirement below rests on such a case. Items marked **build default** are the user's
> open questions that this build answers with a cheap-to-change choice; they are not settled
> design and stay listed under Open Questions.

## Problem

The docs give the Tank a shield (the Brute "push[es] the Tank's shield aside", the special
is Shields Up), and the user has decided it is gear: more than one shield, equipped, taken
off and swapped. In the game today a shield is nothing. There is no slot for one, the shop
doesn't sell one, and it adds nothing to a fight.

## Goal

A Tank has a third gear slot, for a shield. The guild buys shields at the shop, hands them to
Tanks in the Dorms, swaps them, repairs them and sells them back, the way it does weapons and
armour. In battle a working shield adds a rolled defence on top of the Tank's armour, wears
down with every hit the Tank takes, and adds nothing once broken. The Tank's art stays as it
is. Every save made before this change still loads, with no shields anywhere.

## Requirements

### The shields

1. There are four shields, one for each of the four round shield pictures. Each is a separate
   item with its own name, its own picture and its own shop entry, and all four are class F.
   *(EhrensDocs/Equipment.md, "The Tank carries a shield, and shields can be swapped": "there
   is more than one shield"; EhrensDocs/Look and Feel.md, Icons: "shields S1 to S4", and "the
   shields for the Tank's shields".)* Where the pictures come from is open. See Open
   Questions.
2. **Build default:** only the Tank can carry a shield. A shield can't go in any slot of any
   other combat type or of a specialist. *(EhrensDocs/Equipment.md, "Questions on shields and
   potions", Why.)*
3. A shield is neither a weapon nor armour. It never fits a weapon or armour slot, and the
   Tank's armour slot still holds full armour only. *(EhrensDocs/Equipment.md, "The Tank
   carries a shield…": "as well as its weapon and its armour".)*
4. **Build default:** a shield is built like armour. It has a class, a Defence range and a
   Durability, each rolled once when the piece is made and fixed after that. Each shield has
   its own Defence band and Durability band. The Defence band doubles with each class above F
   (both ends double). The Durability band is the same at every class. The range is rolled
   the way armour's is: its span is anywhere from a single figure to four points wide, never
   wider than the band, at every class, and the range sits anywhere inside the band that span
   allows. The Durability is a whole number drawn from the band, and a new piece starts at
   full. *(Equipment.md, Quality; EhrensDocs/Equipment.md, "For now a span is no wider at SSS
   than at F".)*
5. Every shield figure is a placeholder kept in Tuning: each F-class Defence band, each
   Durability band and each shop price. Each one shows up on the game's placeholder list with
   the other placeholders. *(EhrensDocs/Equipment.md, "The Tank carries a shield…": "How much
   defence a shield adds and how much durability it has are placeholders", Why: "kept in the
   game's tuning file with the others".)*

### The Dorms

6. A Tank's sheet in the Dorms has a shield slot beside the weapon and armour slots. The
   player can equip a shield from the stores, which swaps out any shield already in the slot,
   can unequip it back to the stores, and can repair it. The slot gives the same refusals the
   other slots give. Equipping is refused for an unknown member or piece, for a member away on
   a mission, for a member who isn't a Tank, and for a shield another member holds, and a
   refusal changes nothing. A shield the Tank already holds equips as no change. Unequipping
   changes nothing while the holder is away on a mission. Other combat types
   and specialists get no shield slot. *(EhrensDocs/Equipment.md, "The Tank carries a
   shield…"; Equipment.md, Assignment; EhrensDocs/Core Concept.md, "Missions are in the first
   version, as F-rank jobs that pay gold".)*
7. The shield slot shows the shield's name, class and condition, like the other slots. It
   never shows the rolled range or the durability. *(EhrensDocs/Equipment.md, "The Dorms shows
   none of a piece's numbers".)*
8. Equipping, swapping, unequipping or breaking a shield changes nothing about how the Tank is
   drawn. The Tank always shows the shield it is drawn with, even with no shield equipped.
   *(EhrensDocs/Look and Feel.md, Characters and animations, "Gear and the art".)*

### The shop

9. The shop sells each of the four shields at class F, at its own placeholder price. It buys
   them back at the same sell share as other gear, and it refuses to buy a shield that a Tank
   is holding. A shield's shop tile shows only its picture and price, and its name appears in
   the detail panel. *(EhrensDocs/Equipment.md, "Gear can be sold back to the shop", "For now
   the shop sells class F only"; EhrensDocs/Look and Feel.md, "Readable text and spacing".)*

### In battle

10. A Tank's defence on each strike is its Constitution, plus its working armour's roll, plus
    its working shield's roll, plus any Shields Up bonus it holds. The shield's Defence range
    is rolled afresh for each strike, the same way armour's is. *(EhrensDocs/Equipment.md, "The
    Tank carries a shield…": "adds defence on top of the Tank's armour"; Equipment.md,
    Quality, last paragraphs.)*
    - **Order within one strike:** the hit roll, then the attacker's weapon roll, then the
      armour roll, then the shield roll. A roll that doesn't apply is skipped and not drawn: no
      hit roll for an area strike, no weapon roll for a broken or empty weapon slot, no armour
      roll for broken or empty armour, and no shield roll for a broken or empty shield slot.
      On a miss, nothing after the hit roll is drawn. *(Extends the order the engine already
      draws in, hit, weapon, defence; see requirement 15.)*
    - **A strike that ignores defence** draws no armour roll and no shield roll, and its
      defence is zero. Wear still follows requirement 13: armour spends a use on such a strike
      today (`Battle.cs:637-645` rolls nothing but still wears the armour), so the shield does
      too. No attack in the game ignores defence yet.
    - **A Mage field hit** on a Tank standing in the field rolls the shield along with the
      armour, armour first, and the field uses two-thirds of that defence (requirement 12). It
      wears neither: a field hit spends no use of the armour today (`Battle.cs:451-457`), and
      it spends none of the shield's.
11. A broken shield, or an empty slot, adds nothing. If the armour has broken and the shield
    still works, defence is Constitution plus the shield. If both have broken, defence is
    Constitution alone. *(EhrensDocs/Equipment.md, "A broken shield adds nothing, and a working
    one outlasts broken armour".)*
12. The shield counts as part of the Tank's defence everywhere defence is used. An area attack
    uses two-thirds of it, the Mage's field uses it, and the Tank's advantage over the Fighter
    doubles it. **Build default:** the Brute's advantage halves all of the Tank's defence,
    shield included. *(Guild Members.md, Base Stats; Individual Types.md, The Tank, The Brute;
    EhrensDocs/Guild Members.md, "The Mage's field is an area attack, for now".)*
13. **Build default:** the shield spends one use every time the Tank is hit, in exactly the
    cases where the Tank's armour spends one. Spelled out: one use for each strike that lands
    on the Tank, whoever makes it. That covers ordinary attacks and specials, single strikes
    and area strikes, strikes that ignore defence, and strikes that defence reduces to
    nothing. A miss spends nothing, and so does a Mage field hit (requirement 10). Shields Up
    spends nothing from the shield. The use is spent after the strike's damage is worked out,
    so the strike that spends the last use still gets the shield's full roll. Durability never
    goes below zero, and at zero the shield is broken. A shield can break partway through a
    multi-strike attack, and the later strikes then face the Tank's defence without it. *(Equipment.md, Durability;
    EhrensDocs/Equipment.md, "A hit that does nothing still wears gear".)*
14. Shields Up works as it does now. **Build default:** it works with or without a shield. The
    allies behind the Tank get the Shields Up increase only and never any of the shield's
    defence. *(EhrensDocs/Individual Types.md, "The Tank's taunt, Shields Up and bonus, for
    now": "what the allies get is the increase … not the Tank's whole defence".)*
15. A battle where no one wears a working shield draws exactly the same rolls, in the same
    order, as it did before this change. A shield's roll is drawn only when a working shield is
    worn. This is what lets a battle saved before this change carry on exactly when it is
    resumed. *(EhrensDocs/Platform.md, Saving: "the rest of a battle … plays out exactly as it
    would have"; EhrensDocs/Combat.md, "The clock, how a fight opens, and who goes first, for
    now".)*
16. Monsters carry no shield, monster Tanks included. *(EhrensDocs/The Dungeon.md, "The
    dungeon's enemies are monsters": "there's no weapon or armour in either".)*

### Repair and the dive

17. A shield is repaired in the guild hall for gold only, broken or not, at the same price
    rule as any other piece. That rule is one flat price for the piece's condition: Good but
    below full, Worn, Ragged, or Broken. Each price is the existing repair placeholder in
    Tuning, and the shield gets no prices of its own. A shield at full durability can't be
    repaired and costs nothing. A repair restores the shield to full durability and is refused,
    changing nothing, when the guild's gold is short. A held shield stays with its holder, and a
    stored one can be repaired too. *(EhrensDocs/Equipment.md, "For now repair costs gold only", and
    "The Tank carries a shield…": "it's repaired the way a weapon or armour is".)*
18. When a dive ends, a dead Tank's shield goes back to the stores and nobody holds it. If a
    battle leaves no one in the party alive, the shields the party took in are lost along with
    the rest of its gear. *(EhrensDocs/Equipment.md, "A dead member's gear comes home, for
    now".)*

### Saving

19. The save holds every shield in the stores, including its current durability, and each
    Tank's shield slot. *(EhrensDocs/Platform.md, Saving.)*
20. A save made before this change loads with every shield slot empty and no shields in the
    stores, and this is not reported as a repair. That goes for a save taken mid-dive or
    mid-battle too: it loads, and per requirement 15 it carries on exactly. *(EhrensDocs/
    Platform.md, Saving: "A save made by an older version still loads".)*
21. Some saves hold a shield where it can't be, and these are fixed as they load: the slot is
    emptied, the piece goes back to the stores, the load reports the fix, and the save loads.
    The cases are:
    - a shield slot holding something that isn't a shield, or a piece that isn't in the stores
    - a shield slot on any member who isn't a Tank
    - a weapon or armour slot holding a shield
    - one shield claimed by two slots, in which case it stays with the member hired first

    *(EhrensDocs/Platform.md, Saving, "For now", third item.)*
22. The save format version goes up with this change, so a game from before it reports a save
    holding shields as made by a newer version. It must never load that save and quietly drop
    the shields. *(EhrensDocs/Platform.md, Saving: "one made by a newer version of the game, is
    reported as such and left on the phone as it is".)*

## Out of Scope

- **Repairing a shield in the field.** The build default is that the Armourer repairs shields
  on a dive. The game has no Armourer and no field repair yet (the Armourer unlocks at guild
  rank D, and no guild rises above F), so nothing here is built for it. Whoever builds field
  repair applies that default.
- Shields arriving with a recruit, in the demo party, or as loot. A dive yields only gold for
  now *(EhrensDocs/Equipment.md, "For now a dive yields only gold")*. Recruits are an open
  question below.
- Shields above class F in the shop *(EhrensDocs/Equipment.md, "For now the shop sells class F
  only")*.
- Any change to the Tank's art, and any sign on the battle screen that a shield has broken.
- Repairs that cost materials.

## Open Questions

From the design docs, as worded there *(EhrensDocs/Equipment.md, "Questions on shields and
potions")*:

- Can a type other than the Tank carry a shield? *(Build default: no. Requirement 2.)*
- When a Tank has no shield equipped, can it still use Shields Up? *(Build default: yes.
  Requirement 14.)*

From EhrensDocs/Individual Types.md, "Questions on Vanish, taunts and the field". A shield
raises the stakes on this one, because the Tank's whole defence now includes it:

- "It also adds that defence to all the allies behind him" — is that the Shields Up increase,
  or the Tank's whole defence?

The user's open questions on this feature. The build uses the defaults shown. None of these
is in the change notes' question list yet:

- What wears a Tank's shield down — every time the Tank is hit, the same as armour; only when
  the Tank uses Shields Up; or both? *(Build default: every hit, and Shields Up costs nothing
  extra. Requirement 13.)*
- Do shields come in quality classes with rolled numbers, the way weapons and armour do, or is
  every shield the same apart from its picture? *(Build default: classes and rolled numbers.
  Requirement 4.)*
- When a Brute hits the Tank, should it halve the Tank's whole defence, armour and shield
  together, or ignore the shield's part completely and leave the armour's part whole? *(Build
  default: halve the whole. Requirement 12.)*
- On a dive, who fixes a Tank's shield in the field — the Armourer, the Blacksmith, or nobody,
  so shields are only repaired back at the guild hall? *(Build default: the Armourer. Out of
  Scope.)*

Raised by the PRD author. These are not in any doc. Each comes with a proposal, which is mine
and not the user's:

- The game now ships only one shield picture. The other three round shields were taken out of
  the game's icon set, although Look and Feel says the game carries the shields. Where do the
  other three pictures come from? *Proposal: until that's answered, all four shields wear the
  one shield picture the game ships, and the three missing pictures go on the missing-art
  list.*
- Should the four shields differ from each other in defence, durability or price, or only in
  picture? *Proposal: each gets its own placeholder entries (requirement 5), all four starting
  at the same figures.*
- What are the four shields called? *Proposal: plain placeholder names, written without "#"
  or the middle dot, which the font lacks.*
- Can a Tank recruit arrive already carrying a shield, the way recruits can arrive with a
  weapon or armour? *Proposal: not in this build (Out of Scope).*
