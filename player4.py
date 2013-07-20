import sys
import random
whoareyou = sys.stdin.readline()
print("crayfish")
sys.stdout.flush()
number = 0
while True:
    s = sys.stdin.readline( )
    increment = int(s.strip())
    number += increment
    if random.randint(1,100) == 42:
        while True:
            pass
    print(number)
    print("end")
    sys.stdout.flush()
