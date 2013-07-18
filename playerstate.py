class PlayerState:
    class PlayerStateObj:
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return self.name
    NOT_INITIATED = PlayerStateObj("NOT_INITIATED")
    THINKING = PlayerStateObj("THINKING")
    READY = PlayerStateObj("READY")
    LOST = PlayerStateObj("LOST")
    WON = PlayerStateObj("WON")
    KICKED = PlayerStateObj("KICKED")
    def inPlay(state):
        return state in [PlayerState.THINKING, PlayerState.READY]
    def isFinal(state):
        return state in [PlayerState.LOST, PlayerState.WON, PlayerState.KICKED]