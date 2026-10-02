from pymodbus.client import ModbusSerialClient
client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)

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
        elif mode == 2:
            addr = 838
        elif mode == 3:
            addr = 846
        elif mode == 4:
            addr = 850
        elif mode == 5:
            addr = 849

    elif connector_id == 2 or connector_id == 5:
        if mode == 0:
            addr = 832
        elif mode == 1:
            addr = 835
        elif mode == 2:
            addr = 839
        elif mode == 3:
            addr = 847
        elif mode == 4:
            addr = 852
        elif mode == 5:
            addr = 849

    elif connector_id == 3 or connector_id == 6:
        if mode == 0:
            addr = 833
        elif mode == 1:
            addr = 836
        elif mode == 2:
            addr = 840
        elif mode == 3:
            addr = 848
        elif mode == 4:
            addr = 854
        elif mode == 5:
            addr = 849

    data = client.read_holding_registers( address = addr, count = count, unit = 7 ).registers

    if mode == 0: #Voltage
        return (data[0] + data[1]) / 10
    elif mode == 1: #Current
        return ((data[0] + data[1]) * ctratio) / 100
    elif mode == 2: #Power
        return ((data[0] + data[1]) * ctratio) / 1000
    elif mode == 3: #Power Factor
        return (data[0]) / 1000
    elif mode == 4: #kWh
        return ((data[0] + data[1] + data[2] + data[3]) * ctratio) / 100
    elif mode == 5: #Frequency
        return data[0] / 100
    
def turn_on_relay(addr):
    global client
    client.write_coil(addr, 0xff00, slave_id=1)

def turn_off_relay(addr):
    global client
    print(addr)
    client.write_coil(addr, 0x0000, slave_id=1)

def all_relay_off():
    global client
    client.write_coil(0xff, 0x0000, slave_id=1)