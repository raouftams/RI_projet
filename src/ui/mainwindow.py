from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle("Projet RI")
        self.init_ui()
    
    def init_ui(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Hello World")
        self.label.move(100, 100)

        self.btn = QtWidgets.QPushButton(self)
        self.btn.setText("Quit")
        self.btn.move(100, 150)
        self.btn.clicked.connect(self.modify_label)

    def modify_label(self):
        self.label.setText("fuck off")
        self.update_label()

    def update_label(self):
        self.label.adjustSize()

def window():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    window()