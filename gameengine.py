# Legend:
# dir = "N", "S", "W", "E"
# object = "castle", "farm", "barracks", "warrior"

# Server -> client protocol:
#  init:
#   SizeX(int) SizeY(int) nPlayers(int) iPlayer(int)
#   + 0th turn

#  turn:
#   x(int) y(int) owner(int) object(object) hitpoints(int)
#   ...
#   x(int) y(int) owner(int) object(object) hitpoints(int)
#   end

# Client -> server protocol:
#  move  x(int) y(int) dir(dir)
#  spawn x(int) y(int) dir(dir)
#  build x(int) y(int) object(object)


import playerstate as PlayerState
import functools


class Game:
    SizeX = 100
    SizeY = 50
    class Object:
        VisionRange = 3
        CanBeBuilt = True
        def __init__(self):
            self.hitpoints = self.MaxHitpoints

    class Building (Object):
        CanMove = False
        CanAttack = False
        pass
    class Castle (Building):
        MaxHitpoints = 10000
        CanBeBuilt = False
    class Farm (Building):
        MaxHitpoints = 1000
        Cost = 1000
    class Barracks (Building):
        MaxHitpoints = 1500
        Cost = 1500

    class Unit (Object):
        CanMove = True
        CanAttack = True
        pass
    class Warrior (Unit):
        MaxHitpoints = 500
        DamageToBuilding = 100
        DamageToUnits = 100
        Cost = 500

    class Player:
        InitialMoney = 3000
        def __init__(self):
            self.money = InitialMoney

    def __init__(self):
        pass
    def setClients(self, clients):
        nPlayers = len(clients)
        assert(self.isPlayerNumAcceptable(nPlayers))
        self.clients = clients
        self.field = []
        for y in range(self.SizeY):
            field.append([None] * self.SizeX)
        field[0][0] = Castle()
        field[0][0].owner = 0
        field[SizeY - 1][SizeX - 1] = Castle()
        field[SizeY - 1][SizeX - 1].owner = 1
        if nPlayers == 4:
            field[0][SizeX - 1] = Castle()
            field[0][SizeX - 1].owner = 2
            field[SizeY - 1][0] = Castle()
            field[SizeY - 1][0].owner = 3

    def processTurn(self, playerMoves):
        pass
    def initialMessages(self):
        #json.dumps({key: val for (key, val) in dict(A.__dict__).items( ) if key[:2]!='__'})  # TODO
        pass
    def isPlayerNumAcceptable(self, nPlayers):
        return nPlayers in [2, 4]