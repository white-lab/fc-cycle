
import logging
import serial
import ctypes
from serial import win32


LOGGER = logging.getLogger("fc_cycle.gsioc")


class HandleSerial(serial.Serial):
    def __init__(self, *args, **kwargs):
        self.gsioc_id = kwargs.pop("gsioc_id", None) or 61
        super(HandleSerial, self).__init__(*args, **kwargs)

    def _reconfigure_port(self):
        super(HandleSerial, self)._reconfigure_port()

        comDCB = win32.DCB()
        win32.GetCommState(self._port_handle, ctypes.byref(comDCB))

        comDCB.fOutxCtsFlow = 0
        comDCB.fOutxDsrFlow = 0

        if not win32.SetCommState(self._port_handle, ctypes.byref(comDCB)):
            raise serial.SerialException(
                "Cannot configure port, something went wrong. "
                "Original message: {!r}".format(ctypes.WinError())
            )

        win32.PurgeComm(self._port_handle, win32.PURGE_RXCLEAR)

    def write_line(self, text):
        LOGGER.info("writing line: {}".format(repr(text)))
        run_command(self, text.encode(), gsioc_id=self.gsioc_id)


def run_command(port, message, gsioc_id=61):
    to_write = (128 + gsioc_id).to_bytes(1, byteorder='big')
    LOGGER.info("id: {}, message: {}".format(gsioc_id, message))
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


def _open_serial(path, gsioc_id=None):
    return HandleSerial(
        path,
        gsioc_id=gsioc_id,
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


def get_serial(serial_name=None, gsioc_id=None):
    if serial_name:
        return _open_serial(serial_name, gsioc_id=gsioc_id)

    excepts = []

    for path in [
        "COM5",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
    ]:
        try:
            port = _open_serial(path, gsioc_id=gsioc_id)
        except serial.SerialException as e:
            excepts.append(e)
            continue
        else:
            return port

    raise Exception("Unable to find any valid serial ports", excepts)
