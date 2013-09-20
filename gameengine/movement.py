# partial Game class
from .celldefs import Cell
def _setMoveRequest(self, x, y, newx, newy):
    ''' 
        Define that the object @(x,y) wants to move to (newx, newy)
        Stay calm: the object isn't moving anywhere yet.
    '''
    self.field[y][x].newPosition = (newx, newy)
    self._moveRequests[(newx,newy)] = self._moveRequests.get((newx, newy), 0) + 1
def _resolveMovement(self):
    '''
        Performs collisions resolution and does actual moving of units
    '''
    def passable(startx, starty):
        def passableRec(x, y, firstIteration=False):
            cell = self.field[y][x]
            if not firstIteration and (x, y) == (startx, starty):
                return True
            if self._moveRequests.get((x, y), 0) >= 2:
                return False
            if cell is None:
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
        return passableRec(startx, starty, True)
    def pushRec(x, y):
        cell = self.field[y][x]
        if not (cell is None):
            (newx, newy) = cell.newPosition
            pushRec(newx, newy)
            self.field[newy][newx] = cell
            (cell.x, cell.y) = (newx, newy)
            self.field[y][x] = None
            
    movingObjects = {obj for obj in self.objects if obj.newPosition}
    # first determine simple -><- collisions
    for obj in movingObjects:
        newCell = self.field[obj.newPosition[1]][obj.newPosition[0]]
        if newCell in movingObjects and newCell.newPosition == (obj.x, obj.y):
            obj.willMove = False
    # now resolve everything else, including cyclic rotation
    for obj in movingObjects:
        (newx, newy) = obj.newPosition
        if obj.willMove is None:
            obj.willMove = passable(newx, newy)
    # only now we can actually safely move
    for obj in movingObjects:
        (newx, newy) = obj.newPosition
        if (obj.willMove is True) and (obj.newPosition != (obj.x, obj.y)):
            self.field[obj.y][obj.x] = None
            pushRec(newx, newy)
            self.field[newy][newx] = obj
            (obj.x, obj.y) = (newx, newy)
