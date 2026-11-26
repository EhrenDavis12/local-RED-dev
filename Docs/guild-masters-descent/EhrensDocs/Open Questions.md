# Open Questions — for the design docs' owner

> **Status:** Questions the build is waiting on, asked 2026-11-17, 2026-11-19, 2026-11-20 and 2026-11-25, for the design docs' owner to answer. Write an answer under each question; "going ahead with" means the game already does that, so answer only if you want it different.

## How to answer

Reply under each question, or by number (e.g. "1: 110, 3: A"). Skip any you want to leave.

## Open Questions

### Loot and carrying

Capacity is counted in slots: every member carries 5, and a healing potion, a buff potion or an item of loot takes 1 slot each.

3. **A dead member's gear.** When a member dies in the dungeon, how does their gear get
   home? Going ahead with B, one slot a piece. (Fairly easy to change.)
   - A: It always comes home, free.
   - B: Each piece takes up a slot, and it comes home only if the party has a slot free
     for it.
   - C: Only a Porter can bring it home.

   **Answer:**

4. **Gold and slots.** Going ahead with: gold takes no slots, so the party brings out all
   the gold it keeps, however many came along. Fine, or should gold take slots too, say
   so many coins a slot? (Cheap to change.)

   **Answer:**

5. **Repairing gear.** The current reading is that repair costs gold, for now. Is that
   right? (Cheap to change.)

   **Answer:**

9. **Loot.** Going ahead with: when a party clears a floor, each enemy on it has a
   one-in-four chance to drop something — half the time a healing potion like the
   shop's, otherwise one ore or one herb. Fine, or should an item of loot be something
   other than a healing potion? (Cheap to change.)

   **Answer:**

### Health

10. **Cook and Porter health.** Health comes from Constitution alone (Constitution times
    10), for fighters, Cooks and Porters alike. A Cook's or Porter's tier doesn't change
    it. Going ahead with that. Fine, or should their tier raise their health? (Cheap to
    change.)

    **Answer:**

11. **Promotion.** Promotion, say from F rank to E rank, doesn't change a member's health
    directly. Health is Constitution times 10, so it only rises if their Constitution
    does. Going ahead with that. Fine? (Cheap to change.)

    **Answer:**

12. **Practice runs.** Practice runs can hurt but never kill. If a member hits 0 health on
    one, do they come home injured, or just sit out the rest of that run? (Moderate to
    change.)

    **Answer:**

13. **Injury from dives.** Right now a member comes back from a dive either fine or dead,
    and injuries only come from missions and practice. Should a dive ever leave someone
    injured, for example ending it on low health? (Moderate to change.)

    **Answer:**

14. **Medicine.** Missions gather herbs for medicine. Is medicine only for healing
    injuries faster back at the guild, and never used during a dive? (Cheap to change.)

    **Answer:**

### Battle

15. **Experience split.** After a battle, does the experience get shared among everyone who
    started it, or only the members still standing? Going ahead with: only those standing.
    (Easy to change.)

    **Answer:**

16. **Special bar refilling.** After a special is used, its bar empties. Going ahead
    with: no, the special's own hits don't refill it; only ordinary attacks do. Fine?
    (Easy to change.)

    **Answer:**

### Guild rank

The docs say the guild moves up (F → E → … → SSS) by passing a promotion test — a one-off
mission on the mission board that appears "when the guild is close to promotion" — and
that a higher rank raises how many missions run at once and the roster size. None of this
is built yet; the build waits on these.

20. **When the promotion test appears.** Nothing says what "close to promotion" means.
    A placeholder number goes with whichever you pick. (Moderate to change later.)
    - A: Once a set number of missions or battles have been won at the current rank.
    - B: Once some members have reached the next rank themselves (e.g. one member
      promoted to E).
    - C: Once the guild has earned a set amount of gold in total.
    - D: It is always on the board, one test per rank.

    **Answer:**

