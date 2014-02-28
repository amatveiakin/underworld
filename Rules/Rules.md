#Introduction

Underworld is an "AI challenge"-type game where several computer programms fight on a virtual battlefield regarding a simple set of rules 
to represent their author's programming skills. The rules defined by the current document are easily mutable to make the game more interesting.

#Formal definition

## Players and grid. Objects on the grid.

The game is played by at least 2 players controlled by computer programs. Each player has an in-game number from `0` to `nPlayers-1` where `nPlayers` is
the number of players in the game.

The action takes place on a square grid of size _m_ x _n_. Every cell of the grid is either free or occupied with a single object of one of the
following types:

|**Type**  | **Reptn**  | **Description**         |     
|--------- |:----------:|-------------------------|
|Warrior   |   `W`      | Fights with enemies     |
|Barracks  |   `B`      | Produces Warriors       | 
|Castle    |   `C`      | Lost castle = lost game | 
|Farm      |   `F`      | Gives income            | 
|Wall      |   `#`      | Neutral unpassable cells| 

## Turns
The game is turn-based. At the beginning of each turn the server sends information to the clients (players). Then they have `timeout` seconds to make their decisions
about their moves. Once server recieves the data or time for the turn is up (the players that violate the timeout get kicked immediately), 
it resolves players' actions as though they happened simultameously. If any conflicts occur 
(e.g. two warriors trying to step at the same cell), none of the players/units get advantage which means all the conflicting actions are canceled.

## Movement
The only objects that can move are warriors. Each turn a warrior can move 1 cell in one of the four directions:

|**Direction** |  **Reptn** |  **New coords**|
|--------------|:----------:|----------------|
|North         |   `N`      |   `(x, y - 1)` |
|South         |   `S`      |   `(x, y + 1)` |
|East          |   `E`      |   `(x + 1, y)` |
|West          |   `W`      |   `(x - 1, y)` |

If the cell is occupied and the unit inside it isn't going to move, the move command fails (nothing bad happens, our unit just can't step in the given direction
and thus stays where she was).

## Spawning
Each turn each barracks can spawn a warrior to one of 4 it's neighbour cells (if the player has enough money to train one).
One can't spawn units to occupied cells. However, if the target cell is 
occupied by a warrior at the beginning of turn there is a chance that she will move and the cell will become free. (See the resolving order).

## Building
Building rules are very similar to spawning rules. A building (Barracks or Farm) can be constructed 2 units away (or closer) from any of the player's other buildings.
The distance is calculated in a usual 'Euclidian' way: `d(p1, p2) = sqrt((p1.x-p2.x)^2 + (p1.y-p2.y)^2)`.

## Battle
All the battles take place automatically - no commands from players are needed. Damage is calculated in the following manner. For each unit consider a set of
enemies ( units and buildings ) which are within her attack range. The unit's damage is divided uniformly between them. All the damage assignments happen simultaneously, 
so no units die 'in process'. If after the battle a unit has non-positive hitpoints, she dies and is removed from the game.

##Income
Every farm gives you certain amount of money each turn.

## End of game
There are several ways to lose the game:

* Disconnect from server
* Get kicked by timeout
* Get kicked due to violation of security ( see Client-Server communication)
* Lose the castle

And there is only one way to win - make all other players lose.

# Client-server communication
A player program uses standard input and output streams to communicate with the server.

## Handshake and initialization
When the game starts, the server sends a standard handshake phrase "Who are you?" on a single line. The program should reply with "crayfish".
After that the server sends initial data in the form of

~~~
    SizeX(int) SizeY(int) nPlayers(int) iPlayer(int)
~~~
where `SizeX` and `SizeY` represent the size of the battlefield `nPlayers` is the total number of players participating in the game
and `iPlayer` is the number of player you are playing for.

## Server's messages
Each turn starts with the following message from the server:

`money amount(int)`

For example, if you have 1000 units of money, you will recieve a line with 

`money 1000`

This line is followed by all visible objects description in the form of

`x(int) y(int) owner(int) obj(object type reptn) hitpoints(int)`

where `0 <= x < m, 0 <= y < n`, `obj` is a single character representing object type (see above),
`owner` can be either -1 (which means the object doesn't belong to anyone) or in the interval `[0, nPlayers]`.

For example, if a player sees a wall at `(12, 42)`, she will recieve

`12 42 -1 # -1`

Or, if there is a warrior at `(13, 1)` which belongs to player #0 and currently has
41 hitpoints, the line will be

`13 1 0 W 41`

After a set of such lines comes a line with `end` in it.

## Client messages
After a player has recieves `end` from the server, she has `timeout` seconds to make her
decisions. They are represented by a sequence of commands of one the following forms:

~~~
    move  x(int) y(int) dir(dir)
    spawn x(int) y(int) dir(dir)
    build x(int) y(int) obj(object type reptn)
~~~

For the spawn command `(x, y)` is the position of the barrakcs which wants to spaw units, dir is the direction, where the unit should spawn.

## Example program

Here's an example (not very intellectual to say the least) program in python:

~~~python
import sys
import random
try:
    whoareyou = sys.stdin.readline()
    sys.stdout.write("crayfish\n")
    sys.stdout.flush( )
    s = sys.stdin.readline( )
    words = s.split( )
    SizeX = int(words[0])
    SizeY = int(words[1])
    nPlayers = int(words[2])
    iPlayer = int(words[3])

    money = None

    while not sys.stdin.closed:
        s = sys.stdin.readline( )
        while s != "end\n":
            words = s.split( )
            if words[0] == "money":
                money = int(words[1])
            elif iPlayer == int(words[2]):
                myposx = int(words[0])
                myposy = int(words[1])
                direction = random.choice(['E','W','N','S'])
                if words[3] == "W":
                    sys.stdout.write("move %d %d %s\n" % (myposx, myposy, direction))
                elif words[3] == "B":
                    sys.stdout.write("spawn %d %d %s\n" % (myposx, myposy, direction))
            s = sys.stdin.readline( )
        sys.stdout.write("build %d %d F\n" % \
            (random.randint(0, SizeX - 1), random.randint(0, SizeY - 1)))
        sys.stdout.write("end\n")
        sys.stdout.flush( )
except:
    pass
~~~

