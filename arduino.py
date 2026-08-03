import serial 
import time

class Arduino:

    def_init_(self, port, baudrate=115200)

    self.ser = serial.Serial(
        port, 
        baudrate, 
        timeout=1
    )

    time.sleep(2)

def send_command(self, command):

    self.ser.write(
        (command + "\n").encode()
    )

    def close(self):
        self.ser.close()