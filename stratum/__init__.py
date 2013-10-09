import asyncore
from socket import AF_INET, SOCK_STREAM, AF_UNIX
import threading
import os

host = "10.0.2.1"
#host = "localhost"
port_data = 6785
port_command = 6786
socket_name = "/tmp/underworld/game_{gameId}/{playerId}.sock"


class BotHandler(asyncore.dispatcher):
    def __init__(self, sock, bot):
        asyncore.dispatcher.__init__(self, sock)
        self.bot = bot
        self.data = b''
    def writable(self):
        return bool(self.bot.underworldHandler and self.bot.underworldHandler.data)
    def handle_read(self):
        data = self.recv(1024)
        self.data += data
    def handle_write(self):
        sentBytes = self.send(self.bot.underworldHandler.data)
        self.bot.underworldHandler.data = self.bot.underworldHandler.data[sentBytes:]
    def handle_error(self):
        self.bot.disconnect( )
    def handle_close(self):
        self.bot.disconnect( )

class UnderworldHandler(asyncore.dispatcher):
    def __init__(self, sock, bot):
        asyncore.dispatcher.__init__(self, sock)
        self.bot = bot
        self.data = b''
    def writable(self):
        return bool(self.bot.botHandler and self.bot.botHandler.data)
    def handle_read( self):
        data = self.recv(1024)
        self.data += data
    def handle_write( self):
        sentBytes = self.send(self.bot.botHandler.data)
        self.bot.botHandler.data = self.bot.botHandler.data[sentBytes:]
    def handle_error(self):
        self.bot.disconnect( )
    def handle_close(self):
        self.bot.disconnect( )

class Bot:
    addrMap = dict()
    def __init__(self, playerId, tarfile, gameId=0):
        self.playerId = playerId
        self.tarfile = tarfile
        self.gameId = gameId
        self.underworldHandler = None
        self.botHandler = None
    def __repr__(self):
        return "playerId = {0}, tarfile={1}".format(self.playerId, self.tarfile)
    def setAddr(self, addr):
        self.__class__.addrMap[addr] = self
        self.addr = addr
    def getSocketName(self):
        return socket_name.format(gameId=self.gameId, playerId=self.playerId)
    def onUnderworldAccepted(self, sock, addr):
        self.underworldHandler = UnderworldHandler(sock, self)
    def disconnect(self):
        if self.underworldHandler:
            self.underworldHandler.close( )
        if self.botHandler:
            self.botHandler.close( )
        print("Disconnected {0}".format(self))
        
commands = """
    cd /home/player/
    wget --output-document=bot.tar.gz http://{host}/data/{tarfile}
    chown player:player bot.tar.gz
    rm -f /var/tmp/toServer
    mkfifo /var/tmp/toServer
    chmod 666 /var/tmp/toServer
    su player -c "rm -rf bot; tar -xzf bot.tar.gz; cd bot; make &> ../make.log"
    nc {host} {port} < /var/tmp/toServer | su player -c "cd bot; ./run > /var/tmp/toServer" &
"""

class ScreenHandler(asyncore.dispatcher):
    def handle_read(self):
        print(self.recv(1024))

def onClientAccepted(sock, addr):
    print("VM connected: {0}".format(addr))
    if pendingBots:
        bot = pendingBots.pop( )
        print(" Assigning bot {0}".format(bot))
        bot.setAddr(addr[0])
        connectingBots.add(bot)
        ScreenHandler(sock)
        sock.sendall(commands.format(host=host, port=port_data, tarfile=bot.tarfile).encode("utf-8"))
    else:
        sock.send(b"poweroff\n")
        print(" Unexpected VM connection!")

def runGame(bots):
    os.system("cd ..; python3 underworld.py -g stratum/game.json&")

def onPlayerAccepted(sock, addr):
    bot = Bot.addrMap[addr[0]]
    print("Player connected: {0}".format(bot))
    bot.socket = sock
    os.system("rm " + bot.getSocketName( ))
    underworldConnectionListener = Listener(bot.getSocketName( ), 
        bot.onUnderworldAccepted, AF_UNIX)
    bot.botHandler = BotHandler(sock, bot)
    connectingBots.discard(bot)
    runningBots.add(bot)
    if not connectingBots:
        runGame(runningBots)

class Listener(asyncore.dispatcher):
    def __init__(self, hostAddr, onAccept, family=AF_INET):
        asyncore.dispatcher.__init__(self)
        self.create_socket(family, SOCK_STREAM)
        self.set_reuse_addr( )
        self.bind(hostAddr)
        self.listen(1)
        self.onAccept = onAccept
    def handle_accepted(self, sock, addr):
        self.onAccept(sock, addr)

pendingBots = [Bot(0, "bot.tar.gz", 1)]
connectingBots = set( )
runningBots = set( )
def main( ):
    try:
        mainListener = Listener((host, port_data), onPlayerAccepted)
        helloListener = Listener((host, port_command), onClientAccepted)
        os.system("./launchvm &")
        print ("VM launched!")
        asyncore.loop( )
    except:
        asyncore.close_all( )
        raise

if __name__=="__main__":
    main( )
