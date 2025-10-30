# GlowClock PCB
This PCB was designed to, in addition to supporting the glowclock, be a modular prototyping board for various other projects as well, with all unused GPIO broken out and accessible.

V1.0 boards have been produced and are in active use, V1.1 boards are current in development.

## Errata
### V1.0
- The second motor-driver board slot (A2) is not fully populated with the required control signals
- The Raspberry Pi 40 pin header (not to be confused with the Pi Pico's socket) has 0.2mm hole spacing instead of the traditional 2.54mm spacing
- The i2c SDA pin for the I2C_LCD connector is connected to GPIO22 instead of GPIO20. This can be resolved by cutting the trace and green-wiring to the Pi Pico pin 26.
