from __future__ import absolute_import, division

import argparse
import logging
import math
import sys
import time

from fc_cycle import __version__, gsioc

LOGGER = logging.getLogger("fc_cycle.main")


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

    LOGGER.debug("Running FC-Cycle Version {}".format(__version__))

    serial_name = input("Serial Port Name (optional): ")
    gsioc_id = input("GSIOC ID (default 61): ")
    max_tubes = int(input("Max Tubes (default: 20): ") or 20)
    delay = int(input("Delay in Seconds (default: 600): ") or 600)
    total_time = int(input("Total Time in Minutes (default: 85): ") or 85)
    tube_time = int(input("Time per tube in Seconds (default: 60): ") or 60)

    total_time *= 60

    with gsioc.get_serial(serial_name, gsioc_id=gsioc_id) as ser:
        try:
            # Beep and display Hello World
            ser.write_line("%")
            ser.write_line("G010")
            ser.write_line("W0Hello")
            ser.write_line("W01World")

            if delay > 0:
                ser.write_line("X000")
                ser.write_line("Y000")
                time.sleep(delay)

            # Cycle through each tube
            total_tubes = math.ceil((total_time - delay) / tube_time)

            for i in range(total_tubes):
                tube_pos = (i % max_tubes) + 1

                LOGGER.info(
                    "Tube {} / {} (Position: {})"
                    .format(i + 1, total_tubes, tube_pos)
                )
                ser.write_line("T{:03d}".format(tube_pos))

                time.sleep(tube_time)
        except KeyboardInterrupt as err:
            LOGGER.info("Closing connection")
        finally:
            # Reset the machine
            ser.write_line("X000")
            ser.write_line("Y000")
            time.sleep(1)
            ser.write_line("X000")
            ser.write_line("Y000")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except:
        LOGGER.error("Execution error!", exc_info=True)
        input()
        sys.exit(1)
