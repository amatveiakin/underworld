from .celldefs import *
def initFooGame1(self):
    self.SizeX = 5
    self.SizeY = 5

    self.field = []

    for y in range(self.SizeY):
        self.field.append([None] * self.SizeX)

    self.field[0][0] = Castle()
    self.field[0][0].owner = 0
    self.field[self.SizeY - 1][self.SizeX - 1] = Castle()
    self.field[self.SizeY - 1][self.SizeX - 1].owner = 1
    if self.nPlayers == 4:
        self.field[0][self.SizeX - 1] = Castle()
        self.field[0][self.SizeX - 1].owner = 2
        self.field[self.SizeY - 1][0] = Castle()
        self.field[self.SizeY - 1][0].owner = 3
def initFooGame2(self):
    self.SizeX = 5
    self.SizeY = 5
    self.field = []

    for y in range(self.SizeY):
        self.field.append([None] * self.SizeX)

    self.field[0][0] = Warrior()
    self.field[0][0].owner = 0
    self.field[self.SizeY - 1][self.SizeX - 1] = Warrior()
    self.field[self.SizeY - 1][self.SizeX - 1].owner = 1
    if self.nPlayers == 4:
        self.field[0][self.SizeX - 1] = Warrior()
        self.field[0][self.SizeX - 1].owner = 2
        self.field[self.SizeY - 1][0] = Warrior()
        self.field[self.SizeY - 1][0].owner = 3
