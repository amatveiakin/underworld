class Cell:
    def __init__(self):
        self.moveCandidates = []
        self.buildCandidates = []
        
class Object(Cell):
    VisionRange = 3
    CanBeBuilt = True
    def __init__(self):
        super().__init__()
        self.hitpoints = self.MaxHitpoints
        self.newPosition = None
        self.willMove = None

class Building (Object):
    CanMove = False
    CanAttack = False

class Castle (Building):
    MaxHitpoints = 10000
    CanBeBuilt = False
    CharRepr  = "C"

class Farm (Building):
    MaxHitpoints = 1000
    Cost = 1000
    CharRepr  = "F"

class Barracks (Building):
    MaxHitpoints = 1500
    Cost = 1500
    CharRepr = "B"

class Unit (Object):
    CanMove = True
    CanAttack = True

class Warrior (Unit):
    MaxHitpoints = 500
    DamageToBuilding = 100
    DamageToUnits = 100
    Cost = 500
    CharRepr = "W"
