import os

import pygetwindow
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets, uic
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

import pyautogui#librerías para poder capturar la ventana en screenshot


correctos=0
fallidos=0
indices=-1

COLORS = [
    # 17 undertones https://lospec.com/palette-list/17undertones
    '#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
    '#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
    '#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',
]

# define the data
theTitle = "pyqtgraph plot"
y = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]#[1,2,3,4,5,6,7,8,9,10]
y2 = []#[0, 2, 0, 4, 5, 6, 7, 0, 9, 10]#[0, 1, 0, 4, 12, 14, 16, 17, 14, 22]
x = range(0, 10)


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

        self.oldPos = self.pos()

        ##self.setFixedSize(2000, 1200)  # para establecer tamaño de la ventana

        self.setAttribute(Qt.Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.Qt.WA_NoSystemBackground, False)
        # self.setWindowFlags(Qt.Qt.FramelessWindowHint)# self.setWindowFlags(Qt.Qt.WindowStaysOnTopHint | Qt.Qt.FramelessWindowHint)  el top la deja siempre visible
        self.setWindowFlags(Qt.Qt.FramelessWindowHint)
        self.setStyleSheet("Ventanal{background-color: rgb(0, 255, 255, 80);}")  # rgb(0, 215, 55, 70)

        # parte del code para la paleta de colores

        # vamos ahora ocn el cronometro
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
        self.ui.checkBlue.stateChanged.connect(self.state_changed) # chequear casillas de color
        self.ui.checkBlack.stateChanged.connect(self.state_changed)  # chequear casillas de color
        self.ui.btnOk.clicked.connect(self.sumarCorrectos)
        self.ui.btnOff.clicked.connect(self.sumarFallidos)
        # Sub Window
        self.sub_window = MainWindow()#esta línea la usamos para invocar la segunda ventana q hemosllamado MainWindow
        self.ui.btnStats.clicked.connect(self.sub_window.plot)#self.sub_window.show

        # Para cerrardesde el menú salir
        exitAction = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton),
                             '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        self.ui.menusalir.addAction(exitAction)
        #menú stats
        self.ui.mnuStats.triggered.connect(self.sub_window.show)

        self.showTime()  # invocamos mostrar tiempo

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

    def paintEvent(self, QPaintEvent):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.setPen(self.pen)

        start_x_temp = 0
        start_y_temp = 0

        if self.lineHistory:
            for line_n in range(len(self.lineHistory)):
                for point_n in range(1, len(self.lineHistory[line_n])):
                    start_x, start_y = self.lineHistory[line_n][point_n - 1][0], self.lineHistory[line_n][point_n - 1][
                        1]
                    end_x, end_y = self.lineHistory[line_n][point_n][0], self.lineHistory[line_n][point_n][1]
                    self.painter.drawLine(start_x, start_y, end_x, end_y)

        for x, y in self.tracing_xy:
            if start_x_temp == 0 and start_y_temp == 0:
                self.painter.drawLine(self.start_xy[0][0], self.start_xy[0][1], x, y)
            else:
                self.painter.drawLine(start_x_temp, start_y_temp, x, y)

            start_x_temp = x
            start_y_temp = y

        self.painter.end()

    def mousePressEvent(self, QMouseEvent):
        self.start_xy = [(QMouseEvent.pos().x(), QMouseEvent.pos().y())]

    def mouseMoveEvent(self, QMouseEvent):
        self.tracing_xy.append((QMouseEvent.pos().x(), QMouseEvent.pos().y()))
        # self.update()
        # self.pen = QPen(QtCore.Qt.blue, 5, QtCore.Qt.SolidLine)self.setColor(self.pen_color)
        self.update()

    def state_changed(self, int):
        if self.ui.checkBlue.isChecked():
            self.ui.checkBlack.setChecked(False)
            self.ui.checkRed.setChecked(False)
            self.pen = QPen(QtCore.Qt.blue, 5, QtCore.Qt.SolidLine)

        elif self.ui.checkBlack.isChecked():
            self.ui.checkBlue.setChecked(False)
            self.ui.checkRed.setChecked(False)
            self.pen = QPen(QtCore.Qt.black, 5, QtCore.Qt.SolidLine)

        elif self.ui.checkRed.isChecked():
            self.pen = QPen(QtCore.Qt.red, 5, QtCore.Qt.SolidLine)
            self.ui.checkBlue.setChecked(False)
            self.ui.checkBlack.setChecked(False)

    # Adicionamos paleta(fila) de colores al formulario
    def set_pen_color(self, c):
        self.pen_color = QtGui.QColor(c)

    def mouseReleaseEvent(self, QMouseEvent):
        self.lineHistory.append(self.start_xy + self.tracing_xy)
        self.tracing_xy = []

    def reset_ui(self):
        """Clear and reinitalize main layouts content"""
        # os.execl(sys.executable, sys.executable, *sys.argv)
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
        print(status)
        # vamos a guardar un pantallazo de la ventana
        # Capturar pantalla.
        #screenshot = pyautogui.screenshot()#captura toda la pantalla
        ###screenshot = pyautogui.screenshot(region=(640, 330, 1280, 780))#left,top, w,h

        ##x, y = pyautogui.locateCenterOnScreen('Táctica')#para capturar una pantalla especifica
        ##pyautogui.click(x, y)#ubicar coord apartir dle centro de la ventan anterior
        # Guardar imagen.
        ###screenshot.save("screenshot.png")
        #otra forma:
        z3 = "Laboratorio de Táctica por Alexander Narváez"
        my = pygetwindow.getWindowsWithTitle(z3)[0]
        # quarter of screen screensize
        x2, y2 = pyautogui.size()
        x2, y2 = int(str(x2)), int(str(y2))
        x3 = x2 // 2
        y3 = 815#y2 // 2
        my.resizeTo(x3, y3)
        # top-left
        my.moveTo(0, 0)
        my.activate()
        screenshot = pyautogui.screenshot(region=(0, 0, 1285, y3))#left,top, w,h#tomamos pantallazo de la ventana activa
        screenshot.save("screenshot.png")




    def salir(self):
        self.close()

    #def verStats(self):
        #super(MainWindow, self).__init__()


    # a continuación código para generar paleta de colores

    def sumarCorrectos(self):
        global correctos
        global fallidos
        if fallidos + correctos >=9:
            self.ui.btnOff.setEnabled(False)
            self.ui.btnOk.setEnabled(False)
        correctos += 1
        self.ui.lblCorrectos.setText( "Correctos " + str(correctos))
        y2.append(correctos)
        print(y2)

    def sumarFallidos(self):
        global fallidos
        global correctos
        if fallidos + correctos >=9:
            self.ui.btnOff.setEnabled(False)
            self.ui.btnOk.setEnabled(False)
        fallidos +=1
        self.ui.lblFalls.setText( "Fallidos " + str(fallidos))
        y2.append(0)
        print(y2)

