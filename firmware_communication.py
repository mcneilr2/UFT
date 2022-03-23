import serial

class MCR():
    def __init__(self, serial_port='COM3', baud_rate=9600, read_timeout = 5 ):
        """
        Initializes the serial connection to the Arduino board
        """
        self.extend = 11
        self.retract = 10
        self.perm_offset = 14.9
        self.quarterspeed = 63.75
        self.default_forcestop = 2
        self.default_pausetime = 5

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

    def force_stop(self, two_five_distance):
        command = (''.join(('WF', str(0), ':',
            str(self.default_forcestop), ':', str(two_five_distance)))).encode()
        self.conn.write(command)
        print(command)
        return

    def support(self, fourty_distance, two_five_distance):
        command = (''.join(('WS', str(fourty_distance), ':',
            str(self.default_forcestop), ':', str(two_five_distance)))).encode()
        self.conn.write(command)
        print(command)
        return

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


