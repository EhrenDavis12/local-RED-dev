# Open Questions — for the design docs' owner

> **Status:** Questions the build is waiting on, asked 2026-11-17, for the design docs' owner to answer. Write an answer under each question; "going ahead with" means the game already does that, so answer only if you want it different.

## How to answer

Reply under each question, or by number (e.g. "1: 110, 3: A"). Skip any you want to leave.

## Open Questions

### Loot and carrying gold

Each member can carry 10 gold out of the dungeon. A Porter can carry 100.

1. **Porter's gold.** Does a Porter carry 100 in total, or 100 on top of the normal 10, so
   110? (Cheap to change.)

   **Answer:**

2. **Herbalist and Miner.** They carry a bit more than a normal member but less than a
   Porter. How much gold each? For example 20. (Cheap to change.)

   **Answer:**

3. **A dead member's gear.** When a member dies in the dungeon, how does their gear get
   home? (Fairly easy to change.)
   - A: It always comes home, free.
   - B: Each piece takes up space, say 5 gold's worth, so you leave gold behind to carry
     it.
   - C: Only a Porter can bring it home.

   **Answer:**

4. **Too much gold.** When a floor drops more gold than the party can carry, is the extra
   lost straight away? Or does the party keep it all in the dungeon and only leave the
   extra behind when it walks out? (Cheap to change.)

   **Answer:**

5. **Repairing gear.** The current reading is that repair costs gold, for now. Is that
   right? (Cheap to change.)

   **Answer:**

### Enemies

6. **Enemy strength.** Monsters have no gear. How are their attack and defence worked out?
   - A: From their level alone, so they get stronger automatically deeper down.
   - B: Each monster has its own hand-set attack and defence, and level drives only things
     like speed.

   **Answer:**

7. **Enemy types.** For now monsters can only use the Archer's animations. (Cheap to
   change.)
   - A: Every early monster is an Archer type. Simpler, but every fight looks the same.
   - B: Monsters can be any of the six fighter types, all playing Archer animations. This
     tests type advantages from day one.

   **Answer:**

8. **Enemy health.** Going ahead with: a monster has the same health as a member of the
   same level. Fine? (Cheap to change.)

   **Answer:**

9. **Enemy gear and loot.** The newer docs have monsters wearing gear and dives dropping
   gear. Going ahead with: keep it simple, so no monster gear and gold-only loot in the
   first version. Fine? (Easy to add later.)

   **Answer:**

### Health

10. **Cook and Porter health.** Fighters get more health at higher ranks. Cooks and
    Porters climb their own nine tiers instead. Should their health go up with tier, or
    stay at 10? (Cheap to change.)

    **Answer:**

11. **Promotion.** When a member is promoted, say from F rank to E rank, does their health
    rise to match an E-rank hire? Or does only a fresh E-rank hire start with more? (Cheap
    to change.)

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

16. **Special bar refilling.** After a special is used, its bar empties. Do the special's
    own hits start refilling it? Going ahead with: yes, they do. (Easy to change.)

    **Answer:**

17. **Multi-hit attacks.** When a Fighter or Rogue strikes several times in a row:
    - A: The game decides all the hits at once and just plays them one after another
      (recommended — needs no new rules).
    - B: Spread the hits out, so the target can die or move in between.

    **Answer:**

18. **Tapping a special.** When the player taps a member's full special: (Free to change
    now; harder once real-time fighting is built.)
    - A: It fires instantly as a free extra attack.
    - B: It fires instantly, and their next normal attack waits a full turn (recommended).
    - C: It waits for their next attack and replaces it, as now — up to about 7 seconds
      for a Tank.

    **Answer:**

19. **Mage's field.** The Mage's special leaves a damaging field on two enemy columns.
    Right now it ignores defence. Should it work like the Mage's other area attacks —
    can't be dodged, enemies use two-thirds of their defence (recommended)? Or should full
    defence apply? (Cheap to change.)

    **Answer:**

20. **Fighter's flurry.** The Fighter's special hits 4 times, with a chance of a 5th and
    6th. Using the normal luck chance, a 5th hit almost never happens. Should the flurry
    get its own higher chance — about 10% for a new Fighter, rising to about 37% later
    (recommended, so 5 and 6 actually show up)?

    **Answer:**
