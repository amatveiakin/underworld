import sys
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
if d:
    myposx, myposy = (0, 0)
else:
    myposx, myposy = (SizeX - 1, SizeY - 1)
while True:
    try:
        direction = 'E' if d else 'W'
        s = sys.stdin.readline( )
        while s != "end\n":
            #sys.stderr.write(s) 
            s = sys.stdin.readline( )
        sys.stdout.write("move %d %d %s\n" % (myposx, myposy, direction))
        sys.stdout.write("end\n")
        sys.stdout.flush( )
        myposx += (1 if d else -1)
        d = not d
    except:
        break
