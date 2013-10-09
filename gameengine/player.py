# partial Game class
import os
from .celldefs import Farm
class Player:
    def __init__(self, client, game, money):
        self.client = client
        self.money = money
        self._game = game
        self.iPlayer = client.iPlayer
        self.name = client.playerDesc["name"]
    def getPlayerStats(self):
        return [("Money", self.money), ("Income", self.getIncome())]
    def getIncome(self):
        return sum([obj.Income for obj in self._game.objects if obj.owner == self.iPlayer])
