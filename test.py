#######################################################################################################################
import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class PIDS_Command_Controller_GUI(QMainWindow):
    def __init__(self,UserAccLevel):
        super(PIDS_Command_Controller_GUI, self).__init__()
        self.UserAccessLevel = UserAccLevel

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.red)
        painter.setBrush(Qt.white)
        painter.drawLine(0, 0, 300, 300)

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = PIDS_Command_Controller_GUI('Admin')
    window.showMaximized()
    sys.exit(App.exec())
    ####################################################################################################################