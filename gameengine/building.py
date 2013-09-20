# partial Game class
from .celldefs import Cell, ObjTypes, ObjTypeDict, Building, Object

def _canBeBuilt(self, charRepr):
    '''
        Can the object be built
    '''
    if not charRepr in ObjTypeDict:
        return False
    objType = ObjTypeDict[charRepr]
    if not objType.CanBeBuilt:
        return False
    return issubclass(objType, Building)

def _setBuildRequest(self, x, y, charRepr, iPlayer):
    '''
        Sets a request to build `charRep` object @(x,y) for
        player iPlayer.
    '''
    if not self._canBeBuilt(charRepr):
        raise Exception( ) 
    if not (x,y) in self._buildRequests:
        self._buildRequests[(x,y)] = set( )
    self._buildRequests[(x,y)].add((iPlayer, ObjTypeDict[charRepr]))

def _resolveBuilding(self):
    '''
        Do actual building
    '''
    for ((x,y), candidatesSet) in self._buildRequests.items( ):
        if len(candidatesSet) == 1:
            (iPlayer, objType) = candidatesSet.pop( )
            cell = self.field[y][x]
            if cell in self.objects:
                continue
            if self.players[iPlayer].money >= objType.Cost:
                self.players[iPlayer].money -= objType.Cost
                newObj = objType(x, y, iPlayer)
                self.field[y][x] = newObj
                self.objects.add(newObj)
