from pkgutil import extend_path
import PyQt5.QtWidgets as qtw
from PyQt5 import QtGui as g
from PyQt5.QtCore import *
import mysql.connector
import qdarkstyle
from threading import Thread as thr
import pandas as pd
import time

import firmware_communication as events

StyleSheet = '''
#BlueProgressBar {
    border: 2px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
}
'''

class MainWindow(qtw.QWidget):   ##Inherit QtWidget parent class
    def __init__(self):  ##Initialize instance
        super().__init__()  ##Initialize parent classs

        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setWindowIcon(g.QIcon('logo.png'))
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
        self.tab1hbox = qtw.QGridLayout()
        tab2hbox = qtw.QGridLayout()
        tab3hbox = qtw.QGridLayout()
        tab1.setLayout(self.tab1hbox)
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
        self.startbutton = qtw.QPushButton("Start Test", clicked = lambda: self.create_thread(self.test_start))
        #add the widgets to the leftbuttonlayout
        leftbuttonlayout.addWidget(self.startbutton)
        
        ##Force/Displ Display
        #define the display widgets
        self.forcereading = qtw.QLabel('0.0')
        self.forcebutton = qtw.QPushButton("Display Force",  clicked = lambda: self.create_thread(self.display_force))

        self.initializebutton = qtw.QPushButton("Zero Force Initialization",  clicked = lambda: self.create_thread(self.initialize))
        
        #add the widgets to the displaylayout
        displaylayout.addWidget(self.forcebutton, 0, 0)
        displaylayout.addWidget(self.forcereading, 0, 1)
        displaylayout.addWidget(self.initializebutton, 1, 0)

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
        self.movebutton = qtw.QPushButton("Move", clicked = lambda: self.create_thread(self.move))
        self.homebutton = qtw.QPushButton("Retract Home", clicked = lambda: self.create_thread(self.home))
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
        self.thinking = qtw.QProgressBar(self, textVisible=False, objectName = "BlueProgressBar")
    
        #define tab layout
        self.tab1hbox.addWidget(operator_label, 0, 0)
        self.tab1hbox.addWidget(self.operator_name, 0, 1)
        self.tab1hbox.addWidget(date_label, 1, 0)
        self.tab1hbox.addWidget(self.date_entry, 1, 1)
        self.tab1hbox.addWidget(sampleID_label, 2, 0)
        self.tab1hbox.addWidget(self.sampleID_entry, 2, 1)
        self.tab1hbox.addWidget(th_label, 0, 2)
        self.tab1hbox.addWidget(self.th_entry, 0, 3)
        self.tab1hbox.addWidget(support_label, 1, 2)
        self.tab1hbox.addWidget(self.support_calc, 1, 3)
        self.tab1hbox.addWidget(firmness_l_label, 2, 2)
        self.tab1hbox.addWidget(self.firmness_l_calc, 2, 3)
        self.tab1hbox.addWidget(self.enterbutton, 3, 3)
        self.tab1hbox.addWidget(self.thinking, 3,0,1,3)
        
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
    
        #add tabs to widget
        self.entryfields.addTab(tab1, "&Test Results")
        self.entryfields.addTab(tab2, "Results Database")
        # self.entryfields.addTab(tab3, "Device Calibration")
    
        ######## Add Sublayouts to MainLayout ########
        mainlayout.addLayout(topboxlayout, 0, 0)
        mainlayout.addLayout(leftbuttonlayout, 1, 0)
        mainlayout.addLayout(displaylayout, 2, 0)

        mainlayout.addLayout(radiobuttonlayout, 0, 1)
        mainlayout.addLayout(displacementlayout, 1, 1)
        mainlayout.addLayout(buttonlayout, 2, 1)
        mainlayout.addWidget(self.entryfields, 3, 0, 1, 2)

        self.click_all()

    def click_all(self):
        self.forcebutton.setEnabled(False)
        self.startbutton.setEnabled(False)
        self.movebutton.setEnabled(False) 
        self.homebutton.setEnabled(False)
        self.enterbutton.setEnabled(False)


    def unclick_all(self):
        self.forcebutton.setEnabled(True)
        self.startbutton.setEnabled(True)
        self.movebutton.setEnabled(True) 
        self.homebutton.setEnabled(True)
        self.enterbutton.setEnabled(True)

    def create_thread(self, test_funct):
        thread_initialize=thr(target = test_funct)
        thread_initialize.start()
    
    def waiting_loop(self, a):
        while a.conn.in_waiting == 0:
            pass
        self.unclick_all()
        self.thinking.setRange(0,1)
        a.conn.close()
        return
    
    def initialize(self):
        self.thinking.setRange(0,0)
        a = events.MCR()
        if a.failout:
            self.warning_box("Check USB Connection", "Serial Connection Failure")
        elif a.failout == False:
            time.sleep(2)
            self.tare = a.zero_scale()
            if int(self.tare) < -46000 or int(self.tare) > -42000:
                self.warning_box('Force Cell Requires Calibration', 'Maintenance Required')
            else:
                a.conn.close()
                self.unclick_all()
                self.initializebutton.setEnabled(False)
                self.initializebutton.setText('Test Pin Ready')
                self.thinking.setRange(0,1)

    def display_force(self):
        self.thinking.setRange(0,0)
        a = events.MCR()
        if a.failout:
            self.warning_box("Check USB Connection", "Serial Connection Failure")
        elif a.failout == False:
            time.sleep(2)
            offset = self.tare
            for _ in range(4):
                force = float(a.read(offset)) - a.perm_offset
            self.forcereading.setText(str(round(force, 1)))
            a.conn.close()
            self.unclick_all()
            self.thinking.setRange(0,1)

    def move(self):
        self.click_all()
        self.thinking.setRange(0,0)
        a = events.MCR()
        if a.failout:
            self.warning_box("Check USB Connection", "Serial Connection Failure")
        elif a.failout == False:
            if not self.distance.text() or not self.speed.text():
                self.warning_box("Indicate speed/distance to move", "Requires Entry")
            else:
                time.sleep(2)

                read_thread=thr(target = self.waiting_loop, args=(a,))
                read_thread.setDaemon(True)
                read_thread.start()

                if self.extendbox.isChecked():
                    pin_number = a.extend
                elif self.retractbox.isChecked():
                    pin_number = a.retract

                travel = self.distance.text()
                speed = (float(self.speed.text())/100)*255  ###Conversion to pwm cycle
                a.go_the_distance(pin_number, travel, speed)
                return

    def home(self):
        self.click_all()
        self.thinking.setRange(0,0)
        a = events.MCR()
        if a.failout:
            self.warning_box("Check USB Connection", "Serial Connection Failure")
        elif a.failout == False:
            time.sleep(2)
            a.go_home()
            a.conn.close()
            self.unclick_all()
            self.thinking.setRange(0,1)

    def test_start(self):
        choice = self.testchoose.currentIndex()
        if choice == 0:
            self.warning_box("Please select a test", "No test selected")
        elif choice == 1:
            self.selected_test = self.firmness_support
            self.create_thread(self.force_stop(self.selected_test))
        elif choice == 2:
            self.selected_test = self.firmness
            self.create_thread(self.force_stop(self.selected_test))
        elif choice == 3:
            self.selected_test = self.support
            self.create_thread(self.force_stop(self.selected_test))

    def force_stop(self, selected_test):
        self.click_all()
        self.thinking.setRange(0,0)
        a = events.MCR()
        if a.failout:
            self.warning_box("Check USB Connection", "Serial Connection Failure")
        elif a.failout == False:
            time.sleep(2)
            if not self.th_entry.text():
                self.warning_box("Please enter a sample thickness", "Sample thickness required")
                a.conn.close()
                self.unclick_all()
                self.thinking.setRange(0,1)
            else:
                self.tare = a.zero_scale()
                a.force_stop(self.tare)
                while True:
                    print(a.conn.in_waiting)
                
    def firmness_support(self):
        print('firmness and support test')



    


    ########## Standardized question/warnings ###################
    def question_box(self,question, window_title, click_function):
        commence = qtw.QMessageBox()
        commence.setIcon(qtw.QMessageBox.Question)
        commence.setText(question)
        commence.setWindowTitle(window_title)
        commence.setStandardButtons(qtw.QMessageBox.Yes | qtw.QMessageBox.No)
        commence.buttonClicked.connect(click_function)
        returnval = commence.exec()
        return(returnval)

    def warning_box(self,warning, window_title):
        commence = qtw.QMessageBox()
        commence.setIcon(qtw.QMessageBox.Warning)
        commence.setText(warning)
        commence.setWindowTitle(window_title)
        commence.setStandardButtons(qtw.QMessageBox.Ok)
        returnval = commence.exec()
        return(returnval)


########################### Check Serial Connection ########################################################


if __name__ == '__main__':
    app = qtw.QApplication([])  ##Create QApplication instance
    UFT = MainWindow() ##Create Mainwindow (inherit from QtWidget) instance
    UFT.show()  ##Set the window logo
    app.exec_()  ##Initialize event loop




