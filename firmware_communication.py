from threading import Thread as thr
import serial
import time

class MCR():
    def __init__(self, serial_port='COM3', baud_rate=9600, read_timeout = 5 ):
        """
        Initializes the serial connection to the Arduino board
        """
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


