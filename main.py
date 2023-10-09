import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import Qt
from tactical import *
class Principal(QMainWindow):
    def __init__(self):
        super(Principal, self).__init__()

        lbl = Qt.QLabel('Laboratorio de Táctica por Aexander Narváez!!', self)
        lbl.setStyleSheet("""QLabel{
          font-family:'Consolas'; 
          color: red; 
          font-size: 26px;}""")
        lbl.setGeometry(7, 20, 900, 30)


        self.setAttribute(Qt.Qt.WA_TranslucentBackground, True )   
        self.setAttribute(Qt.Qt.WA_NoSystemBackground, False)      
        self.setWindowFlags(Qt.Qt.FramelessWindowHint)

        self.setStyleSheet("Principal{background-color: rgba(0, 215, 55, 70);}") 


  #El valor de 20 es el filtro alfa para la transparencia pero no funciona

        self.boton1 = Qt.QPushButton("Quit", self)
        self.boton1.setAutoFillBackground(False)
        self.boton1.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.988818, y1:0.915, x2:0, y2:0, stop:0 rgba(53, 129, 90, 255), stop:1 rgba(255, 255, 255, 255));\n"
"font: 75 16pt \"Georgia\";")
        self.boton1.setGeometry(225, 170, 150, 150)
        self.boton1.clicked.connect(self.close)
        self.setGeometry(350,150,600,400)

app = QApplication(sys.argv)
p = Principal()
p.show()
app.exec_()