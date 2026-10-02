#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient
import time

client = ModbusSerialClient(port="/dev/ttyUSB0", baudrate=9600, timeout=1)

loop = False
relayTest = True
relayState = 0xff00

def testBatch():
    if relayTest:
        for channel in range(7):
            result = client.write_coil(channel, relayState)
            print(f"Write {relayState} to Relay CH{channel}")
            print(result)
    print("~~~")

if loop:
    while True:
        testBatch()
        time.sleep(2)
else:
    testBatch()
