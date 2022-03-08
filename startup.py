from PyQt5.QtWidgets import QWidget as qw
from PyQt5 import QtGui as qg
from PyQt5.QtWidgets import QMessageBox as qm
import qdarkstyle

import GUI


class Startup(qw):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        commence = qm()
        commence.setIcon(qm.Question)
        commence.setText("Is the test pin clear of all obstructions for zero force initialization?")
        commence.setWindowTitle("Load Cell Initializing")
        commence.setStandardButtons(qm.Yes | qm.No)
        commence.buttonClicked.connect(self.startup)
        commence.exec()

    def startup(self, i):
        if i.text() == 'OK':
            GUI()
        else:
            'not clear'
            quit()


        




if __name__ == '__main__':
        
    app = qtw.QApplication([])
    Startup = Startup()
    Startup.setWindowIcon(g.QIcon('logo.png'))
    app.exec_()