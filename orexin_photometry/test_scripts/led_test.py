import serial 
import time 

arduino = serial.Serial(
    port="COM10", 
    baudrate=115200,
    timeout=1
)

#Allow Arduino to initialise
time.sleep(2)

print("Turning LED on...")
arduino.write(b"ON\n")

time.sleep(2)

print("Turning LED off...")
arduino.write(b"OFF\n")

arduino.close()
