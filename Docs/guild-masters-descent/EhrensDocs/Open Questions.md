# Open Questions — for the design docs' owner

> **Status:** Questions the build is waiting on, asked 2026-11-17, for the design docs' owner to answer. Write an answer under each question; "going ahead with" means the game already does that, so answer only if you want it different.

## How to answer

Reply under each question, or by number (e.g. "1: 110, 3: A"). Skip any you want to leave.

## Open Questions

### Loot and carrying

Capacity is counted in slots: every member carries 5, and a healing potion or an item of loot takes 1 slot each.

3. **A dead member's gear.** When a member dies in the dungeon, how does their gear get
   home? (Fairly easy to change.)
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

### Enemies

6. **Enemy strength.** Monsters have no gear. How are their attack and defence worked out?
   - A: From their level alone, so they get stronger automatically deeper down.
   - B: Each monster has its own hand-set attack and defence, and level drives only things
     like speed.

   **Answer:**

7. **Enemy types.** Going ahead with: monsters can be any of the six fighter types,
   picked at random, and each is drawn as a mirrored guild member of that type. Fine?
   (Cheap to change.)

   **Answer:**

8. **Enemy health.** Going ahead with: a monster has the same health as a member of the
   same level. Fine? (Cheap to change.)

   **Answer:**

9. **Enemy gear and loot.** The newer docs have monsters wearing gear and dives dropping
   gear. Going ahead with: keep it simple, so no monster gear and gold-only loot in the
   first version. Fine? (Easy to add later.)

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

18. **Tapping a special.** When the player taps a member's full special: (Free to change
    now; harder once real-time fighting is built.)
    - A: It fires instantly as a free extra attack.
    - B: It fires instantly, and their next normal attack waits a full turn (recommended).
    - C: It waits for their next attack and replaces it, as now — up to about 7 seconds
      for a Tank.

    **Answer:**

19. **Mage's field.** The Mage's special leaves a damaging field on two enemy columns.
    Going ahead with: the field works like the Mage's other area attacks — it can't be
    dodged, and enemies use two-thirds of their defence. Fine, or should full defence
    apply? (Cheap to change.)

    **Answer:**

