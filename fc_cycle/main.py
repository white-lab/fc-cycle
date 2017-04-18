
from __future__ import absolute_import

import argparse
import logging
import math
import serial
import serial.threaded
import sys
import time
import traceback

from fc_cycle import __version__

LOGGER = logging.getLogger("fc_cycle.main")


class HandleSerial(serial.threaded.LineReader):
    def connection_made(self, transport):
        super(HandleSerial, self).connection_made(transport)
        LOGGER.info('port opened')

    def handle_packet(self, data):
        LOGGER.debug("received packet: {}".format(repr(data)))
        super(HandleSerial, self).handle_packet(data)

    def handle_line(self, data):
        LOGGER.info("received line: {}".format(repr(data)))

    def write_line(self, text):
        LOGGER.info("writing line: {}".format(repr(text)))
        super(HandleSerial, self).write_line(text)

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        LOGGER.info('port closed')


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
            port = serial.Serial(
                path,
                baudrate=19200,  # 9600?
                parity=serial.PARITY_EVEN,  # PARITY_NONE?
                stopbits=serial.STOPBITS_ONE,
            )
        except serial.serialutil.SerialException as e:
            excepts.append(e)
            continue
        else:
            return port

    raise Exception("Unable to find any valid serial ports", excepts)


def _parse_args(args):
    """
    Parses arguments from a argv format.

    Parameters
    ----------
    args : list of str

    Returns
    -------
    argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="FC-Cycle",
        description="Utility for collecting fraction in a cycle on the Gilson "
        "FC 204 Fraction Collector.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        help="Increase verbosity of output.",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="count",
        help="Decrease verbosity of output.",
    )
    parser.add_argument(
        '-V', '--version',
        action="version",
        version="%(prog)s {}".format(__version__),
    )
    return parser, parser.parse_args(args)


def _set_verbosity(args):
    verbosity = (args.verbose or 0) - (args.quiet or 0)

    if verbosity <= -2:
        level = logging.CRITICAL
    elif verbosity == -2:
        level = logging.ERROR
    elif verbosity == -1:
        level = logging.WARNING
    elif verbosity == 0:
        level = logging.INFO
    elif verbosity > 0:
        level = logging.DEBUG

    logger = logging.getLogger('fc_cycle')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = logging.FileHandler('fc_cycle.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    LOGGER.debug(sys.argv)
    LOGGER.debug(args)


def main(args):
    _, args = _parse_args(args)
    _set_verbosity(args)

    serial_name = input("Serial Port Name (optional): ")
    max_tubes = int(input("Max Tubes (default: 20): ") or 20)
    delay = int(input("Delay in Minutes (default: 5): ") or 5)
    total_time = int(input("Total Time in Minutes (default: 85): ") or 85)
    tube_time = int(input("Time per tube in Seconds (default: 60): ") or 60)

    total_time *= 60
    delay *= 60

    with serial.ReaderThread(
        _get_serial(serial_name),
        HandleSerial,
    ) as ser:
        try:
            # Beep and display Hello World
            ser.write_line("G010")
            ser.write_line("W0Hello")
            ser.write_line("W01World")
            ser.write_line("V1")
            time.sleep(delay)
            ser.write_line("V0")

            # Cycle through each tube
            for i in range(math.ceil((total_time - delay) / tube_time)):
                ser.write_line("T{:03d}".format((i % max_tubes) + 1))
                time.sleep(tube_time)
        except KeyboardInterrupt as err:
            LOGGER.info("Closing connection")
        finally:
            # Reset the machine
            ser.write_line("V1")
            time.sleep(10)
            ser.write_line("$")
            ser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
