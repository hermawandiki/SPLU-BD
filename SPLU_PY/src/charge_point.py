from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import ChargePoint as cp

from src.modbus import turn_off_relay, turn_on_relay, all_relay_off
import asyncio
import RPi.GPIO as GPIO

pin1 = 36
pin2 = 38
pin3 = 40
pin4 = 33
pin5 = 35
pin6 = 37
emergency_pin = 29

pins = [pin1, pin2, pin3, pin4, pin5, pin6, emergency_pin]

currentTx = {
    'connected'     : [0, 0, 0, 0, 0, 0],
    'started'       : [0, 0, 0, 0, 0, 0],
    'txid'          : [0, 0, 0, 0, 0, 0],
    'txid_off'      : [0, 0, 0, 0, 0, 0],
    'idinterval'    : [0, 0, 0, 0, 0, 0],
    'token_id'      : [0, 0, 0, 0, 0, 0],
    'meter_start'   : [0, 0, 0, 0, 0, 0],
    'datetime_start': [0, 0, 0, 0, 0, 0],
    'meter_stop'    : [0, 0, 0, 0, 0, 0],
    'datetime_stop' : [0, 0, 0, 0, 0, 0]
}

CTRATIO = 4
token_pending = [0, 0, 0, 0, 0, 0]
txid_pending = []
txid_emergency_pending = []

class ChargePoint(cp):
    def init_variables(self, ws_connected, cp_online):
        self.last_total_connect = 0
        self.ws_address = ws_connected
        self.cp_online = cp_online

class OfflineOperation():    
    def __init__(self):
        pass
    
    async def all_off(self):
        all_relay_off()
        
    async def local_start(self, connector_id):
        turn_on_relay(connector_id)
        GPIO.setmode(GPIO.BOARD)    
        GPIO.setup(pin1, GPIO.OUT)
        GPIO.setup(pin2, GPIO.OUT)
        GPIO.setup(pin3, GPIO.OUT)
        GPIO.setup(pin4, GPIO.OUT)
        GPIO.setup(pin5, GPIO.OUT)
        GPIO.setup(pin6, GPIO.OUT)
        
        GPIO.output(pins[connector_id], 1)
        await asyncio.sleep(2)
        GPIO.output(pins[connector_id], 0)

    async def local_stop(self, connector_id):
        turn_off_relay(connector_id)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin1, GPIO.OUT)
        GPIO.setup(pin2, GPIO.OUT)
        GPIO.setup(pin3, GPIO.OUT)
        GPIO.setup(pin4, GPIO.OUT)
        GPIO.setup(pin5, GPIO.OUT)
        GPIO.setup(pin6, GPIO.OUT)
        
        GPIO.output(pins[connector_id], 1)
        await asyncio.sleep(2)
        GPIO.output(pins[connector_id], 0)