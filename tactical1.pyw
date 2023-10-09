import os

from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QPainter, QPen, QPainterPath

from tactical import *
from PyQt5.QtCore import QTime, QTimer, QDateTime, QPoint, QSize
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QAction, QStyle, qApp, QVBoxLayout, QLabel, \
    QWidget
from PyQt5 import Qt
import sys
COLORS = [
# 17 undertones https://lospec.com/palette-list/17undertones
'#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
'#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
'#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',
]

class Ventanal(QMainWindow):
    def __init__(self, parent=None):
        super(Ventanal, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # invocamos la función del ui para que nos cargue el design

        # lo que necesitamos para poder rayar en el formulario
        self.tracing_xy = []
        self.lineHistory = []
        # self.pen = QPen(QtCore.Qt.black)#
        self.pen = QPen(QtCore.Qt.blue, 5, QtCore.Qt.SolidLine)

        #self.label = QtWidgets.QLabel()
        #canvas = QtGui.QPixmap(400, 300)
        #self.label.setPixmap(canvas)



        self.oldPos = self.pos()

        self.setAttribute(Qt.Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.Qt.WA_NoSystemBackground, False)
        # self.setWindowFlags(Qt.Qt.FramelessWindowHint)# self.setWindowFlags(Qt.Qt.WindowStaysOnTopHint | Qt.Qt.FramelessWindowHint)  el top la deja siempre visible
        self.setWindowFlags(Qt.Qt.FramelessWindowHint)
        self.setStyleSheet("Ventanal{background-color: rgb(0, 255, 255, 80);}")  # rgb(0, 215, 55, 70)

        # vamos ahora con el cronometro
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.run_watch)
        self.timer.setInterval(1000)  #
        self.mscounter = 0
        self.isreset = True

        # conectamos los slots a los botones que controlaran el reloj

        self.ui.btnStartTimer.clicked.connect(self.startTimer)
        self.ui.btnEndTimer.clicked.connect(self.endTimer)
        self.ui.btnPauseTimer.clicked.connect(self.watch_pause)
        self.ui.btnResetTimer.clicked.connect(self.watch_reset)
        self.ui.btnResetLines.clicked.connect(self.reset_ui)  # resetea las lineas

        # Para cerrardesde el menú salir
        exitAction = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton),
                             '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        self.ui.menusalir.addAction(exitAction)
        self.showTime()  # invocamos mostrar tiempo

        self.canvas = Canvas()

        w = QtWidgets.QWidget()
        l = QtWidgets.QVBoxLayout()
        w.setLayout(l)
        l.addWidget(self.canvas)

        palette = QtWidgets.QHBoxLayout()
        self.add_palette_buttons(palette)
       # l.addLayout(palette)

        self.setCentralWidget(w)


    def add_palette_buttons(self, layout):
        for c in COLORS:
            b = QPaletteButton(c)
            b.pressed.connect(lambda c=c: self.canvas.set_pen_color(c))
            layout.addWidget(b)


    def showTime(self):
        # text = str(datetime.timedelta(milliseconds=self.mscounter))[:-3]
        text = str(datetime.timedelta(seconds=self.mscounter))
        self.ui.lcdNumber.setDigitCount(5)  # 11
        if not self.isreset:  # if "isreset" is False
            self.ui.lcdNumber.display(text)
        else:
            self.ui.lcdNumber.display('0:00:00')  # self.ui.lcdNumber.display('0:00:00.000')

    def run_watch(self):
        self.mscounter += 1
        self.showTime()

    def startTimer(self):
        self.timer.start()
        self.isreset = False
        self.ui.btnResetTimer.setEnabled(True)
        self.ui.btnStartTimer.setEnabled(True)
        self.ui.btnEndTimer.setEnabled(True)
        self.ui.btnPauseTimer.setDisabled(False)

    def endTimer(self):
        self.timer.stop()
        self.mscounter = 0
        self.ui.btnResetTimer.setEnabled(False)
        self.ui.btnStartTimer.setEnabled(True)
        self.ui.btnEndTimer.setEnabled(True)
        self.ui.btnPauseTimer.setDisabled(True)

    def watch_pause(self):
        self.timer.stop()
        self.ui.btnResetTimer.setEnabled(False)
        self.ui.btnStartTimer.setEnabled(True)
        self.ui.btnEndTimer.setEnabled(True)
        self.ui.btnPauseTimer.setDisabled(True)

    def watch_reset(self):
        self.timer.stop()
        self.mscounter = 0
        self.isreset = True
        self.showTime()
        self.ui.btnResetTimer.setEnabled(True)
        self.ui.btnStartTimer.setEnabled(True)
        self.ui.btnEndTimer.setEnabled(False)
        self.ui.btnPauseTimer.setDisabled(True)

        # funciones de dibujo
        # La función de copia repintada se dibuja principalmente aquí
    def set_pen_color(self, c):
        self.pen_color = QtGui.QColor(c)

    def mouseMoveEvent(self, e):
        if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time.

        painter = QtGui.QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()
        self.update()

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

    def reset_ui(self):
        """Clear and reinitalize main layouts content"""
        #os.execl(sys.executable, sys.executable, *sys.argv)
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
        print(status)


    def salir(self):
        self.close()


class QPaletteButton(QtWidgets.QPushButton):

    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QtCore.QSize(24,24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)

class Canvas(QtWidgets.QLabel):

    def __init__(self):
        super().__init__()
        #pixmap = QtGui.QPixmap(1200, 900)
        #self.setPixmap(pixmap)

        self.last_x, self.last_y = None, None
        self.pen_color = QtGui.QColor('#000000')

    def set_pen_color(self, c):
        self.pen_color = QtGui.QColor(c)

    def mouseMoveEvent(self, e):
        if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time.

        painter = QtGui.QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()
        self.update()

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon("./images/cartoon1.ico"))
    main = Ventanal()
    main.show()
    sys.exit(app.exec_())
