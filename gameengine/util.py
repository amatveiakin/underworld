# partial Game class
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

def _neighbourhood(self, x, y, r):
    '''
        Utility funtction.
        Returns euclidian neighbourhood of (x, y) of a radius r
    '''
    return ((x + dx, y + dy) for dx in range(-r,r+1) for dy in range(-r,r+1) \
        if self._isInside(x + dx, y + dy) and dx * dx + dy * dy <= r * r)

def _neighbours(self, x, y, r):
    '''
        Utility function.
        Returns objects in self._neighbourhood(x, y, r)
    '''
    for (newx, newy) in self._neighbourhood(x, y, r):
        obj = self.field[newy][newx]
        if obj in self.objects:
            yield obj
