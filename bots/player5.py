import sys
import random
try:
    whoareyou = sys.stdin.readline()
    sys.stdout.write("crayfish\n")
    sys.stdout.flush( )
    s = sys.stdin.readline( )
    words = s.split( )
    SizeX = int(words[0])
    SizeY = int(words[1])
    nPlayers = int(words[2])
    iPlayer = int(words[3])

    while not sys.stdin.closed:
        s = sys.stdin.readline( )
        while s != "end\n":
            words = s.split( )
            if iPlayer == int(words[2]):
                myposx = int(words[0])
                myposy = int(words[1])
                direction = random.choice(['E','W','N','S']) 
                if words[3] == "W":
                    sys.stdout.write("move %d %d %s\n" % (myposx, myposy, direction))
                elif words[3] == "B":
                    sys.stdout.write("spawn %d %d %s\n" % (myposx, myposy, direction))
            s = sys.stdin.readline( )
        sys.stdout.write("build %d %d F\n" % (random.randint(0, SizeX - 1), random.randint(0, SizeY - 1)))
        sys.stdout.write("end\n")
        sys.stdout.flush( )
except:
    pass
