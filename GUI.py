import PyQt5.QtWidgets as qtw
from PyQt5 import QtGui as g
from PyQt5.QtCore import *
import mysql.connector
import qdarkstyle
from threading import Thread as thr
import pandas as pd
import time
import sqlite3

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
        test_l = qtw.QLabel('&Test:')
        test_l.setBuddy(self.testchoose)
        #add the widgets to the topboxlayout
        topboxlayout.addWidget(test_l)
        topboxlayout.addWidget(self.testchoose)

        ##Start/Stop Buttons
        #define the start/stop widgets
        self.startbutton = qtw.QPushButton("Start Test", clicked = lambda: self.create_event_thread(self.test_start))
        #add the widgets to the leftbuttonlayout
        leftbuttonlayout.addWidget(self.startbutton)
        
        ##Force/Displ Display
        #define the display widgets
        self.forcereading = qtw.QLabel('0.0')
        self.forcebutton = qtw.QPushButton("Display Force",  clicked = lambda: self.create_event_thread(self.display_force))

        self.initializebutton = qtw.QPushButton("Zero Force Initialization",  clicked = lambda: self.create_event_thread(self.initialize))
        
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
        self.movebutton = qtw.QPushButton("Move", clicked = lambda: self.create_event_thread(self.move))
        self.homebutton = qtw.QPushButton("Retract Home", clicked = lambda: self.create_event_thread(self.home))
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
        self.firmness_calc = qtw.QLabel('')
        firmness_label = qtw.QLabel("Firmness (N):")
        self.enterbutton = qtw.QPushButton("Record Results", clicked = self.commit)
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
        self.tab1hbox.addWidget(firmness_label, 2, 2)
        self.tab1hbox.addWidget(self.firmness_calc, 2, 3)
        self.tab1hbox.addWidget(self.enterbutton, 3, 3)
        self.tab1hbox.addWidget(self.thinking, 3,0,1,3)
        
        ## Tab2
        self.table = qtw.QTableWidget(10, 10)
        self.table.setAlternatingRowColors(True)
        #define back end widgets
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(self.table)
        try:
            conn = sqlite3.connect('foam_local.db')
        except:
            warning_box('Database Not Connected', 'Database Error')
            conn = None
        else:
            cur = conn.cursor()
            cur.execute("""select * from tests_local order by test_id desc""")
            df = cur.fetchall()
            self.table.setHorizontalHeaderLabels(["Test ID", "Test Name", "Result", "Date", "Operator", "Thickness", "Sample ID"])
            for i, row in enumerate(df):
                for j, x in enumerate(row):
                    tableItem = qtw.QTableWidgetItem(str(x))
                    self.table.setItem(i, j, tableItem)
    
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

    def create_event_thread(self, test_funct):
        self.thinking.setRange(0,0)
        self.click_all()
        a = events.MCR()
        if a.failout:
            warning_box("Check USB Connection", "Serial Connection Failure")
            return
        else:
            if test_funct == self.move:
                if not self.distance.text() or not self.speed.text():
                    warning_box("Indicate speed/distance to move", "Requires Entry")
                    self.unclick_all()
                    self.thinking.setRange(0,1)
                    a.conn.close()
                    return
                else: pass
            if test_funct == self.test_start:
                if self.testchoose.currentIndex() == 0:
                    warning_box("Please select a test", "No test selected")
                    self.unclick_all()
                    self.thinking.setRange(0,1)
                    a.conn.close()
                    return
                if not self.th_entry.text():
                    warning_box("Please enter a sample thickness", "Sample thickness required")
                    self.unclick_all()
                    self.thinking.setRange(0,1)
                    a.conn.close()
                    return
                else: pass
            thread_initialize=thr(target = test_funct, args = (a,))
            thread_initialize.start()

    def create_serial_read_thread(self, a, waiting_function):
        read_thread=thr(target = waiting_function, args=(a,))
        read_thread.setDaemon(True)
        read_thread.start()

    def serial_wait(self, a):
        while a.conn.in_waiting == 0:
            pass
        if self.another_step == True:
            self.selected_test(a)
        self.unclick_all()
        self.thinking.setRange(0,1)
        a.conn.close()
        return
    
    def initialize(self, a):
        time.sleep(2)
        self.another_step = False
        self.tare = a.zero_scale()
        print(self.tare)
        if int(self.tare) < -46000 or int(self.tare) > -42000:
            self.movebutton.setEnabled(True)
            self.initializebutton.setText("CLEAR LOAD")
            a.conn.close()
            self.thinking.setRange(0,1)
        else:
            a.conn.close()
            self.unclick_all()
            self.initializebutton.setEnabled(False)
            self.initializebutton.setText('Test Pin Ready')
            self.thinking.setRange(0,1)

    def display_force(self, a):
        time.sleep(2)
        offset = self.tare
        for _ in range(2):
            force = float(a.read(offset)) - a.perm_offset
        self.forcereading.setText(str(round(force, 1)))
        a.conn.close()
        self.unclick_all()
        self.thinking.setRange(0,1)

    def move(self, a):
        self.click_all()
        self.thinking.setRange(0,0)
        time.sleep(2)
        if self.extendbox.isChecked():
            pin_number = a.extend
        elif self.retractbox.isChecked():
            pin_number = a.retract
        travel = self.distance.text()
        speed = (float(self.speed.text())/100)*255  ###Conversion to pwm cycle
        self.create_serial_read_thread(a, self.serial_wait)
        a.go_the_distance(pin_number, travel, speed)
        return

    def home(self, a):
        time.sleep(2)
        self.create_serial_read_thread(a, self.serial_wait)
        a.go_home()

    def test_start(self, a):
        choice = self.testchoose.currentIndex()
        if choice == 0:
            warning_box("Please select a test", "No test selected")
        elif choice == 1:
            self.selected_test = self.support_move
            self.force_stop(a)
        elif choice == 2:
            self.selected_test = self.firmness_read
            self.force_stop(a)

    def force_stop(self, a):
        time.sleep(2)
        self.tare = a.zero_scale()
        self.two_five_distance = round(0.25*float(self.th_entry.text()), 2)
        self.fourty_distance = round(0.4*float(self.th_entry.text()), 2)
        self.another_step = True
        self.create_serial_read_thread(a, self.serial_wait)
        a.force_stop(self.two_five_distance)

    def firmness_read(self, a):
        for _ in range(2):
            self.two_five_force = float(a.read(self.tare)) - a.perm_offset
        self.firmness_calc.setText(str(round(self.two_five_force, 1)))
        self.another_step = False
        a.go_the_distance(a.retract, (self.fourty_distance*5), 255)
        self.unclick_all()
        self.thinking.setRange(0,1)
        a.conn.close()
        return
    
    def support_move(self, a):
        for _ in range(2):
            self.two_five_force = float(a.read(self.tare)) - a.perm_offset
        self.firmness_calc.setText(str(round(self.two_five_force, 1)))
        self.another_step = False
        a.go_the_distance(a.extend, self.fourty_distance, 255)
        time.sleep(a.default_pausetime)
        for _ in range(2):
            self.fourty_force = float(a.read(self.tare)) - a.perm_offset
        force = (float(self.fourty_force)-a.perm_offset)/(float(self.firmness_calc.text()))
        self.support_calc.setText((str(round(force, 3))))
        self.another_step = False
        a.go_the_distance(a.retract, (self.fourty_distance*5), 255)
        self.unclick_all()
        self.thinking.setRange(0,1)
        a.conn.close()
        return

    def commit(self):
        self.click_all()
        self.thinking.setRange(0,0)
        try:
            conn = sqlite3.connect('foam_local.db')
        except:
            warning_box('Database Not Connected', 'Database Error')
            conn = None
        else:
            c = conn.cursor()
            if not self.sampleID_entry.text() or not self.date_entry.text() or not self.operator_name.text() or not self.th_entry.text():
                warning_box("Fill out all data before submitting",  "Missing Data")
                c.close()
                self.unclick_all()
                self.thinking.setRange(0,1)
            else:
                sample_id = self.sampleID_entry.text()
                test_date = self.date_entry.text()
                operator = self.operator_name.text()
                thickness = self.th_entry.text()
                if self.firmness_calc.text():
                    test_name = 'firmness (N)'
                    entry = self.firmness_calc.text()
                    query = """INSERT INTO tests_local(sample_id, test_name_local,
                    result_local,test_date_local, operator_local, thickness_local) 
                    VALUES(?, ?, ?, ?, ?, ?);"""
                    c.execute(query, (sample_id, test_name, entry, test_date, operator, thickness))
                    self.firmness_calc.setText('')

                if self.support_calc.text():
                    test_name = 'support factor (N/N)'
                    entry = self.support_calc.text()
                    query = """INSERT INTO tests_local(sample_id, test_name_local,
                    result_local,test_date_local, operator_local, thickness_local) 
                    VALUES(?, ?, ?, ?, ?, ?);"""
                    c.execute(query, (sample_id, test_name, entry, test_date, operator, thickness))
                    self.support_calc.setText('')

                c.execute("""select * from tests_local order by test_id desc""")
                df = c.fetchall()
                self.table.setHorizontalHeaderLabels(["Test ID", "Test Name", "Result", "Date", "Operator", "Thickness", "Sample ID"])
                for i, row in enumerate(df):
                    for j, x in enumerate(row):
                        tableItem = qtw.QTableWidgetItem(str(x))
                        self.table.setItem(i, j, tableItem)
                c.close()
                self.unclick_all()
                self.thinking.setRange(0,1)
        return
        
    ########## Standardized question/warnings ###################
def question_box(question, window_title, click_function):
    commence = qtw.QMessageBox()
    commence.setIcon(qtw.QMessageBox.Question)
    commence.setText(question)
    commence.setWindowTitle(window_title)
    commence.setStandardButtons(qtw.QMessageBox.Yes | qtw.QMessageBox.No)
    commence.buttonClicked.connect(click_function)
    returnval = commence.exec()
    return

def warning_box(warning, window_title):
    commence = qtw.QMessageBox()
    commence.setIcon(qtw.QMessageBox.Warning)
    commence.setText(warning)
    commence.setWindowTitle(window_title)
    commence.setStandardButtons(qtw.QMessageBox.Ok)
    returnval = commence.exec()
    return
########################### Check Serial Connection ########################################################

if __name__ == '__main__':
    app = qtw.QApplication([])  ##Create QApplication instance
    UFT = MainWindow() ##Create Mainwindow (inherit from QtWidget) instance
    UFT.show()  ##Set the window logo
    app.exec_()  ##Initialize event loop




