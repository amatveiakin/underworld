class PlayerState:
    NOT_INITIATED = 1
    THINKING = 2
    READY = 3
    LOST = 4
    WON = 5
    KICKED = 6

    def inPlay(state):
        return state in [THINKING, READY]
