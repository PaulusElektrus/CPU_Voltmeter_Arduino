# Psutil for retrieving CPU Usage
import psutil
# Pyfirmata to communicate with Arduino (StandardFirmata)
import pyfirmata
import time

def main():
    # Specify COM Port
    board = pyfirmata.Arduino('COM3')

    # Set up Arduino loop
    it = pyfirmata.util.Iterator(board)
    it.start()

    # Set up Digital Pin 9 as PWM Output
    analog = board.get_pin('d:9:p')

    while True:
        cpu_percentage = psutil.cpu_percent()
        # Convert it to 0-1 value
        cpu_value = cpu_percentage/100
        # Neutral value that it looks better
        if cpu_value < 0.04:
            cpu_value = 0.03
        # Writing value to Arduino via Serial
        analog.write(cpu_value)
        # Refresh Time in Seconds
        time.sleep(0.5)

if __name__ == "__main__":
    main()