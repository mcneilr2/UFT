import PyQt5.QtWidgets as qtw
from PyQt5 import QtGui as g
from PyQt5.QtCore import *
import mysql.connector
import qdarkstyle
import threading
import pandas as pd

import ui_event_management as events

## Force user to clear the cell for zero-force initialization
def EnforcePinClearWindow():
        dialog = qtw.QDialog()
        ##Main layout
        mainlayout = qtw.QGridLayout()
        dialog.setLayout(mainlayout)
        dialog.setWindowTitle("Clear Testing Pin")
        dialog.setGeometry(500,500,300,200)
        dialog.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        ##Sub layouts
        radiobuttonlayout = qtw.QHBoxLayout()
        displacementlayout = qtw.QFormLayout()
        buttonlayout = qtw.QVBoxLayout()
        
        ##Extend/Retract Radio Buttons
        extendbox = qtw.QRadioButton("Extend")
        retractbox = qtw.QRadioButton("Retract")
        extendbox.setChecked(True)
        radiobuttonlayout.addWidget(extendbox)
        radiobuttonlayout.addWidget(retractbox)
        
        ##Distance/Speed Fields
        distance = qtw.QLineEdit()
        distancelabel = qtw.QLabel("Displacement (mm):")
        speed = qtw.QLineEdit()
        speedlabel = qtw.QLabel("Speed (%):")
        displacementlayout.addRow(distancelabel, distance)
        displacementlayout.addRow(speedlabel, speed)

        movebutton = qtw.QPushButton("Move", clicked = lambda: events.th_move())
        homebutton = qtw.QPushButton("Retract Home", clicked = lambda: events.th_home())
        clearbutton = qtw.QPushButton("Enter", clicked = startup_question)
        buttonlayout.addWidget(movebutton)
        buttonlayout.addWidget(homebutton)
        buttonlayout.addWidget(clearbutton)

        mainlayout.addLayout(radiobuttonlayout, 0, 0)
        mainlayout.addLayout(displacementlayout, 1, 0)
        mainlayout.addLayout(buttonlayout, 2, 0)

        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()
