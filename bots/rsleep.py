import sys
import random
import time
try:
    whoareyou = sys.stdin.readline()
    sys.stdout.write("crayfish\n")
    sys.stdout.flush( )
    number = 0
    s = sys.stdin.readline( )
    words = s.split( )
    SizeX = int(words[0])
    SizeY = int(words[1])
    nPlayers = int(words[2])
    iPlayer = int(words[3])

    d = iPlayer == 0
    while True:
        s = sys.stdin.readline( )
        while s != "end\n":
            words = s.split( )
            if (d and words[2] == "0") or (not d and words[2] == "1"):
                myposx = int(words[0])
                myposy = int(words[1])
                direction = random.choice(['E','W','N','S']) 
                if words[3] == "W":
                    sys.stdout.write("move %d %d %s\n" % (myposx, myposy, direction))
                elif words[3] == "B":
                    sys.stdout.write("spawn %d %d %s\n" % (myposx, myposy, direction))
            s = sys.stdin.readline( )
        sys.stdout.write("build %d %d F\n" % (random.randint(0, SizeX - 1), random.randint(0, SizeY - 1)))
        if random.randint(0,10) == 5:
            sys.stderr.write(str(iPlayer) + " sleeps!\n")
            time.sleep(1)
        sys.stdout.write("end\n")
        sys.stdout.flush( )
except:
    pass
