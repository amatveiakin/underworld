import asyncore
import threading

#host = "10.0.2.1"
host = "localhost"
port_data = 6783
port_command = 6784

class Bot:
    addrMap = dict()
    def __init__(self, playerId, tarfile, gameId=0):
        self.playerId = playerId
        self.tarfile = tarfile
        self.gameId = gameId
    def __repr__(self):
        return "playerId = {0}, tarfile={1}".format(self.playerId, self.tarfile)
    def setAddress(self, addr):
        self.__cls__.addrMap[addr] = self
        self.addr = addr
    def fifoNames(self):
        return [x.format(self.gameId, self.playerId) for x in ["/tmp/game_{0}_bot_{1}_to", "/tmp/game_{0}_bot_{1}_from"]]

class Connection:
    def __init__(self, toClientFile, fromClientFile, socket, addr):
        self.toClientFile = toClientFile
        self.fromClientFile = fromClientFile
        self.socket = socket
        self.addr = addr
        self.threadToClient = threading.Thread( self.toClientLoop)
        self.threadToClient.setDaemon(True)
        self.threadFromClient = threading.Thread( self.fromClientLoop)
        self.threadFromClient.setDaemon(True)
        self.threadToClient.start( ) 
        self.threadFromClient.start( )

    def toClientLoop(self):
        try:
            fd = open(self.toClientFile)
            while True:
                data = fd.readline( )
                if data:
                    self.socket.send(data)
        except:
        #FIXME
            raise 
        
    def fromClientLoop(self):
        try:
            fd = open(self.fromClientFile, "w")
            while True:
                data = self.socket.recv(8192)
                fd.write(data)
                fd.flush( )
        except:
        #FIXME
            raise


commands = """
    cd /home/player/
    wget --output-document=bot.tar.gz http://{host}/data/{tarfile}
    chown player:player bot.tar.gz
    mkfifo /tmp/toServer
    mkfifo /tmp/fromServer
    chmod 666 /tmp/toServer
    chmod 666 /tmp/fromServer
    nc {host} {port} < /tmp/toServer > /tmp/fromServer &
    su player
    mkdir bot
    tar -xzf bot.tar.gz -C bot
    cd bot
    make &> ../make.log
    ./run < /tmp/fromServer > /tmp/toServer &
"""


def onClientAccept(sock, addr):
    print("VM connected: {0}".format(addr))
    if pendingBots:
        print(" Assigning bot {0}".format(bot))
        bot = pendingBots.pop( )
        bot.setAddr(addr)
        runningBots.append(bot)
        sock.send(commands.format(host=host, port=port_data, tarfile=bot.tarfile).encode("utf-8"))
        if not pendingBots:
            startGame( runningBots)
    else:
        sock.send(b"poweroff\n")
        print(" Unexpected VM connection!")

def onPlayerAccepted(sock, addr):
    bot = Bot.addrMap[addr]
    fifos = bot.fifoNames( )
    connection = Connection(fifos[0], fifos[1], sock, addr)
    
class Listener(asyncore.dispatcher):
    def __init__(self, host, port, onAccept):
        asyncore.dispatcher.__init__(self)
        self.create_socket( )
        self.set_reuse_addr( )
        self.bind((host, port))
        self.listen(5)
        self.onAccept = onAccept
    def handle_accepted(self, sock, addr):
        handler = self.onAccept(sock, addr)


def main( ):
    helloListener = Listener(host, port, onClientAccept)
    mainListener = Listener(host, port + 1, onPlayerAccepted)
    asyncore.loop( )

if __name__=="__main__":
    main( )
