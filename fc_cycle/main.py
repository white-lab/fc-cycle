
import logging
import math
import serial
import sys
import time

LOGGER = logging.getLogger("fc_cycle.main")


class SerialWrapper(object):
    def __init__(self, f, encode_bytes=True):
        self.f = f
        self.encode_bytes = encode_bytes

    def write(self, b):
        LOGGER.debug("Write:", b)

        if not isinstance(b, bytes) and self.encode_bytes:
            b = b.encode()

        return self.f.write(b)

    def writeline(self, b):
        if not isinstance(b, bytes) and self.encode_bytes:
            b = b.encode() + b"\n"
        else:
            b = b + "\n"

        return self.write(b)

    def read(self):
        b = self.f.read()
        LOGGER.debug("Read:", b)
        return b

    def close(self):
        return self.f.close()

    def __enter__(self):
        self.f.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        return self.f.__exit__(*args, **kwargs)


def _get_serial(serial_name=None):
    if serial_name:
        return serial.Serial(serial_name)

    excepts = []

    for path in [
        "/dev/ttyUSB0",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
    ]:
        try:
            port = serial.Serial(path)
        except serial.serialutil.SerialException as e:
            excepts.append(e)
            continue
        else:
            return port

    return sys.stdout

    raise Exception("Unable to find any valid serial ports", excepts)


def main(args):
    serial_name = input("Serial Port Name (optional): ")
    max_tubes = int(input("Max Tubes (default: 20): ") or 20)
    delay = int(input("Delay in Minutes (default: 5): ") or 5)
    total_time = int(input("Total Time in Minutes (default: 85): ") or 85)
    tube_time = int(input("Time per tube in Seconds (default: 60): ") or 60)

    total_time *= 60
    delay *= 60

    with SerialWrapper(_get_serial(serial_name)) as ser:
        # Beep and display Hello World
        ser.writeline("G010")
        ser.writeline("W0Hello")
        ser.writeline("W01World")
        ser.writeline("V1")
        time.sleep(delay)
        ser.writeline("V0")

        # Cycle through each tube
        for i in range(math.ceil((total_time - delay) / tube_time)):
            ser.writeline("T{:03d}".format((i % max_tubes) + 1))
            time.sleep(tube_time)

        # Reset the machine
        ser.writeline("V1")
        time.sleep(10)
        ser.writeline("$")


if __name__ == "__main__":
    main(sys.argv[1:])