#vamos ahora con le código para la ventana de gráficas estafísticas
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('mainwindow.ui', self)
        #vamos cn la gráphic statics
        #self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])
        #self.plot(y2) #invocmos la grafica




    def plot(self):
        # create plot
        plt = pg.plot()
        plt.showGrid(x=True, y=True)
        plt.addLegend()

        # set properties
        plt.setLabel('left', 'Ejercicios (2 unidades x ejercicio)', units='V')
        plt.setLabel('bottom', 'Aciertos y Fallidos', units='1 unidad x ejercicio')
        plt.setXRange(0, 10)
        plt.setYRange(0, 20)#Acierto   plt.setYRange(0, 20)
        plt.setWindowTitle('Estadísticas de ejercicios realizados - Tactical Chess Por Alexander Narváez')

        # plot
        c1 = plt.plot(x, y, pen='b', symbol='x', symbolPen='b', symbolBrush=0.2, name='Umbral a conseguir.')
        c2 = plt.plot(x, y2, pen='r', symbol='o', symbolPen='r', symbolBrush=0.2, name='Aciertos')
        #self.graphWidget.plot(hour, temperature)



    def mostrar(self):
        app = QtWidgets.QApplication(sys.argv)
        main = MainWindow()
        main.show()
        sys.exit(app.exec_())




if __name__ == "__main__":
    app = QApplication(sys.argv)
    import sys

    #if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        # app.setWindowIcon(QIcon("./images/cartoon1.ico"))
    main = Ventanal()
    main.show()
    sys.exit(app.exec_())
