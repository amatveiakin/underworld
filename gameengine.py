import playerstate as PlayerState
from random import randint
import functools


class Game:
    def __init__(self):
        self.number = 0
        self.increment = 42
        self.turn = 0
    def setPlayers(self, players):
        self.players = players
    def processTurn(self, playerMoves):
        self.number += self.increment
        self.increment = randint(-10, 10)
        #return map(lambda x: (PlayerState.LOST if not PlayerState.isFinal(x.state) else x.state, ""), self.players)
        res = []
        for (player, move) in zip(self.players, playerMoves):
            if PlayerState.isFinal(player.state):
                res.append((player.state, ""))
                continue
            x = None
            try:
                x = int(move.strip())
            except:
                res.append((PlayerState.LOST, "You've lost! A number expected.\n"))
                continue
            if x != self.number:
                res.append((PlayerState.LOST, "You've lost! Can you add numbers?\n"))
                continue
            res.append((PlayerState.THINKING, str(self.increment) + "\n"))
        if functools.reduce(lambda nInPlay, resItem: nInPlay + int(PlayerState.inPlay (resItem[0])), res, 0) == 1:
            for player in self.players:
                if PlayerState.inPlay(res[player.iPlayer][0]):
                    res[player.iPlayer] = (PlayerState.WON, res[player.iPlayer][1])
        self.turn += 1
        return res
    def initialMessages(self):
        return [str(self.increment) + "\n"] * len(self.players)
