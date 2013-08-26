# partial Game class
from .util import _neighbourhood
def _resolveBattle(self):
    # calculate the battles
    for obj in self.objects:
        if obj.CanAttack:
            obj.enemies = []
            for (x, y) in self._neighbourhood(obj.x, obj.y, obj.AttackRange):
                enemy = self.field[y][x]
                if enemy in self.objects:
                    if obj.owner != enemy.owner:
                        # enemy indeed
                        obj.enemies.append(enemy)
    # do the damage
    dead = set( ) 
    for obj in self.objects:
        if obj.CanAttack and obj.enemies:
            perUnit = obj.DamageToUnits / len(obj.enemies)
            for enemy in obj.enemies:
                enemy.hitpoints -= perUnit
                if enemy.hitpoints <= 0:
                    dead.add(enemy)
            obj.enemies = []
    # clean the corpses
    for obj in dead:
        self.field[obj.y][obj.x] = None
    self.objects -= dead