21. **What a promotion test is.** How is it passed? (Moderate to change later — it
    decides the test screen and what is saved.)
    - A: A mission like the others — pick members, it runs on a timer and succeeds or
      fails the way missions do, ranked one grade above the guild, so lower-rank members
      on it can die.
    - B: A special dungeon run or battle the party has to win.
    - C: Something else.

    **Answer:**

22. **Failing the promotion test.** If the guild fails it, what happens? Members come
    home injured either way, as on any failed mission. (Cheap to change.)
    - A: It stays on the board and can be tried again straight away.
    - B: It disappears and comes back after a wait.
    - C: It disappears until the guild is "close to promotion" again.

    **Answer:**

23. **What each rank raises.** How many missions can run at once, and how big can the
    roster be, at each rank? Numbers get placeholders until answered. (Cheap to change.)

    **Answer:**

24. **The shop at E rank.** What does the shop sell once the guild is E rank? The
    equipment doc gives prices only for F-class gear. (Cheap to change.)
    - A: Keep selling F-class gear until E-class gear gets prices.
    - B: The shop is empty of gear.
    - C: E-class gear at placeholder prices.

    **Answer:**

### Finding dungeons

The docs say dungeons are found through the mission board — a small chance on an
ordinary mission (claimed outright), and a rank-up reveals one with a claim mission that
"requires a big group" and stays on the board if it fails; only dungeons at or below the
guild's rank. Not built yet; waits on these and on guild rank.

25. **How big a "big group" is.** How big is a "big group" for a claim mission? And is a
    claim mission a timed mission like the others that succeeds or fails, or a battle the
    group plays? (Moderate to change later.)
    - A: A fixed number, e.g. at least 5.
    - B: More than a normal mission allows.
    - C: Something else.

    **Answer:**

26. **Finding on a failed mission.** Can an ordinary mission find a dungeon only when it
    succeeds, or on a failed mission too? (Cheap to change.)

    **Answer:**

27. **The bottom floor of a found dungeon.** A found dungeon's depth is random. The
    starting dungeon ends on a rest area, but a random depth can end mid-way (e.g. 13
    floors, last rest area at floor 10). When the party clears the bottom floor:
    (Moderate to change later — a dungeon already made keeps its depth.)
    - A: The dive ends and the party goes home with everything it carries, as at a rest
      area.
    - B: The bottom floor is always a rest area — depth is a multiple of 5.
    - C: The bottom floor is a boss floor, then home.

    **Answer:**

29. **Buying a dungeon.** Can a dungeon ever be bought? The docs only describe finding
    and claiming them. Going ahead with: no buying. (Cheap to change.)

    **Answer:**

### Buff potions

The five buff potions — Wind Step, Dragon's Vein, Rock Skin, Ancient Gift and God's Wish —
are in the game. The player uses one from the battle screen and it helps the whole party
for the rest of that fight.

30. **Buffs at the shop.** Buffs come from the Alchemist, who isn't in the game yet.
    Going ahead with: the shop sells all five from the start, 30 gold each and God's Wish
    40, and every one raises its stat by a fixed 3 (God's Wish turns 2 Falses into
    Trues). Fine? (Cheap to change.)

    **Answer:**

31. **Where a buff reaches.** Going ahead with: a buff's raise counts everywhere the
    fight uses that stat — the support ring's help, which of two attacks on the same tick
    goes first, and the Tank's Shields Up included. Rock Skin still never adds health.
    Fine? (Cheap to change.)

    **Answer:**

32. **God's Wish's Trues.** After God's Wish a member's bag holds its own Trues and up to
    2 extra ones. Going ahead with: when a True is drawn, an extra one is used up first, so
    the member's own Trues are kept for later fights. Or should it be either one at
    random? (Cheap to change.)

    **Answer:**

33. **Whose buff gets used.** When several members carry the buff being used, going ahead
    with: it comes from whoever was picked first for the party. That decides whose slot is
    free for loot at the end of the dive. Fine? (Cheap to change.)

    **Answer:**

