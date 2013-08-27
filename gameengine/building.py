# partial Game class
from .celldefs import Cell, ObjTypes, ObjTypeDict, Building, Object

def log_function(f):
    ''' A decorator to log general function calls '''
    def decorator(*args, **kwargs):
        print(f.__name__, " ", args, ", ", kwargs)
        return f(*args, **kwargs)
    return decorator

def _canBeBuilt(self, charRepr, iPlayer, asBuilding):
    if not charRepr in ObjTypes:
        objType = ObjTypeDict[charRepr]
    if not objType.CanBeBuilt:
        return False
    return asBuilding == issubclass(objType, Building)

def _setBuildRequest(self, x, y, charRepr, iPlayer, asBuilding):
    if self.field[y][x] == None: 
        self.field[y][x] = Cell( )
    if not self._canBeBuilt(charRepr, iPlayer, asBuilding):
        raise Exception( ) 
    if not (x,y) in self._buildRequests:
        self._buildRequests[(x,y)] = set( )
    self._buildRequests[(x,y)].add((iPlayer, ObjTypeDict[charRepr]))

def _resolveBuilding(self):
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