class MainWindow(qtw.QWidget):   ##Inherit QtWidget parent class
    def __init__(self):  ##Initialize instance
        super().__init__()  ##Initialize parent classs
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        ######## Layout Management ########
        #set main layout
        mainlayout = qtw.QGridLayout()
        self.setLayout(mainlayout)
        self.setWindowTitle("Universal Foam Tester")
        #setup sublayouts
        topboxlayout = qtw.QHBoxLayout()
        leftbuttonlayout = qtw.QVBoxLayout()
        displaylayout = qtw.QGridLayout()
        radiobuttonlayout = qtw.QHBoxLayout()
        displacementlayout = qtw.QFormLayout()
        buttonlayout = qtw.QVBoxLayout()

        self.entryfields = qtw.QTabWidget()
        tab1 = qtw.QWidget()
        tab2 = qtw.QWidget()
        tab3 = qtw.QWidget()
        tab1hbox = qtw.QGridLayout()
        tab2hbox = qtw.QGridLayout()
        tab3hbox = qtw.QGridLayout()
        tab1.setLayout(tab1hbox)
        tab2.setLayout(tab2hbox)
        tab3.setLayout(tab3hbox)

        ######## Define Sublayouts ########

        ##Test Selection
        #define the test selection
        self.testchoose = qtw.QComboBox()
        self.testchoose.addItem("Choose Test")
        self.testchoose.addItem("Support Factor +  Firmness")
        self.testchoose.addItem("Firmness")
        self.testchoose.addItem("Support Factor")
        # self.testchoose.addItem("Support Factor")
        # self.testchoose.addItem("Hysteresis")
        test_l = qtw.QLabel('&Test:')
        test_l.setBuddy(self.testchoose)
        #add the widgets to the topboxlayout
        topboxlayout.addWidget(test_l)
        topboxlayout.addWidget(self.testchoose)

        ##Start/Stop Buttons
        #define the start/stop widgets
        self.startbutton = qtw.QPushButton("Start Test", clicked = lambda: events.th_test_initiate())
        #add the widgets to the leftbuttonlayout
        leftbuttonlayout.addWidget(self.startbutton)
        
        ##Force/Displ Display
        #define the display widgets
        self.forcereading = qtw.QLabel('0.0')
        self.forcebutton = qtw.QPushButton("Display Force",  clicked = lambda: events.th_display_force())
        
        #add the widgets to the displaylayout
        displaylayout.addWidget(self.forcebutton, 0, 0)
        displaylayout.addWidget(self.forcereading, 0, 1)

        ##Extend/Retract Radio Buttons
        #define the radiobutton widgets
        self.extendbox = qtw.QRadioButton("Extend")
        self.retractbox = qtw.QRadioButton("Retract")
        self.extendbox.setChecked(True)
        #add the widgets to the radiobuttonlayout
        radiobuttonlayout.addWidget(self.extendbox)
        radiobuttonlayout.addWidget(self.retractbox)
        
        ##Displacement Entry
        #define the entry field widgets
        self.distance = qtw.QLineEdit()
        distancelabel = qtw.QLabel("Displacement (mm):")
        self.speed = qtw.QLineEdit()
        speedlabel = qtw.QLabel("Speed (%):")
        #add widgets to displacementlayout
        displacementlayout.addRow(distancelabel, self.distance)
        displacementlayout.addRow(speedlabel, self.speed)

        ##Move Button
        #define move button
        self.movebutton = qtw.QPushButton("Move", clicked = lambda: events.th_move())
        self.homebutton = qtw.QPushButton("Retract Home", clicked = lambda: events.th_home())
        buttonlayout.addWidget(self.movebutton)
        buttonlayout.addWidget(self.homebutton)

        ## Tab1
        #define entry widgets for test tab
        operator_label = qtw.QLabel("Operator Name:")
        self.operator_name = qtw.QLineEdit()
        self.date_entry = qtw.QLineEdit()
        date_label = qtw.QLabel("Date (yyyy-mm-dd):")
        self.sampleID_entry = qtw.QLineEdit()
        sampleID_label = qtw.QLabel("Sample ID:")
        self.th_entry = qtw.QLineEdit()
        th_label = qtw.QLabel("Thickness (mm):")
        self.support_calc = qtw.QLabel('')
        support_label = qtw.QLabel("Support Factor (N/N):")
        self.firmness_l_calc = qtw.QLabel('')
        firmness_l_label = qtw.QLabel("Firmness (N):")
        self.enterbutton = qtw.QPushButton("Record Results", clicked = lambda: events.th_commit())
        
        
        #define tab layout
        tab1hbox.addWidget(operator_label, 0, 0)
        tab1hbox.addWidget(self.operator_name, 0, 1)
        tab1hbox.addWidget(date_label, 1, 0)
        tab1hbox.addWidget(self.date_entry, 1, 1)
        tab1hbox.addWidget(sampleID_label, 2, 0)
        tab1hbox.addWidget(self.sampleID_entry, 2, 1)
        tab1hbox.addWidget(th_label, 0, 2)
        tab1hbox.addWidget(self.th_entry, 0, 3)
        tab1hbox.addWidget(support_label, 1, 2)
        tab1hbox.addWidget(self.support_calc, 1, 3)
        tab1hbox.addWidget(firmness_l_label, 2, 2)
        tab1hbox.addWidget(self.firmness_l_calc, 2, 3)
        tab1hbox.addWidget(self.enterbutton, 3, 3)
        
        ## Tab2
        self.table = qtw.QTableWidget(10, 10)
        self.table.setAlternatingRowColors(True)
        #define back end widgets
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(self.table)
        conn = mysql.connector.connect(host = 'localhost', user = 'root', passwd = 'password', database = 'foam')
        query = """select * from testing_results order by test_id desc"""
        df = pd.read_sql(query, conn)
        self.table.setHorizontalHeaderLabels(df.columns)
        for row in df.iterrows():
            values = row[1]
            for col_index, value in enumerate(values):
                tableItem = qtw.QTableWidgetItem(str(value))
                self.table.setItem(row[0], col_index, tableItem)

        ## Tab3
        #define entry widgets for test tab
        self.calibrate = qtw.QPushButton("Run Calibration", clicked = lambda: events.th_calibration())
        #define tab layout
        tab3hbox.addWidget(self.calibrate, 0,0)
    
        #add tabs to widget
        self.entryfields.addTab(tab1, "&Test Results")
        self.entryfields.addTab(tab2, "Results Database")
        self.entryfields.addTab(tab3, "Device Calibration")
    
        ######## Add Sublayouts to MainLayout ########
        mainlayout.addLayout(topboxlayout, 0, 0)
        mainlayout.addLayout(leftbuttonlayout, 1, 0)
        mainlayout.addLayout(displaylayout, 2, 0)

        mainlayout.addLayout(radiobuttonlayout, 0, 1)
        mainlayout.addLayout(displacementlayout, 1, 1)
        mainlayout.addLayout(buttonlayout, 2, 1)
        mainlayout.addWidget(self.entryfields, 3, 0, 1, 2)

    def click_all(self):
        self.forcebutton.setEnabled(False)
        self.startbutton.setEnabled(False)
        self.movebutton.setEnabled(False) 
        self.homebutton.setEnabled(False)
        self.enterbutton.setEnabled(False)

    def unclick_all(self):
        print('unclicking')
        self.forcebutton.setEnabled(True)
        self.startbutton.setEnabled(True)
        self.movebutton.setEnabled(True) 
        self.homebutton.setEnabled(True)
        self.enterbutton.setEnabled(True)

def startup_question():
    question = "Is the test pin clear for zero-force initialization?"
    window_title = "Force Cell Initialization"
    returnval = question_box(question, window_title, _)
    return returnval

def _():
    return

########## Standardized question/warnings and greying out functions ###################
def question_box(question, window_title, click_function):
    commence = qtw.QMessageBox()
    commence.setIcon(qtw.QMessageBox.Question)
    commence.setText(question)
    commence.setWindowTitle(window_title)
    commence.setStandardButtons(qtw.QMessageBox.Yes | qtw.QMessageBox.No)
    commence.buttonClicked.connect(click_function)
    returnval = commence.exec()
    return(returnval)

def warning_box(warning, window_title, click_function):
    commence = qtw.QMessageBox()
    commence.setIcon(qtw.QMessageBox.Warning)
    commence.setText(warning)
    commence.setWindowTitle(window_title)
    commence.setStandardButtons(qtw.QMessageBox.Ok)
    commence.buttonClicked.connect(click_function)
    returnval = commence.exec()
    return(returnval)

if __name__ == '__main__':
    app = qtw.QApplication([])  ##Create QApplication instance
    UFT = MainWindow()  ##Create Mainwindow (inherit from QtWidget) instance
    UFT.setWindowIcon(g.QIcon('logo.png'))  ##Set the window logo
    UFT.show()  ##Show the window
    clear = False
    check = startup_question()
    while clear == False:
        if check == 65536:
            EnforcePinClearWindow()
        elif check == 16384:
            clear = True ##Trigger initialize function
    app.exec_()  ##Initialize event loop




