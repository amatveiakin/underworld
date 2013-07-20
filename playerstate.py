# export only needed names - do't export PlayerStateObj
__all__ = ['NOT_INITIATED', 'THINKING', 'READY', 'LOST', 'WON', 'KICKED', 'inPlay', 'isFinal']
class PlayerStateObj:
    ''' Represents player's state '''
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
    return state in [THINKING, READY]
def isFinal(state):
    return state in [LOST, WON, KICKED]

