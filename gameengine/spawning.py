# partial Game class
from .celldefs import Cell, ObjTypes, ObjTypeDict, Building, Object, Unit, Barracks

def _canSpawn(self, charRepr):
    '''
        Can the object be built
    '''
    if not charRepr in ObjTypeDict:
        return False
    objType = ObjTypeDict[charRepr]
    if not objType.CanBeBuilt:
        return False
    return issubclass(objType, Unit)

def _setSpawnRequest(self, x, y, charRepr, iPlayer, spawner):
    '''
        Sets a request to spawn `charRep` object @(x,y)
        from the spawner object ( usually barracks )
    '''
    if not isinstance(spawner, Barracks) or \
       spawner.hasSpawnRequest or \
       not self._canSpawn(charRepr):
        raise Exception( ) 
    if not (x,y) in self._spawnRequests:
        self._spawnRequests[(x,y)] = set( )
    self._spawnRequests[(x,y)].add((iPlayer, ObjTypeDict[charRepr]))
    spawner.hasSpawnRequest = True

def _resolveSpawning(self):
    '''
        Do actual spawning
    '''
    for ((x,y), candidatesSet) in self._spawnRequests.items( ):
        if len(candidatesSet) == 1:
            (iPlayer, objType) = candidatesSet.pop( )
            cell = self.field[y][x]
            if cell in self.objects:
                continue
            if self.players[iPlayer].money >= objType.Cost:
                self.players[iPlayer].money -= objType.Cost
                newObj = objType( )
                newObj.owner = iPlayer
                newObj.x, newObj.y = (x, y)
                self.field[y][x] = newObj
                self.objects.add(newObj)
