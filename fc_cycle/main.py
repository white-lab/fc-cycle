from __future__ import absolute_import, division

import argparse
import logging
import math
import ctypes
import serial
from serial import win32
import sys
import time

from fc_cycle import __version__

LOGGER = logging.getLogger("fc_cycle.main")

serial.XON = 0
serial.XOFF = 0


class HandleSerial(serial.Serial):
    def _reconfigure_port(self):
        super(HandleSerial, self)._reconfigure_port()

        comDCB = win32.DCB()
        win32.GetCommState(self._port_handle, ctypes.byref(comDCB))

        comDCB.fOutxCtsFlow = 0
        comDCB.fOutxDsrFlow = 0

        if not win32.SetCommState(self._port_handle, ctypes.byref(comDCB)):
                raise serial.SerialException(
                    'Cannot configure port, something went wrong. '
                    'Original message: {!r}'.format(ctypes.WinError()))

    def write_line(self, text):
        LOGGER.info("writing line: {}".format(repr(text)))
        run_command(self, text.encode())


def _open_serial(path):
    return HandleSerial(
        path,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,
        rtscts=True,
        dsrdtr=True,
        timeout=0.1,
        write_timeout=.1,
    )


def _get_serial(serial_name=None):
    if serial_name:
        return _open_serial(serial_name)

    excepts = []

    for path in [
        "COM5",
        "/dev/ttyUSB0",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
    ]:
        try:
            port = _open_serial(path)
        except serial.SerialException as e:
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


def run_command(port, message, id=61):
    to_write = (128 + id).to_bytes(1, byteorder='big')
    LOGGER.info("id: {}, message: {}".format(id, message))
    LOGGER.debug("w: {}".format(to_write))
    port.write(to_write)
    LOGGER.debug("r: {}".format(port.read(1)))
    win32.PurgeComm(port._port_handle, win32.PURGE_RXCLEAR)

    if len(message) > 1:
        to_write = b"\x0a"
        LOGGER.debug("w: {}".format(to_write))
        port.write(b"\x0a")
        LOGGER.debug("r: {}".format(port.read(1)))
        win32.PurgeComm(port._port_handle, win32.PURGE_RXCLEAR)

    for letter in message:
        LOGGER.debug("w: {}".format(letter.to_bytes(1, byteorder='big')))
        port.write(letter.to_bytes(1, byteorder='big'))
        LOGGER.debug("r: {}".format(port.read(1)))
        win32.PurgeComm(port._port_handle, win32.PURGE_RXCLEAR)

    if len(message) > 1:
        to_write = b"\x0d"
        LOGGER.debug("w: {}".format(to_write))
        port.write(to_write)
        LOGGER.debug("r: {}".format(port.read(1)))
        win32.PurgeComm(port._port_handle, win32.PURGE_RXCLEAR)

    while True:
        rep = port.read(1)
        if not rep:
            break
        rep = rep[0]
        LOGGER.debug("r: {}".format(rep.to_bytes(1, byteorder="big")))
        win32.PurgeComm(port._port_handle, win32.PURGE_RXCLEAR)

        to_write = b"\x06"
        LOGGER.debug("w: {}".format(to_write))
        port.write(to_write)
        if rep > 127:
            LOGGER.debug("break")
            break


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

    with _get_serial(serial_name) as ser:
        win32.PurgeComm(ser._port_handle, win32.PURGE_RXCLEAR)

        try:
            # Beep and display Hello World
            ser.write_line("%")
            ser.write_line("G010")
            ser.write_line("W0Hello")
            ser.write_line("W01World")
            ser.write_line("X000")
            ser.write_line("Y000")
            time.sleep(delay)

            # Cycle through each tube
            for i in range(math.ceil((total_time - delay) / tube_time)):
                ser.write_line("T{:03d}".format((i % max_tubes) + 1))
                time.sleep(tube_time)
        except KeyboardInterrupt as err:
            LOGGER.info("Closing connection")
        finally:
            # Reset the machine
            ser.write_line("X000")
            ser.write_line("Y000")


if __name__ == "__main__":
    main(sys.argv[1:])
