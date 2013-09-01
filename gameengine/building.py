# partial Game class
from .celldefs import Cell, ObjTypes, ObjTypeDict, Building, Object

def _canBeBuilt(self, charRepr, asBuilding):
    '''
        Can the object be built (asBuilding = true) / spawned (asBuilding = false)
    '''
    if not charRepr in ObjTypeDict:
        return False
    objType = ObjTypeDict[charRepr]
    if not objType.CanBeBuilt:
        return False
    return asBuilding == issubclass(objType, Building)

def _setBuildRequest(self, x, y, charRepr, iPlayer, asBuilding):
    '''
        Sets a request to build `charRep` object @(x,y) for
        player iPlayer. if asBuilding == False, then request spawn
    '''
    if self.field[y][x] == None: 
        self.field[y][x] = Cell( )
    if not self._canBeBuilt(charRepr, asBuilding):
        raise Exception( ) 
    if not (x,y) in self._buildRequests:
        self._buildRequests[(x,y)] = set( )
    self._buildRequests[(x,y)].add((iPlayer, ObjTypeDict[charRepr]))

def _resolveBuilding(self):
    '''
        Do actual building / spawning
    '''
    for ((x,y), candidatesSet) in self._buildRequests.items( ):
        if len(candidatesSet) == 1:
            (iPlayer, objType) = candidatesSet.pop( )
            cell = self.field[y][x]
            if cell in self.objects:
                continue
            if self.clients[iPlayer].money >= objType.Cost:
                self.clients[iPlayer].money -= objType.Cost
                newObj = objType( )
                newObj.owner = iPlayer
                newObj.x, newObj.y = (x, y)
                self.field[y][x] = newObj
                self.objects.add(newObj)
