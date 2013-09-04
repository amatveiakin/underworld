import sys
import time
import subprocess
import threading
import config
import gameengine
import playerstate as PlayerState
import json
from visualizer import Visualizer
from options import parseOptions

class Unbuffered:
    ''' Unbuffered output wrapper '''
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        try:
            self.stream.write(data)
            self.stream.flush()
        except:
            pass
    def __getattr__(self, attr):
        return getattr(self.stream, attr)


class MutexLocker:
    ''' Simple mutex lock object '''
    def __init__(self, mutex):
        self.mutex = mutex
    def __enter__(self):
        self.mutex.acquire()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.mutex.release()

def log_function(f):
    ''' A decorator to log general function calls '''
    def decorator(*args, **kwargs):
        print(f.__name__, " ", args, ", ", kwargs)
        return f(*args, **kwargs)
    return decorator


class Client:
    ''' Represents the Player object in underworld server '''
    @property
    def state(self):
        ''' state property setter ''' 
        return self._state

    @state.setter
    def state(self, value):
        ''' state property getter ''' 
        assert(not PlayerState.isFinal(self._state) or self._state == value)
        if PlayerState.isFinal(value):
            if self._state != value:
                print("Player ", self.iPlayer + 1, " reaches his destiny: ", value)
                if value == PlayerState.KICKED and self.reason:
                    print(" Reason: ", self.reason)
            self.process.kill()
        if value != self.state:
            if value == PlayerState.THINKING:
                self.startThinkingEvent.set( )
            else:
                self.startThinkingEvent.clear( )
                if callable(self.onReady):
                    self.onReady(self)
        self._state = value

    def __init__(self, exeName, iPlayer, onReady=None):
        ''' Initialize a player 
                Args:
                    exeName - the executable name ( should not spawn new processes )
                    iPlayer - player's unique ID
                    onReady - the callback which is called when the player is ready
                        onReady(player): player is a Client object
        '''
        self.process = subprocess.Popen(exeName.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.thread = threading.Thread(target=self.playerLoop)
        self.thread.setDaemon(True)
        self.lock = threading.RLock()
        self.onReady = onReady
        self._state = PlayerState.NOT_INITIATED
        self.startThinkingEvent = threading.Event( )
        self.iPlayer = iPlayer
        self.process.stdin = Unbuffered(self.process.stdin)
        self.messageFromPlayer = b""
        self.receivedLinesNo = 0
        self.reason = ""
    def handshake(self):
        ''' Perform handshake. If it fails, kick the player '''
        answer = self.process.stdout.readline().strip()
        with MutexLocker(self.lock):
            if answer != config.handshakeAck:
                self.reason = "Handshake failed"
            if self.state == PlayerState.NOT_INITIATED:
                if answer == config.handshakeAck:
                    self.state = PlayerState.READY
                else:
                    self.state = PlayerState.KICKED
    def playerLoop(self):
        ''' Player's thread main function.
            Handshakes, then repeatedly performs the IO while player is in play.
        '''
        self.handshake()
        while True:
            if not PlayerState.inPlay(self.state):
                break
            self.startThinkingEvent.wait( )
            receivedMessage = self.process.stdout.readline(config.maxRecvLineLen)
            with MutexLocker(self.lock):
                if receivedMessage.strip() == b"end":
                    self.state = PlayerState.READY
                else:
                    if not self._isMessageSecure(receivedMessage):
                        self.reason = "Spam protection"
                        self.state = PlayerState.KICKED
                        break
                    self.messageFromPlayer += receivedMessage
                    self.receivedLinesNo += 1
    def _isMessageSecure(self, message):
        return self.receivedLinesNo < config.maxRecvLinesNo and \
            len(self.messageFromPlayer) + len(message) < config.maxRecvSize and \
            message[-1:] == b"\n"

    def run(self):
        ''' Start player's IO '''
        self.thread.start()

    def kick(self, reason="for nothing"):
        ''' Kick the player '''
        with MutexLocker(self.lock):
            self.reason = reason
            self.state = PlayerState.KICKED
    def __repr__(self):
        ''' String representation - just the player's id '''
        return str(self.iPlayer + 1)

def main():
    game = gameengine.Game()
    options = parseOptions( )
    fGame = open(options.game)
    gameDesc = json.load(fGame)
    fGame.close( )

    playerList = []
    playerNames = gameDesc["players"]
    playerNum = len(playerNames)

    thinkingSetLock = threading.RLock( )
    thinkingSet = set( )
    everyoneReadyEvent = threading.Event( )
    def onClientStopThinking(client):
        with MutexLocker(thinkingSetLock):
           if client in thinkingSet:
               thinkingSet.remove(client)
           if thinkingSet == set( ):
               everyoneReadyEvent.set( )

    for (playerExeFile, iPlayer) in zip(playerNames, range(playerNum)):
        playerList.append(Client(playerExeFile, iPlayer, onClientStopThinking))

    game.setClients(playerList, gameDesc)
    v = Visualizer(game)
    initialMessages = game.initialMessages()
    thinkingSet = set(playerList)
    for (player, message) in zip(playerList, initialMessages):
        player.process.stdin.write(config.handshakeSyn + b"\n")
        player.run()

    everyoneReadyEvent.wait(config.turnDurationInSec)
    with MutexLocker(thinkingSetLock):
        thinkingSet = set( )
        for (player, message) in zip(playerList, initialMessages):
            if player.state == PlayerState.READY:
                player.state = PlayerState.THINKING
                thinkingSet.add(player)
                player.process.stdin.write(bytearray(message, "utf-8"))
        everyoneReadyEvent.clear( )

    while True:
        everyoneReadyEvent.wait(config.turnDurationInSec)
        playerMoves = []
        for player in playerList:
            with MutexLocker(player.lock):
                if player.state == PlayerState.THINKING:
                    player.kick("Timeout")
                    playerMoves.append(None)
                else:
                    playerMoves.append(player.messageFromPlayer.decode("utf-8"))
                    player.messageFromPlayer = b""
                    player.receivedLinesNo = 0

        engineReply = game.processTurn(playerMoves)
        print("Let the turn ", game.turn, " end!")
        somebodyStillPlays = False
        with MutexLocker(thinkingSetLock):
            thinkingSet = set( )
            for (player, reply) in zip(playerList, engineReply):
                with MutexLocker(player.lock):
                    player.state = reply[0]
                    somebodyStillPlays |=  PlayerState.inPlay(player.state)
                    if player.state == PlayerState.THINKING:
                        thinkingSet.add(player)
                        player.process.stdin.write(bytearray(reply[1], "utf-8"))
            everyoneReadyEvent.clear( )
        if not somebodyStillPlays:
            print("Game over!")
            return

if __name__ == "__main__":
    main()
