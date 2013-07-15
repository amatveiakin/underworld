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


class Player:
    def __init__(self, exeName):
        self.process = subprocess.Popen([exeName], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        self.thread = threading.Thread(target=self.playerLoop)
        self.lock = threading.RLock()
        self.state = PlayerState.NOT_INITIATED
        self.process.stdout = Unbuffered(self.process.stdout)
        self.messageFromPlayer = ""
        self.messageToPlayer = ""

    def playerLoop(self):
        self.process.stdin.write(b"Who are you?\n")
        answer = self.process.stdout.readline()
        self.lock.acquire()
        self.state = PlayerState.PLAYING if answer == "crayfish" else PlayerState.KICKED
        self.lock.release()
        while True:
            self.lock.acquire()
            if not PlayerState.inPlay(self.state):
                break
            messageToPlayer = self.messageToPlayer
            self.lock.release()
            if self.messageToPlayer:
                self.process.stdin.write(self.messageToPlayer)
                self.messageToPlayer = ""
            newCommand = self.process.stdout.readline()
            self.lock.acquire()
            if newCommand == "end":
                self.state = PlayerState.READY
            messageFromPlayer += newCommand
            self.messageFromPlayer = messageFromPlayer
            self.lock.release()

    def run(self):
        self.thread.run()

    def kick(self):
        self.lock.acquire()
        self.state = PlayerState.KICKED
        self.lock.release()


def main():
    game = gameengine.Game()

    playerList = []
    for playerExeFile in sys.argv[1:]:
        playerList.append(Player(playerExeFile))
    for player in playerList:
        player.run()

    turnEndTime = time.time() + config.turnDurationInSec
    while True:
        somePlayersThinking = False
        for player in playerList:
            player.lock.acquire()
            somePlayersThinking |= (player.state == PlayerState.THINKING)
            player.lock.release()

        if not somePlayersThinking or time.time() > turnEndTime:
            playerMoves = []
            for player in playerList:
                player.lock.acquire()
                if player.state != PlayerState.READY:
                    player.kick()
                    playerMoves.append(None)
                else:
                    playerMoves.append(player.messageFromPlayer)
                player.lock.release()

            engineReply = game.processTurn(playerMoves)

            for (player, reply) in zip(playerList, engineReply):
                player.lock.acquire()
                player.state = reply[0]
                player.messageToPlayer += reply[1]
                player.lock.release()

            somebodyStillPlays = False
            for player in playerList:
                player.lock.acquire()
                somebodyStillPlays |= PlayerState.inPlay(player.state)
                player.lock.release()
            if not somebodyStillPlays:
                print("Game over!")
                return

        turnEndTime = time.time() + config.turnDurationInSec


if __name__ == "__main__":
    main()
