import sys
import time
import subprocess
import threading

from playerstate import PlayerState
import config
import gameengine


class Unbuffered:
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
    def __init__(self, mutex):
        self.mutex = mutex
    def __enter__(self):
        self.mutex.acquire()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.mutex.release()

def log_function(f):
    def decorator(*args, **kwargs):
        print(f.__name__, " ", args, ", ", kwargs)
        return f(*args, **kwargs)
    return decorator


class Player:
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        assert(not PlayerState.isFinal(self._state) or self._state == value)
        if PlayerState.isFinal(value):
            if self._state != value:
                print("Player ", self.iPlayer + 1, " reaches his destiny: ", value)
            self.process.kill()
        self._state = value

    def __init__(self, exeName, iPlayer):
        self.process = subprocess.Popen(exeName.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.thread = threading.Thread(target=self.playerLoop)
        self.lock = threading.RLock()
        self._state = PlayerState.NOT_INITIATED
        self.iPlayer = iPlayer
        self.process.stdin = Unbuffered(self.process.stdin)
        self.messageToPlayer = b""
        self.messageFromPlayer = b""
    def handshake(self):
        self.process.stdin.write(b"Who are you?\n")
        answer = self.process.stdout.readline().strip()
        with MutexLocker(self.lock):
            if self.state == PlayerState.NOT_INITIATED:
                self.state = PlayerState.THINKING if answer == b"crayfish" else PlayerState.KICKED
    def playerLoop(self):
        self.handshake()
        while True:
            with MutexLocker(self.lock):
                if not PlayerState.inPlay(self.state):
                    break
                messageToPlayer = self.messageToPlayer
            if self.messageToPlayer:
                self.process.stdin.write(self.messageToPlayer)
                self.messageToPlayer = b""
            if self.state != PlayerState.READY:
                newCommand = self.process.stdout.readline().strip()
                with MutexLocker(self.lock):
                    if newCommand == b"end":
                        self.state = PlayerState.READY
                    else:
                        self.messageFromPlayer += newCommand
            time.sleep(config.mainLoopIterationDelay)

    def run(self):
        self.thread.start()

    def kick(self):
        with MutexLocker(self.lock):
            self.state = PlayerState.KICKED
    def __repr__(self):
        return str(self.iPlayer + 1)

def main():
    game = gameengine.Game()

    playerList = []
    playerNames = sys.argv[1:]
    playerNum = len(playerNames)
    for (playerExeFile, iPlayer) in zip(playerNames, range(playerNum)):
        playerList.append(Player(playerExeFile, iPlayer))
    game.setPlayers(playerList)
    initialMessages = game.initialMessages()
    for (player, message) in zip(playerList, initialMessages):
        with MutexLocker(player.lock):
            player.messageToPlayer += bytearray(message, "utf-8")
        player.run()

    turnEndTime = time.time() + config.turnDurationInSec
    while True:
        somePlayersThinking = False
        for player in playerList:
            with MutexLocker(player.lock):
                somePlayersThinking |= (player.state in [PlayerState.THINKING, PlayerState.NOT_INITIATED])
        if not somePlayersThinking or time.time() > turnEndTime:
            print("Let the turn ", game.turn, " end!")
            playerMoves = []
            for player in playerList:
                with MutexLocker(player.lock):
                    if player.state == PlayerState.THINKING:
                        player.kick()
                        playerMoves.append(None)
                    else:
                        playerMoves.append(player.messageFromPlayer.decode("utf-8"))
                        player.messageFromPlayer = b""
            engineReply = game.processTurn(playerMoves)
            for (player, reply) in zip(playerList, engineReply):
                with MutexLocker(player.lock):
                    player.state = reply[0]
                    player.messageToPlayer += bytearray(reply[1], "utf-8")

            somebodyStillPlays = False
            for player in playerList:
                with MutexLocker(player.lock):
                    somebodyStillPlays |= PlayerState.inPlay(player.state)
            if not somebodyStillPlays:
                print("Game over!")
                return
            turnEndTime = time.time() + config.turnDurationInSec

        time.sleep(config.mainLoopIterationDelay)


if __name__ == "__main__":
    main()
