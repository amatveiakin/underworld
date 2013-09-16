import gameengine
import threading
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import Qt
import copy
import time
import sys
import argparse

minZoomExp = -20.
maxZoomExp = 10.
defaultZoom = -5.

cellSize = 64
hBarBorder = 6
hBarHeight = 6

def bound(minVal, current, maxVal):
    return max(min(current, maxVal), minVal)

class VisualizerWidget(QtGui.QWidget):
    PlayerColors = [ QtGui.QColor(255, 0, 0), QtGui.QColor(0, 0, 255),
                     QtGui.QColor(0, 255, 0), QtGui.QColor(0, 0, 0) ]
    NeutralColor = QtGui.QColor(0, 0, 0)
    def __init__(self, parent, visualizer):
        super(VisualizerWidget, self).__init__(parent)
        self._visualizer = visualizer
        self.zoomExp = defaultZoom
        self.shift = QtCore.QPointF(0., 0.)
        self.isDragging = False
    def zoomFactor(zoomExp):
        return pow(1.1, zoomExp)
    def currentTransform(self):
        zoom = VisualizerWidget.zoomFactor(self.zoomExp)
        return QtGui.QTransform(zoom, 0., 0., zoom, self.shift.x(), self.shift.y())
    def paintEvent(self, event):
        objects = self._visualizer.objects
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        painter.setTransform(self.currentTransform())
        painter.setFont(QtGui.QFont('', cellSize / 2))
        for o in objects:
            if o.owner >= 0:
                mainColor = self.PlayerColors[o.owner]
            else:
                mainColor = self.NeutralColor
            cellRect = QtCore.QRect(o.x * cellSize, o.y * cellSize, cellSize, cellSize)
            hBarRect = cellRect.adjusted(hBarBorder, hBarBorder, -hBarBorder, -hBarBorder)
            hBarRect.setHeight(hBarHeight)
            textRect = cellRect
            textRect.setTop(hBarRect.bottom())
            if isinstance(o, gameengine.Game.ObjectWithHitpoints):
                hBarGreenRect = copy.copy(hBarRect)
                hBarGreenRect.setWidth(hBarRect.width() * o.hitpoints / o.MaxHitpoints)
                pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.black))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.red)))
                painter.drawRect(hBarRect)
                painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.green)))
                painter.drawRect(hBarGreenRect)
            painter.setPen(self.PlayerColors[o.owner])
            painter.drawText(textRect, QtCore.Qt.AlignCenter, o.CharRepr)
        painter.end()
    def wheelEvent(self, event):
        oldZoom = VisualizerWidget.zoomFactor(self.zoomExp)
        self.zoomExp += event.delta() / 120.
        self.zoomExp = bound(minZoomExp, self.zoomExp, maxZoomExp)
        newZoom = VisualizerWidget.zoomFactor(self.zoomExp)
        self.shift += (event.pos() - self.shift) * (1. - newZoom / oldZoom)
        self.update()
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.isDragging = True
            self.dragStart = event.pos()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.isDragging = False
    def mouseMoveEvent(self, event):
        if self.isDragging:
            self.shift += event.pos() - self.dragStart
            self.dragStart = event.pos()
            self.update()

class MainWidget(QtGui.QWidget):
    def __init__(self, visualizer):
        super( ).__init__( )
        self.layout = QtGui.QHBoxLayout()
        self.layout.setMargin(0)
        self.layout.addWidget(VisualizerWidget(self, visualizer))
        self.setLayout(self.layout)
        self.setGeometry(120, 120, 480, 480)
        self.setWindowTitle('Underworld')
        self.show()
    def event(self, ev):
        if ev.type( ) == QtCore.QEvent.User + 1:
            self.update( )
        return super(MainWidget, self).event(ev)

class VisualizerClosedException( Exception ):
    pass

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage( )
        sys.stderr.write("replay plugin error: " + message + "\n")
        sys.exit(2)

class Plugin:
    def __init__(self, game, args):
        """
            Initialize a visualizer with an instance of Game.
            sets onTurnEnd binding, spawns a GUI thread
        """
        parser = ArgumentParser(prog="")
        parser.add_argument("--turn-time", "-t", 
                            type=float, 
                            help="delay between turns in seconds(%(default)f)",
                            default=0.1)
        self._options = parser.parse_args(args.split( ))
        self._readyEvent = threading.Event( )
        self.game = game
        self.objects = copy.deepcopy(self.game.objects)
        self._thread = threading.Thread(target=self._mainLoop)
        self._thread.start( )
        self._readyEvent.wait( )

    def _turnEnd(self):
        """
            The event handler. Abuses the fact that assignment is atomic
        """
        self.objects = copy.deepcopy(self.game.objects)
        self._app.postEvent(self._widget, QtCore.QEvent(QtCore.QEvent.User + 1))
        time.sleep(self._options.turn_time)
        if not self._thread.is_alive():
            raise VisualizerClosedException()

    def _mainLoop(self):
        """
            GUI main loop - a separate thread
        """
        self._app = QtGui.QApplication([])
        self._widget = MainWidget(self)
        self.game.onTurnEnd = self._turnEnd
        self._readyEvent.set( )
        self._app.exec_()

__all__ = ["Visualizer"]
