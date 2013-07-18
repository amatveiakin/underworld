from playerstate import PlayerState


class Game:
    def __init__(self):
        pass

    def processTurn(self, playerMoves):
        return map(lambda x: (PlayerState.LOST, ""), playerMoves)
