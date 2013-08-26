import gameengine
import threading
from PyQt4 import QtGui, QtCore
import copy
import time
import sys

def makeRect(x, y, cellSize):
    return QtCore.QRect(x * cellSize, y * cellSize, cellSize, cellSize)
ObjAlignMode = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom

class VisualizerWidget(QtGui.QWidget):
    PlayerColors = [ QtGui.QColor(255, 0, 0), QtGui.QColor(0, 0, 255),
                     QtGui.QColor(0, 255, 0), QtGui.QColor(0, 0, 0) ]
    def __init__(self, visualizer):
        super(VisualizerWidget, self).__init__()
        self._visualizer = visualizer
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Underworld')
        self.show()
    def paintEvent(self, event):
        size = self.size()
        cellWidth = size.width() / self._visualizer.game.SizeX
        cellHeight = size.height() / self._visualizer.game.SizeY
        cellSize = min(cellWidth, cellHeight)
        hBarWidth = cellSize * 0.75
        hBarHeight = cellSize * 0.1
        hBarLeftOffset = (cellSize - hBarWidth) * 0.5
        hBarTopOffset = cellSize * 0.1
        objects = self._visualizer.objects

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setFont(QtGui.QFont('Decorative', cellSize / 2))
        for o in objects:
            painter.setPen(self.PlayerColors[o.owner])
            painter.drawText( makeRect(o.x, o.y, cellSize), ObjAlignMode, o.CharRepr)
            hBarGreen = hBarWidth * o.hitpoints / o.MaxHitpoints
            hBarRed = hBarWidth - hBarGreen 
            hBarLeft = o.x * cellSize + hBarLeftOffset
            hBarTop = o.y * cellSize + hBarTopOffset
            painter.setPen(QtGui.QColor(QtCore.Qt.black))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.green)))
            painter.drawRect( QtCore.QRect(hBarLeft, hBarTop, hBarGreen, hBarHeight))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
            painter.drawRect( QtCore.QRect(hBarLeft + hBarGreen, hBarTop, hBarRed, hBarHeight))
        painter.end()
        
    def event(self, ev):
        if ev.type( ) == QtCore.QEvent.User + 1:
            self.repaint( )
        return super(VisualizerWidget, self).event(ev)

class VisualizerClosedException( Exception ):
    pass

class Visualizer:
    def __init__(self, game):
        """
            Initialize a visualizer with an instance of Game.
            sets onTurnEnd binding, spawns a GUI thread
        """
        self.game = game
        self.objects = copy.deepcopy(self.game.objects)
        self._thread = threading.Thread(target=self._mainLoop)
        self._thread.setDaemon(True)
        self._thread.start( )

    def _turnEnd(self):
        """
            The event handler. Abuses the fact that assignment is atomic
        """
        self.objects = copy.deepcopy(self.game.objects)
        self._app.postEvent(self._widget, QtCore.QEvent(QtCore.QEvent.User + 1))
        time.sleep(0.1)
        if not self._thread.is_alive():
            raise VisualizerClosedException()

    def _mainLoop(self):
        """
            GUI main loop - a separate thread
        """
        self._app = QtGui.QApplication([])
        self._widget = VisualizerWidget(self)
        self.game.onTurnEnd = self._turnEnd
        self._app.exec_()

__all__ = ["Visualizer"]