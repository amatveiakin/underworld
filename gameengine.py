from playerstate import PlayerState


class Game:
    def __init__(self):
        pass
    def setPlayers(self, players):
        self.players = players
    def processTurn(self, playerMoves):
        return map(lambda x: (PlayerState.LOST if not PlayerState.isFinal(x.state) else x.state, b""), self.players)
