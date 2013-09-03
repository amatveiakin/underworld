# parse the options 
import argparse

def parseOptions():
    parser = argparse.ArgumentParser(description="Underworld server - play some crayfish games!")
    parser.add_argument("-g", "--game",
                        help="Game description file in json format",
                        default="game.json")
    return parser.parse_args( )
