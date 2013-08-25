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

class Game:
    from .celldefs import Cell, Object, Building, Castle, Farm, Barracks, Unit, Warrior
    from .initgame import initFooGame1, initFooGame2
    class Player:
        InitialMoney = 3000
        def __init__(self):
            self.money = InitialMoney

    def __init__(self):
        self.onTurnEnd = None 
        pass

    def setClients(self, clients):
        ''' initializes the game with specified list of clients '''
        self.nPlayers = len(clients)
        assert(self.isPlayerNumAcceptable(self.nPlayers))
        self.clients = clients
        self.initFooGame2( )
        self.turn = 0

    def processTurn(self, playerMoves):
        ''' 
            Process inputs from all clients.
            playerMoves is a list with nPlayers items, each of which is a string with a player's move 
            returns list of nPlayers tuples (new playerState, message to player)
        '''
        for iPlayer in range(self.nPlayers):
            if not PlayerState.inPlay(self.clients[iPlayer].state):
                continue
            linesFromPlayer = playerMoves[iPlayer].strip( ).split("\n")
            for line in linesFromPlayer:
                try:
                    words = line.split( )
                    x = int(words[1])
                    y = int(words[2])
                    cell = self.field[y][x]
                    if words[0] == "move":
                        if cell.owner != iPlayer or not cell.CanMove:
                            raise Exception( )
                        direction = words[3]
                        (newx, newy) = Game._applyDirection(x, y, direction)
                        if self._isInside(newx, newy):
                            self._setMoveRequest(x, y, newx, newy)
                    elif words[0] == "build":
                        pass
                    elif words[0] == "spawn":
                        pass
                    else:
                        raise Exception( )
                except:
                    # just ignore incorrect moves
                    pass
                
        self._resolveMovement( )
        self._cleanup( )
        self.turn += 1
        res = []
        for iPlayer in range(self.nPlayers):
            res.append((PlayerState.THINKING, self.getPlayerInfoString(iPlayer) + "end\n"))
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
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                if isinstance(self.field[y][x], Game.Object):
                    msg.append(self._compose_cell_info(x, y))
        return "\n".join(msg) + "\n"
    def _compose_cell_info(self, x, y):
        '''
            Returns a string representing info about a cell @(x, y)
        '''
        cell = self.field[y][x]
        return "%d %d %d %s %d" % (x, y, cell.owner, cell.CharRepr, cell.hitpoints)
    def _applyDirection(x, y, direction):
        '''
            Utility function. 
            Returns where (x,y) would be if it went by direction in form of a  tuple.
        '''
        newx = x
        newy = y
        if direction == 'N':
            newy = y - 1
        elif direction == 'S':
            newy = y + 1
        elif direction == 'W':
            newx = x - 1
        elif direction == 'E':
            newx = x + 1
        return (newx, newy)
    def _isInside(self, x, y):
        ''' 
            Utility function.
            Returns true iff (x,y) is inside the board
        '''
        return x >= 0 and x < self.SizeX and y >= 0 and y < self.SizeY
    def _setMoveRequest(self, x, y, newx, newy):
        ''' 
            Define that the object @(x,y) wants to move to (newx, newy)
            Stay calm: the object isn't moving anywhere yet.
        '''
        self.field[y][x].newPosition = (newx, newy)

        if self.field[newy][newx] is None:
            self.field[newy][newx] = Game.Cell( )
        self.field[newy][newx].moveCandidates.append((x,y))
        
    def _cleanup(self):
        '''
            Cleans up intermediate turn info about battles, movements, etc.
            Call each time a turn ends.
        '''
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                cell = self.field[y][x]
                if not (cell is None):
                    cell.moveCandidates = []
                    cell.buildCandidates = []
                    if isinstance(cell, Game.Object):
                        cell.newPosition = None
                        cell.willMove = None
    def _resolveMovement(self):
        '''
            Performs collisions resolution and does actual moving of units
        '''
        def passable(startx, starty):
            def passableRec(x, y, check=True):
                cell = self.field[y][x]
                if check and (x, y) == (startx, starty):
                    return True
                if cell is None:
                    return True
                if len(cell.moveCandidates) >= 2:
                    return False
                if not isinstance(cell, Game.Object):
                    return True
                if not (cell.willMove is None):
                    return cell.willMove
                if cell.newPosition is None:
                    return False
                newx, newy = cell.newPosition
                if passableRec(newx, newy):
                    cell.willMove = True
                    return True
                else:
                    cell.willMove = False
                    return False
            return passableRec(startx, starty, False)
        def pushRec(x, y):
            cell = self.field[y][x]
            if isinstance(cell, Game.Object):
                (newx, newy) = cell.newPosition
                pushRec(newx, newy)
                self.field[newy][newx] = cell
                self.field[y][x] = None
                
        # first determine simple -><- collisions
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                cell = self.field[y][x]
                if isinstance(cell, Game.Object) and cell.newPosition:
                    newCell = self.field[cell.newPosition[1]][cell.newPosition[0]]
                    if isinstance(newCell, Game.Object) and newCell.newPosition and \
                        newCell.newPosition == (x, y):
                        cell.willMove = False
        # now resolve everything else, including cyclic rotation
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                cell = self.field[y][x]
                if isinstance(cell, Game.Object) and cell.newPosition:
                    (newx, newy) = cell.newPosition
                    if cell.willMove is None:
                        cell.willMove = passable(newx, newy)
        # only now we can actually safely move
        for y in range(self.SizeY):
            for x in range(self.SizeX):
                cell = self.field[y][x]
                if isinstance(cell, Game.Object) and cell.newPosition:
                    (newx, newy) = cell.newPosition
                    if (cell.willMove is True) and (cell.newPosition != (x, y)):
                        self.field[y][x] = None
                        pushRec(newx, newy)
                        self.field[newy][newx] = cell
