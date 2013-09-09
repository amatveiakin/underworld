# partial Game class
from .util import _neighbourhood
def _resolveBattle(self):
    # calculate the battles
    for obj in self.objects:
        if obj.CanAttack:
            obj.enemies = []
            for enemy in self._neighbours(obj.x, obj.y, obj.AttackRange):
                if enemy.TakesDamage and \
                   obj.owner != enemy.owner:
                        # enemy indeed
                        obj.enemies.append(enemy)
    # do the damage
    dead = set( ) 
    for obj in self.objects:
        if obj.CanAttack and obj.enemies:
            perUnit = int(obj.DamageToUnits / len(obj.enemies) + 0.5)
            for enemy in obj.enemies:
                enemy.hitpoints -= perUnit
                if enemy.hitpoints <= 0:
                    dead.add(enemy)
            obj.enemies = []
    # clean the corpses
    for obj in dead:
        self.field[obj.y][obj.x] = None
    self.objects -= dead
