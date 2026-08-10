import serial

arduino = serial.Serial(
    port="COM10", #change if needed
    baudrate=115200,
    timeout=1
)

print("Listening for pedal presses...")

while True:

    line = arduino.readline().decode().strip()

    if line:
        print(line)