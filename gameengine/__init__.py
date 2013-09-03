# Legend:
# dir = "N", "S", "W", "E"
# object = "castle", "farm", "barracks", "warrior"

# Server -> client protocol:
#  init:
#   SizeX(int) SizeY(int) nPlayers(int) iPlayer(int)
#   + 0th turn

#  turn:
#   x(int) y(int) owner(int) object(object) [hitpoints(int)]
#   ...
#   x(int) y(int) owner(int) object(object) [hitpoints(int)]
#   end

# Client -> server protocol:
#  move  x(int) y(int) dir(dir)
#  spawn x(int) y(int) dir(dir)
#  build x(int) y(int) object(object)

import playerstate as PlayerState

class Game:
    from .celldefs import Cell, Object, ObjectWithHitpoints, Building, Farm, Castle, Barracks, Unit, Warrior, Wall, ObjTypes, ObjTypeDict

    def __init__(self):
        self.onTurnEnd = None 
        self._buildRequests = dict( )
        self._spawnRequests = dict( )
        self._cellsToCleanup = set()

    def setClients(self, clients, gameDesc):
        ''' initializes the game with specified list of clients '''
        self.nPlayers = len(clients)
        self.clients = clients
        self.turn = 0
        self.objects = set( )
        self.SizeX = gameDesc["sizex"]
        self.SizeY = gameDesc["sizey"]
        self.field = []
        for y in range(self.SizeY):
            self.field.append([None] * self.SizeX)
        try:
            for o in gameDesc["objects"]:
                objType = Game.ObjTypeDict[o["type"]]
                newObj = objType()
                (newObj.x, newObj.y) = (o["x"], o["y"])
                newObj.owner = o["owner"]
                self.field[newObj.y][newObj.x] = newObj
                self.objects.add(newObj)
            for iPlayer in range(len(clients)):
                self.clients[iPlayer].money = gameDesc["money"][iPlayer]
        except Exception as e:
            raise e
                


    def processTurn(self, playerMoves):
        ''' 
            Process inputs from all clients.
            playerMoves is a list with nPlayers items, each of which is a string with a player's move 
            returns list of nPlayers tuples (new playerState, message to player)
        '''
        for iPlayer in range(self.nPlayers):
            if not PlayerState.inPlay(self.clients[iPlayer].state) or  \
                not playerMoves[iPlayer]:
                continue
            linesFromPlayer = playerMoves[iPlayer].strip( ).split("\n")
            for line in linesFromPlayer:
                try:
                    words = line.split( )
                    x = int(words[1])
                    y = int(words[2])
                    cell = self.field[y][x]
                    if words[0] == "move":
                        if cell.owner != iPlayer or not cell.CanMove or cell.newPosition:
                            raise Exception( )
                        direction = words[3]
                        (newx, newy) = Game._applyDirection(x, y, direction)
                        if self._isInside(newx, newy):
                            self._setMoveRequest(x, y, newx, newy)
                    elif words[0] == "build":
                        alliedBuildings = (o for o in self._neighbours(x, y, 2) \
                            if o.owner == iPlayer and isinstance(o, Game.Building))
                        if len(list(alliedBuildings)) > 0:
                            self._setBuildRequest(x, y, words[3], iPlayer)
                    elif words[0] == "spawn":
                        if cell.owner != iPlayer:
                            raise Exception( )
                        direction = words[3]
                        (newx, newy) = Game._applyDirection(x, y, direction)
                        if not self._isInside(newx, newy):
                            raise Exception( )
                        self._setSpawnRequest(newx, newy, "W", iPlayer, cell)
                    else:
                        raise Exception( )
                except Exception as e:
                    # just ignore incorrect moves
                    pass
                
        self._resolveIncome( )
        self._resolveMovement( )
        self._resolveBattle( )
        self._resolveBuilding( )
        self._resolveSpawning( )
        self._checkWinConditions( )
        self._cleanup( )
        self.turn += 1
        res = []
        for iPlayer in range(self.nPlayers):
            if PlayerState.inPlay(self.clients[iPlayer].state):
                res.append((PlayerState.THINKING, self.getPlayerInfoString(iPlayer) + "end\n"))
            else:
                res.append((self.clients[iPlayer].state, "end\n"))
        if callable(self.onTurnEnd):
            try:
                self.onTurnEnd( )
            except: 
                # kick everyone: the interactive UI is dead
                res = [ (PlayerState.KICKED, "" ) ] * self.nPlayers
        return res

    def initialMessages(self):
        '''
            Returs the list of nPlayers initial messages to players
        '''
        res = []
        for iPlayer in range(self.nPlayers):
            res.append(("%d %d %d %d" % (self.SizeX, self.SizeY, self.nPlayers, iPlayer)) + \
                "\n" + self.getPlayerInfoString(iPlayer) + "end\n")
        return res
            
    def isPlayerNumAcceptable(self, nPlayers):
        return nPlayers in [2, 4]

    def getPlayerInfoString(self, iPlayer):
        '''
            The string representing all objects visible to the player iPlayer
            in the format below:
                x y owner type hitpoints
        '''
        msg = []
        for obj in self.objects:
            msg.append(self._compose_cell_info(obj))
        return "\n".join(msg) + ("\n" if msg else "")
    def _compose_cell_info(self, obj):
        '''
            Returns a string representing info about a cell @(x, y)
        '''
        if isinstance(obj, Game.ObjectWithHitpoints):
            return "%d %d %d %s %d" % (obj.x, obj.y, obj.owner, obj.CharRepr, obj.hitpoints)
        else:
            return "%d %d %d %s" % (obj.x, obj.y, obj.owner, obj.CharRepr)
    def _resolveIncome(self):
        for o in self.objects:
            if o.owner >=0 and isinstance(o, Game.Farm):
                self.clients[o.owner].money += 50

    def _checkWinConditions(self):
        alivePlayers = set( )
        for obj in self.objects:
            if obj.owner >= 0:
                alivePlayers.add(obj.owner)
        for iPlayer in range(self.nPlayers):
            if not iPlayer in alivePlayers:
                self.clients[iPlayer].state = PlayerState.LOST
        if len(alivePlayers) == 1:
            self.clients[alivePlayers.pop( )].state = PlayerState.WON
        
    def _cleanup(self):
        '''
            Cleans up intermediate turn info about battles, movements, etc.
            Call each time a turn ends.
        '''
        for (x, y) in self._cellsToCleanup:
            if not self.field[y][x] in self.objects:
                self.field[y][x] = None
        for obj in self.objects:
            obj.willMove = None
            obj.newPosition = None
            obj.moveCandidates = []
            obj.hasSpawnRequest = False
        self._cellsToCleanup = set()
        self._buildRequests = dict( )
        self._spawnRequests = dict( )
    from .movement import _resolveMovement, _setMoveRequest
    from .util import _applyDirection, _isInside, _neighbourhood, _neighbours
    from .battle import _resolveBattle
    from .building import _setBuildRequest, _resolveBuilding, _canBeBuilt
    from .spawning import _setSpawnRequest, _resolveSpawning, _canSpawn
