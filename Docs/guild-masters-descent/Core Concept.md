# Guild Master's Descent

> **Status:** Early concept. Nothing is built yet — the systems are taking shape, but most
> of the numbers aren't set.

## The Premise

The player manages a guild. The player has no presence or avatar in the world — they are
not a character in it. The main screen is the inside of a guild hall.

## Time

Time passes in real time, and it keeps passing while the game is closed — missions
complete, injuries heal, and lost health is recovered while the player is away.

A dive in progress is the exception: it doesn't advance while the game is closed. It
pauses, and picks up again right where it left off.

## Guild Rank

The game starts at an F-rank guild. Grade is raised by clearing milestone quests — named,
one-off tests that appear when the guild is close to promotion. They appear on the mission
board, marked out as the promotion test, and they're separate from the routine work there.
The full ladder, in order:

F → E → D → C → B → A → S → SS → SSS

## The Three Boards

The hall has three boards — a mission board, a recruiting board, and a dungeon board.

## The Dorms and the Stations

The Dorms are where the player sees members' stats and assigns their weapons and armour.

Each specialist that works at home has a station of its own: the smithy for the
Blacksmith, the armoury for the Armourer, the laboratory for the Alchemist, and the mead
hall for the Cook. When the guild holds more than one of a trade, it is the one assigned
to that station whose work counts. A specialist away from the hall, on a dive or a
mission, is not working its station.

How gear and quality actually work is covered in the Equipment doc.

## The Mead Hall

Health lost on a dive doesn't come back at once — a member that comes home hurt needs
time to heal, the same as an injury. With no Cook in the guild, health comes back on its
own at 1 point a minute, and there is nothing to pay for — waiting is all there is. The
mead hall is a room in the hall where the player pays gold to speed that up: recovery
happens on its own given time, and gold buys it sooner.

What a single heal restores, and what it costs, are both set by the Cook — the
Specialists doc covers the Cook's tiers.

The mead hall works on every member that needs healing at once, not one at a time. Each
member being healed is charged for each minute, so what a minute costs is the Cook's
price multiplied by however many members it's healing at once — a whole party is put
right in the time a single member alone would take.

## The Party

A party is made of multiple divers, plus specialists. Specialists have a reason for being
there and need to be protected by the party. Specialists have out-of-combat abilities.

The maximum team is 15 members, including specialists, and the player chooses how many of
that to take.

## Missions

Missions are support activities that help the guild — things like gathering herbs to make
medicine, or hunting for materials to make better equipment. Missions are timed, and any
member sent on one is not available for the dungeon dive.

Missions have a stated rank, using the same F–SSS ladder as guild rank — a mission marked
C is one a C-rank guild is expected to handle. The mission board only offers missions at
or below the guild's own grade; a guild cannot reach for a mission ranked above itself. A
milestone quest is the exception: it's deliberately above the guild's grade, and the board
shows it anyway because it's a test rather than a job. There's backend variance on top of
that, though: a mission can turn out easier or harder than its stated rank suggests.
That's deliberate, to give the player a sense of mystery.

A few missions can run at once, and the cap grows with guild rank. Anything the guild
sends people out on takes one of those slots — a claim mission and a milestone quest
included, not just routine work. How many members a mission needs varies by the mission
— some want one, some want several. How long a mission takes varies by its rank: low-rank
missions take minutes, high-rank ones take hours.

Mission failure normally results in an injured status, not death — members abandon a
mission before dying. An injured member is out of action until healed — they can't be sent
on a mission or taken on a dive. They recover on their own for free, though slowly — or
the player can pay gold to speed it up. Gold only reaches the injury: a mission timer runs
its full length whatever the player pays. The exception: sending an individual member
whose own rank or tier is below the mission's rank, even one the guild as a whole is
otherwise suited for, carries a chance that member is killed.

Missions pay, and they also collect items and materials the guild can sell; some mission
rewards can themselves be items. A mission can also bring back gear — a weapon or a piece
of armour.

The intent is that mission rewards keep the guild going but don't advance it — the climb
comes from milestone quests and from what the dungeon yields.

## The Recruiting Board

The recruiting board is where new members are hired — divers and specialists alike.
Recruiting costs gold. A recruit's rank or tier caps out at the guild's own: an A-rank
guild can hire up to A-rank members.

A candidate on the board shows its type and its rank or tier plainly, along with a rough
impression of where its strengths lie — promising, unremarkable, that kind of thing. There
are no exact stat numbers.

The board restocks over time: new candidates appear as time passes, so a poor board is
worth waiting out.

The guild's roster size grows with guild rank. That's separate from the fifteen-member
party cap, which stays the same regardless of guild rank.

A member can be dismissed to make room on the roster. The gold spent recruiting and
promoting that member is lost.

The intent is that a member raised up through the ranks ends up stronger than one hired at
that rank, because it keeps the stats earned at every level climbed along the way.

Which specialist types the guild can recruit is covered in the Specialists doc.

## The Economy

Gold is the money in the game.

At rank F the guild has access to a shop. The guild sells items and materials there, and
the shop sells to the guild too — the player can buy items and equipment.

Having a blacksmith, armourer or alchemist in the guild gives it that kind of crafting.

The quality of the equipment the shop sells, and how a crafter's work compares, are
covered in the Equipment doc.

## Open Questions

- What changes at each rank from F to SSS?
- A member short of health is not the same as an injured one, and nothing says whether
  it holds them back. Can a member be sent on a dive or a mission while still short of
  health, or must they be whole first?
