import gameengine
import argparse
import json
import sys

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage( )
        sys.stderr.write("replay plugin error: " + message + "\n")
        sys.exit(2)

class Plugin:
    def __init__(self, game, args):
        parser = ArgumentParser(prog="")
        parser.add_argument("--output-file", "-o", default="replay.txt")
        parser.add_argument("--compress", "-c", default=False, action="store_true")
        self._game = game
        self._options = parser.parse_args(args.split( ))
        if self._options.compress:
            import gzip
            import io
            self.outputFile = io.TextIOWrapper(gzip.GzipFile(filename=self._options.output_file, mode="w"))
        else:
            self.outputFile = open(self._options.output_file, "w")
        game.onTurnEnd = self._onTurnEnd
    def _onTurnEnd(self):
        d = {
            "turn": self._game.turn,
            "money": [p.money for p in self._game.clients],
            "state": [str(p.state) for p in self._game.clients],
            "objects": list(map(Plugin._getObjectDict, self._game.objects))
        }
        json.dump(d, self.outputFile)
        self.outputFile.write("\n")
    def _getObjectDict(o):
        d = {"x": o.x, "y": o.y, "owner": o.owner, "type": o.CharRepr}
        if o.TakesDamage:
            d["hitpoints"] = o.hitpoints
        return d
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        self.outputFile.close( )
