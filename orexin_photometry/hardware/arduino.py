"""
arduino.py

Provides an interface between Python and the Arduino Uno R3

This module is responsible for sending commands to the Arduino,
which then controls sensory stimuli and TTL signals.
"""

#Import necessary modules
import serial 
import time

class Arduino: #Interface for communicating with Arduino

    def __init__(self, port, baudrate=115200):

        self.serial = serial.Serial(
        port, #Serial port assigned to Arduino (e.g. COM10)
        baudrate, #Serial communication speed
        timeout=1
    )
        #Give Arduino time to reboot after opening serial
        time.sleep(2)

    #Send a command string to the Arduino
    def send_command(self, command):

        self.serial.write(
        f"{command}\n".encode()
        )

    #Add trigger funtions for light and airpuff
    def trigger_light(self):
        self.send_command("LIGHT")

    def trigger_airpuff(self):
        self.send_command("AIRPUFF")

    #Read information about manual stimulations
    def read_message(self):

        if self.serial.in_waiting:

            return (
                self.serial.readline()
                .decode(errors="ignore")
                .strip()
            )
        return None

    #Close serial connection
    def close(self):
        self.serial.close()