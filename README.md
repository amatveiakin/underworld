Underworld
==========

Description
------------
AI challenge contest hosting system

Requirements
------------
* pyqt4 for python3


Usage examples
--------------
* To print help:

    `python3 underworld.py -h`

* To print help for the replay plugin:

    `python3 underworld.py -p replay -P="-h"`

* To print help for the visualizer plugin:

    `python3 underworld.py -p visualizer -P="-h"`

* Run with a reasonable default config:

    `python3 underworld.py`

Tests
-----
* game.json - basic test for every feature
* game_tcp.json - a test for tcp proto with manual play(you'll _probably_ want to
  change the timeout to something > 1sec):

            # a player has to be the server for the socket connection
            nc -l -p 5555 
            # in separate console
            python3 underworld.py -g game_tcp.json
