# FC-Cycle

[![Build status](https://ci.appveyor.com/api/projects/status/615gjbnthy6cmtvi?svg=true)](https://ci.appveyor.com/project/naderm/fc-cycle)

Utility for collecting fraction in a cycle on the Gilson FC 204 Fraction Collector.

## Installation

To download a completely packaged Windows executable, visit our [releases page](https://github.com/white-lab/fc-cycler/releases). This software has only been tested on Windows as it required altering several serial flow control settings that require platform-dependent code.

## Hardware

In order to connect your computer to the FC 204, you will need a USB to RS-232 cable (We used a [TRENDnet USB to Serial Converter](https://www.amazon.com/TRENDnet-Converter-Prolific-Chipset-TU-S9/dp/B0007T27H8/)). For development of this program, we also used a Gilson GSIOC cable to connect the male end of the RS-232 to the male GSIOC port on the instrument. However, one may be able to use a more readily available DB9 female to female cable to connect the two male ports together.

No GSIOC to RS-232 Converter box, such as the Gilson 606, was required in order to successfully connect to the FC 204.

## Usage

To run the cycler, connect the FC 204 to your computer using a USB to Serial cable, double-click the executable, and fill out the short control options:

```
>FC-Cycle.exe
Serial Port Name (optional):
GSIOC ID (default 61):
Max Tubes (default: 20):
Delay in Minutes (default: 5):
Total Time in Minutes (default: 85):
Time per tube in Seconds (default: 60):
```