34. **Auto and buffs.** Going ahead with: Auto never uses a buff; only the player does.
    Should Auto use them too, and when? (Cheap to change.)

    **Answer:**

### Dungeon gold and fees

A cleared floor pays a count drawn from its enemy count less two up to its enemy count,
1 gold each in an F-rank dungeon and doubling each rank. Re-entering at a rest area costs
the entry fee again plus a teleport fee of "1 gold a floor in an F-rank dungeon, rising 1
a rank". The game pays and charges this way, with these readings where the docs don't
say.

35. **A floor with one or two enemies.** "Enemy count less two" goes below zero when a
    floor has fewer than two enemies, and a floor can be one battle against one strong
    enemy. Going ahead with: the count never starts below 0, so one enemy pays 0 or 1
    gold and two pay 0 to 2. Fine, or should every fighting floor pay at least 1? (Cheap
    to change.)

    **Answer:**

36. **The odds of the count.** Going ahead with: every count in the range is as likely as
    any other, so a floor of fifteen enemies at F pays 13, 14 or 15 gold at even odds.
    Fine? (Cheap to change.)

    **Answer:**

37. **Clearing the same floor again.** When a later dive clears a floor that was cleared
    before, going ahead with: its gold is drawn again, the same as its loot. Or should a
    floor's gold be fixed when the dungeon is made, as its monsters are? (Moderate to
    change — a fixed figure would be saved with the dungeon.)

    **Answer:**

38. **What rises in the teleport fee.** Going ahead with: the gold a floor rises 1 a rank
    — 1 at F, 2 at E, up to 9 at SSS — so re-entering an E-rank dungeon at floor 5 costs
    10 gold on top of the entry fee. Or does the whole fee rise 1 a rank, so the same
    re-entry costs 6? (Cheap to change.)

    **Answer:**

39. **Which floor the teleport fee counts.** Going ahead with: the rest area's own floor,
    so re-entering at the floor-5 rest area counts 5 floors. Or should it count the floor
    the party's first battle is on, 6? (Cheap to change.)

    **Answer:**

### Gear finds

A weapon or a piece of armour drops on the last fighting floor before each rest area and
on the dungeon's last floor, and the party carries it home in a slot, the way it carries
loot. The game drops and carries it this way, with these readings where the docs don't
say.

40. **How many pieces.** Going ahead with: one piece on each of those floors, however
    deep. Or should deeper floors drop more? (Cheap to change.)

    **Answer:**

41. **Weapon or armour.** Going ahead with: a weapon or an armour piece at even odds,
    and never a shield. Fine? (Cheap to change.)

    **Answer:**

42. **Whose kind.** A piece is the weapon or armour of one combat type. Going ahead
    with: any of the six types, at even odds. Or should it be the type of one of the
    floor's own monsters, or of someone in the party, so it's gear the party can use?
    (Cheap to change.)

    **Answer:**

43. **Its class.** Going ahead with: the dungeon's own rank, with a deeper floor giving a
    better piece inside that class, the same way a monster's gear gets better deeper
    down. Or should a deep enough floor drop a higher class? (Cheap to change.)

    **Answer:**

44. **No room.** Going ahead with: a full party can't throw anything away to make room,
    so a piece that doesn't fit is lost. Fine, or should the player be able to drop
    something for it? (Moderate to change — throwing away needs its own step at the end
    of a dive.)

    **Answer:**

45. **What comes home first.** At the end of a dive the free slots go to a fallen
    member's gear first. Going ahead with: then the pieces found, the deepest first,
    then the loot. Or should loot come before found pieces, or the pieces come in the
    order they were found? (Cheap to change.)

    **Answer:**

46. **Clearing the same floor again.** Going ahead with: a floor cleared again on a
    later dive drops a piece again, the same as its gold and loot. Or should each floor
    drop a piece only once a dungeon, so it can't be farmed? (Moderate to change — the
    dungeon would have to remember which floors have dropped.)

    **Answer:**
