# parse the options 
import argparse

def parseOptions():
    parser = argparse.ArgumentParser(description="Underworld server - play some crayfish games!")
    parser.add_argument("-g", "--game",
                        help="Game description file in json format (%(default)s)",
                        default="game.json")
    parser.add_argument("-p", "--plugin",
                        help="The plugin module name (%(default)s)",
                        default="visualizer")
    parser.add_argument("-P", "--plugin-args",
                        help="Arguments passed to the plugin",
                        default="")
    parser.add_argument("-r", "--results",
                        help="Results filename",
                        default="")
    return parser.parse_args( )
