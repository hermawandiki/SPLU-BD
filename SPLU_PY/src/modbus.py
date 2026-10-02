from pymodbus.client import ModbusSerialClient
client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600, timeout=1)

def read_power_meter(connector_id, mode, ctratio):
    global client
    if mode == 4:
        count = 4
    else:
        count = 2

    if connector_id == 0:
        return 0

    if connector_id == 1 or connector_id == 4:
        if mode == 0: 
            addr = 831
        elif mode == 1:
            addr = 834
        elif mode == 4:
            addr = 850

    elif connector_id == 2 or connector_id == 5:
        if mode == 0:
            addr = 832
        elif mode == 1:
            addr = 835
        elif mode == 4:
            addr = 852

    elif connector_id == 3 or connector_id == 6:
        if mode == 0:
            addr = 833
        elif mode == 1:
            addr = 836
        elif mode == 4:
            addr = 854

    if connector_id == 1 or connector_id == 2 or connector_id == 3:
        devid=7
    else:
        devid=10

    try:
        result = client.read_holding_registers(
            address=addr,
            count=count,
            device_id=devid
        )
        if result is None or result.isError():
            return 0
        data = result.registers
    except Exception as e:
        return 0

    if mode == 0: #Voltage
        return (data[0]) / 10
    elif mode == 1: #Current
        return ((data[0]) * ctratio) / 100
    elif mode == 2: #Power
        return ((data[0] + data[1]) * ctratio) / 1000
    elif mode == 3: #Power Factor
        return (data[0]) / 1000
    elif mode == 4: #kWh
        return ((data[0] + data[1] + data[2] + data[3]) * ctratio) / 100
    elif mode == 5: #Frequency
        return data[0] / 100

def read_modbus(devid, addr):
    global client
    resp = client.read_holding_registers(
            address=addr,
            count=2,
            device_id=devid
    )
    
    if not resp or not hasattr(resp, "registers"):
        return None
    r = resp.registers
    return r[0], r[1]

def timeout_relay(connector_id, ctratio):
    global client
    if connector_id == 0:
        return 0
    if connector_id == 1 or connector_id == 4:
        addr=834
    elif connector_id == 2 or connector_id == 5:
        addr=835
    elif connector_id == 3 or connector_id == 6:
        addr=836

    if connector_id == 1 or connector_id == 3 or connector_id == 2:
        devid=7
    else:
        devid=10

    try:
        result = client.read_holding_registers(
            address=addr,
            count=2,
            device_id=devid
        )
        if result is None or result.isError():
            return 0

        data = result.registers
    except Exception as e:
        return 0
    return ((data[0]) * ctratio) / 100
                    
def turn_on_relay(addr):
    global client
    try:
        client.write_coil(addr, 0xff00)
    except Exception as e:
        return 0

def turn_off_relay(addr):
    global client
    try:
        client.write_coil(addr, 0x0000)
    except Exception as e:
        return 0

def all_relay_off():
    global client
    try:
        for addr in range(1, 7):
            client.write_coil(addr, 0x0000)
    except Exception as e:
        return 0