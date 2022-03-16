from threading import Thread as thr
import serial
import time

class MCR():
    def __init__(self, serial_port='COM3', baud_rate=9600, read_timeout = 5 ):
        """
        Initializes the serial connection to the Arduino board
        """
        self.extend = 11
        self.retract = 10
        self.perm_offset = 14.89
        self.default_forstop_newtons = 2

        try:
            self.conn = serial.Serial(serial_port, baud_rate)
            self.conn.timeout = read_timeout # Timeout for readline()
            self.failout = False
        
        except:
            self.failout = True

    def zero_scale(self):
        command = (''.join(('RT', str(0), ':', str(0)))).encode()
        self.conn.write(command)
        line_received = self.conn.readline().decode().strip()
        return line_received

    def read(self, offset):
        command = (''.join(('RF', str(0), ':', str(offset)))).encode()
        self.conn.write(command) 
        line_received = self.conn.readline().decode().strip()
        return line_received

    def go_the_distance(self, pin_number, distance, speedvalue):
        command = (''.join(('WG', str(pin_number), ':', str(distance),':', str(speedvalue)))).encode()
        self.conn.write(command)
        return

    def go_home(self):
        command = (''.join(('WH', str(0), ':', str(0)))).encode()
        self.conn.write(command)
        return

    def force_stop(self, offset):
        command = (''.join(('WF', str(0), ':', str(self.default_forstop_newtons), ':', str(offset)))).encode()
        self.conn.write(command)
        line_received = self.conn.readline().decode().strip()
        return line_received

