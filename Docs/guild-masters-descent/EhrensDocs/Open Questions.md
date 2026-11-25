# Open Questions — for the design docs' owner

> **Status:** Questions the build is waiting on, asked 2026-11-17, 2026-11-19 and 2026-11-20, for the design docs' owner to answer. Write an answer under each question; "going ahead with" means the game already does that, so answer only if you want it different.

## How to answer

Reply under each question, or by number (e.g. "1: 110, 3: A"). Skip any you want to leave.

## Open Questions

### Loot and carrying

Capacity is counted in slots: every member carries 5, and a healing potion or an item of loot takes 1 slot each.

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

9. **Loot.** The newer docs have dives dropping gear. Going ahead with: keep it simple,
   so gold-only loot in the first version. Fine? (Easy to add later.)

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
