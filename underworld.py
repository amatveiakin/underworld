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
       self.stream.write(data)
       self.stream.flush()
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
    @log_function
    def state(self, value):
        #if PlayerState.isFinal(self._state):
            #raise ValueError("Trying to reassign final state")
        if PlayerState.isFinal(value):
            self.process.kill()
        self._state = value

    def __init__(self, exeName, iPlayer):
        self.process = subprocess.Popen(exeName.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.thread = threading.Thread(target=self.playerLoop)
        self.lock = threading.RLock()
        self._state = PlayerState.NOT_INITIATED
        self.iPlayer = iPlayer
        self.process.stdout = Unbuffered(self.process.stdout)
        self.messageFromPlayer = b""
        self.messageToPlayer = b""
    def handshake(self):
        self.process.stdin.write(b"Who are you?\n")
        answer = self.process.stdout.readline().strip()
        with MutexLocker(self.lock):
            if self.state == PlayerState.NOT_INITIATED:
                self.state = PlayerState.READY if answer == b"crayfish" else PlayerState.KICKED
    def playerLoop(self):
        self.handshake()
        while True:
            with MutexLocker(self.lock):
                if not PlayerState.inPlay(self.state):
                    break
                messageToPlayer = self.messageToPlayer
            if  self.messageToPlayer:
                self.process.stdin.write(self.messageToPlayer)
                self.messageToPlayer = b""
            newCommand = self.process.stdout.readline().strip()
            with MutexLocker(self.lock):
                self.messageFromPlayer += newCommand

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
    print("1")
    for player in playerList:
        player.run()
    print("2")

    turnEndTime = time.time() + config.turnDurationInSec
    while True:
        #print("time = ", time.time(), ", ", turnEndTime)
        somePlayersThinking = False
        for player in playerList:
            with MutexLocker(player.lock):
                somePlayersThinking |= (player.state in [PlayerState.THINKING, PlayerState.NOT_INITIATED])
        if not somePlayersThinking or time.time() > turnEndTime:
            playerMoves = []
            for player in playerList:
                with MutexLocker(player.lock):
                    if player.state != PlayerState.READY:
                        player.kick()
                        playerMoves.append(None)
                    else:
                        playerMoves.append(player.messageFromPlayer)
            print(4)
            engineReply = game.processTurn(playerMoves)
            for (player, reply) in zip(playerList, engineReply):
                with MutexLocker(player.lock):
                    player.state = reply[0]
                    player.messageToPlayer += reply[1]

            print(5)
            somebodyStillPlays = False
            for player in playerList:
                with MutexLocker(player.lock):
                    somebodyStillPlays |= PlayerState.inPlay(player.state)
            print(6)
            if not somebodyStillPlays:
                print("Game over!")
                return
            print(7)
            turnEndTime = time.time() + config.turnDurationInSec

        time.sleep(config.mainLoopIterationDelay)


if __name__ == "__main__":
    main()
