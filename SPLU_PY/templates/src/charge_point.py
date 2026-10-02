from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16 import call_result
from ocpp.v16 import enums
from ocpp.routing import on, after

import src.database as db
from src.modbus import read_power_meter, \
    turn_off_relay, turn_on_relay, all_relay_off

from datetime import datetime
from colorama import Fore

import asyncio

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


import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

from mfrc522 import SimpleMFRC522


class ChargePoint(cp):

    def init_variables(self, ws_connected, cp_online):
        self.last_total_connect = 0
        self.ws_address = ws_connected
        self.cp_online = cp_online
   
    async def connect_modbus(self, sleep):
        await asyncio.sleep(sleep) 
        print("Connected to Modbus")
        all_relay_off()

    async def startup_detailcp(self, sleep):
        await asyncio.sleep(sleep)
        print(
            # db.find_values("detailcp", "endpointurl", "id", 2),
            self.ws_address,
            db.find_values("detailcp", "chargeboxid", "id", 2),
            db.find_values("detailcp", "cboxnum", "id", 2), 
            db.find_values("detailcp", "cpmodel", "id", 2),
            db.find_values("detailcp", "cpnum", "id", 2),
            db.find_values("detailcp", "cpvendor", "id", 2),
            db.find_values("detailcp", "fwversion", "id", 2), 
            db.find_values("detailcp", "iccid", "id", 2),
            db.find_values("detailcp", "imsi", "id", 2),
            db.find_values("detailcp", "metersn", "id", 2),
            db.find_values("detailcp", "metertype", "id", 2),
            db.find_values("detailcp", "currentlimit", "id", 2),
            db.find_values("detailcp", "intervalmetervalue", "id", 2),
            "Connector Id       : " + str(db.find_values("configcp", "connectorid", "idconfig", 1)),
            "CP Status          : " + db.find_values("configcp", "cpstatus", "idconfig", 1),
            "CP Error           : " + db.find_values("configcp", "cperror", "idconfig", 1),
            "IdToken            : " + str(db.find_values("configcp", "IdToken", "idconfig", "1")),
            "Heartbeat Interval : " + str(db.find_values("configcp", "HeartbeatInterval", "idconfig", "1")),
            "[",
            Fore.GREEN + "  '" +  db.meter_values_sampled_data[0] + "',",
            "  '" + db.meter_values_sampled_data[1] + "',",
            "  '" + db.meter_values_sampled_data[2] + "',",
            "  '" + db.meter_values_sampled_data[3] + "',",
            "  '" + db.meter_values_sampled_data[4] + "',",
            "  '" + db.meter_values_sampled_data[5] + "'," + Fore.RESET ,
            "]",

            "Minimum Status Duration           : " + str(db.find_values("configcp", "MinimumStatusDuration", "idconfig", 1)),
            "StopTransactionOnEVSideDisconnect : " + str(db.find_values("configcp", "StopTransactionOnEVSideDisconnect", "idconfig", "1")),
            "AllowOfflineTxForUnknownId        : " + str(db.find_values("configcp", "AllowOfflineTxForUnknownId", "idconfig", "1")),
            "AuthorizationCacheEnabled         : " + str(db.find_values("configcp", "AuthorizationCacheEnabled", "idconfig", "1")),
            "LocalPreAuthorize                 : " + str(db.find_values("configcp", "LocalPreAuthorize", "idconfig", "1")),
            "LocalAuthorizeOffline             : " + str(db.find_values("configcp", "LocalAuthorizeOffline", "idconfig", "1")),
            sep='\n'
        )

    # Indikasi terkoneksi Websocket
    async def connected_ws(self, sleep):
        await asyncio.sleep(sleep)
        print(
            db.find_values("detailcp", "endpointurl", "id", 2) + str(db.find_values("detailcp", "chargeboxid", "id", 2)),
            "Websocket Client Connected",
            sep="\n"

            
        )
   
   #####################################
    # SENDING REQUEST TO CENTRAL SYSTEM #
    #####################################

    async def send_authorize(self, id):
        """Send Authorization Request to Central System"""

        await asyncio.sleep(1)

        request = call.AuthorizePayload(id_tag=id)
        response = await self.call(request)

        if response.id_tag_info.status == 'Accepted':
            print("Authorized.")
        else:
            print("Authorization failed.")

    async def send_boot_notification(self, sleep):
        """ Send Boot Notification Request to Central System"""

        await asyncio.sleep(sleep)

        request = call.BootNotificationPayload(
            charge_point_model          = db.find_values("detailcp", "cpmodel", "id", 2),
            charge_point_vendor         = db.find_values("detailcp", "cpvendor", "id", 2),
            charge_point_serial_number  = db.find_values("detailcp", "cpnum", "id", 2), 
            charge_box_serial_number    = db.find_values("detailcp", "cboxnum", "id", 2),
            firmware_version            = db.find_values("detailcp", "fwversion", "id", 2),
            iccid                       = db.find_values("detailcp", "iccid", "id", 2),
            imsi                        = db.find_values("detailcp", "imsi", "id", 2),
            meter_type                  = db.find_values("detailcp", "metertype", "id", 2),
            meter_serial_number         = db.find_values("detailcp", "metersn", "id", 2),
        )

        response = await self.call(request)

        if response.status == 'Accepted':
            print("Connected to central system.")
        else:
            print("Connection to central system failed.")

    # SENDING HEARTBEAT
    async def send_heartbeat(self):
        """ Send Heartbeat to Central System"""
        while True:
            await asyncio.sleep(db.find_values("configcp", "HeartbeatInterval", "idconfig", 1))

            request = call.HeartbeatPayload()
            response = await self.call(request)
            return response
        
    async def send_meter_values(self):
        """ Send Meter Values to Central System"""
        while True:
            total_connect = 0

            await asyncio.sleep(
                db.find_values("configcp", "MeterValueSampleInterval", "idconfig", 1) - (self.last_total_connect * 0.7 )
            )

            for i, status in enumerate(currentTx['connected']):

                # if connector is on
                if status == 1:
                    total_connect += 1

                    transaction_id = currentTx['txid'][i]

                    currentTx['idinterval'][i] += 1

                    meter_voltage = read_power_meter(i + 1, 0, CTRATIO)
                    meter_current = read_power_meter(i + 1, 1, CTRATIO)
                    meter_power = read_power_meter(i + 1, 2, CTRATIO)
                    meter_pf = read_power_meter(i + 1, 3, CTRATIO)
                    meter_kwh_value = read_power_meter(i + 1, 4, CTRATIO)
                    meter_freq = read_power_meter(i + 1, 5, CTRATIO)

                    measurandarray = db.meter_values_sampled_data

                    sample_value = []

                    for measure in measurandarray:
                        if (measure == enums.Measurand.voltage):
                            meter_voltage = float(meter_voltage)
                            obj = {
                                'value': str(meter_voltage),
                                'format': enums.ValueFormat.raw,
                                'measurand': enums.Measurand.voltage,
                                'context': enums.ReadingContext.sample_periodic,
                                'phase': enums.Phase.l1,
                                'unit': enums.UnitOfMeasure.v,
                            }
                            sample_value.append(obj)

                        if (measure == enums.Measurand.current_import):
                            meter_current = float(meter_current)
                            obj = {
                                'value': str(meter_current),
                                'format': enums.ValueFormat.raw,
                                'measurand': enums.Measurand.current_import,
                                'context': enums.ReadingContext.sample_periodic,
                                'phase': enums.Phase.l1,
                                'unit': enums.UnitOfMeasure.a,
                            }
                            sample_value.append(obj)

                        if (measure == enums.Measurand.power_active_import):
                            meter_power = float(meter_power)
                            obj = {
                                'value': str(meter_power),
                                'format': enums.ValueFormat.raw,
                                'measurand': enums.Measurand.power_active_import,
                                'context': enums.ReadingContext.sample_periodic,
                                'phase': enums.Phase.l1,
                                'unit': enums.UnitOfMeasure.kw,
                            }
                            sample_value.append(obj)

                        if (measure == enums.Measurand.power_factor):
                            meter_pf = float(meter_pf)
                            obj = {
                                'value': str(meter_pf),
                                'format': enums.ValueFormat.raw,
                                'measurand': enums.Measurand.power_factor,
                                'context': enums.ReadingContext.sample_periodic,
                                'phase': enums.Phase.l1,
                            }
                            sample_value.append(obj)

                        if (measure == enums.Measurand.energy_active_import_register):
                            meter_kwh_value = float(meter_kwh_value)
                            obj = {
                                'value': str(meter_kwh_value),
                                'format': enums.ValueFormat.raw,
                                'measurand': enums.Measurand.energy_active_import_register,
                                'context': enums.ReadingContext.sample_periodic,
                                'phase': enums.Phase.l1,
                                'unit': enums.UnitOfMeasure.kwh,
                            }
                            sample_value.append(obj)  

                        if (measure == enums.Measurand.frequency):
                            meter_freq = float(meter_freq)
                            obj = {
                                'value': str(meter_freq),
                                'format': enums.ValueFormat.raw,
                                'measurand': enums.Measurand.frequency,
                                'context': enums.ReadingContext.sample_periodic,
                                'phase': enums.Phase.l1,
                            }
                            sample_value.append(obj)      

                    request = call.MeterValuesPayload(
                        connector_id=i+1,
                        meter_value=[{
                            'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            'sampled_value': sample_value,
                        }],
                        transaction_id=transaction_id
                    )


                    response = await self.call(request)
                    return response
                
                self.last_total_connect = total_connect
                total_connect = 0   
                
    async def send_status_notification(self, connector_id, sleep):
        await asyncio.sleep(sleep)

        if(db.check_if_operative(connector_id) == "Operative"):
            status = enums.ChargePointStatus.available
        elif(db.check_if_operative(connector_id) == "Inoperative"):
            status = enums.ChargePointStatus.unavailable

        request = call.StatusNotificationPayload(
            connector_id=connector_id,
            error_code=enums.ChargePointErrorCode.no_error,
            status=status,
        )
        response = await self.call(request)
        return response
    

    @after(enums.Action.RemoteStartTransaction)
    async def send_start_transaction(self, connector_id, id_tag, remote=1):
        if(currentTx['connected'][connector_id - 1] == 1 and (db.check_if_id_exists(id_tag))):

            date_time = datetime.now()
            
            if(remote == 1):
                await asyncio.sleep(5)

            # check apakah transaksi sudah berjalan sebelumnya, 
            # jika sudah menggunakan meter start yang digunakan sebelumnya
            if(currentTx['started'][connector_id - 1] == 1):
                meter_start = currentTx['meter_start'][connector_id - 1]
            else:
                meter_start = int(read_power_meter(connector_id, 4, CTRATIO))
                currentTx['meter_start'][connector_id - 1] = int(read_power_meter(connector_id, 4, CTRATIO))

            if(currentTx['datetime_start'][connector_id - 1] != 0):
                timestamp = currentTx['datetime_start'][connector_id - 1]
            else:
                timestamp = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                currentTx['datetime_start'][connector_id - 1] = timestamp
            
            request = call.StartTransactionPayload(
                connector_id=connector_id,
                id_tag = str(id_tag),
                meter_start=meter_start,
                timestamp=timestamp
            )
            currentTx["connected"][connector_id - 1] = 1

            response = await self.call(request)

            # jika transaksi blum berjalan, maka nyalakan relay
            if(currentTx['started'][connector_id - 1] == 0):
                GPIO.setmode(GPIO.BOARD)
                GPIO.setup(pin1, GPIO.OUT)
                GPIO.setup(pin2, GPIO.OUT)
                GPIO.setup(pin3, GPIO.OUT)
                GPIO.setup(pin4, GPIO.OUT)
                GPIO.setup(pin5, GPIO.OUT)
                GPIO.setup(pin6, GPIO.OUT)

                turn_on_relay(connector_id - 1)
                GPIO.output(pins[connector_id - 1], 1)
                await asyncio.sleep(2)
                GPIO.output(pins[connector_id - 1], 0)
                GPIO.cleanup()
        
                currentTx['started'][connector_id - 1] = 1
                db.update_switchpos(connector_id, 1)

                offline_transaction_id = (db.get_latest_id() + 1)

                db.start_transaction(offline_transaction_id, id_tag, connector_id, meter_start, date_time.strftime("%Y-%m-%d %H:%M:%S"), transaction_id_cs=response.transaction_id)
                if(db.check_auth_id(id_tag) != True):
                    db.store_auth_cache(id_tag)

            else:
                db.update_transaction_id(currentTx['txid_off'][connector_id - 1], response.transaction_id)

            currentTx['idinterval'][connector_id - 1] = 1
            currentTx["txid"][connector_id - 1] = response.transaction_id
            currentTx["token_id"][connector_id - 1] = id_tag 

            # print(currentTx)
            print("START TRANSACTION SUCCESS")

            return response
        
        else:
            currentTx['connected'][connector_id - 1] = 0
            print("masuk rejected")

    @after(enums.Action.RemoteStopTransaction)
    async def send_stop_transaction(self, transaction_id, remote=1):
        if remote==1:
            reason = enums.Reason.remote
        elif remote==2:
            reason = enums.Reason.emergency_stop
            all_relay_off()
            for x in range(6):
                db.update_switchpos(x + 1, 0)

        else:
            reason = enums.Reason.local

        if (transaction_id in currentTx['txid']):

            date_time = datetime.now()

            print("masuk stop transaction req")
            i = currentTx['txid'].index(transaction_id)

            if remote == 1:
                await asyncio.sleep(5)

            if(currentTx['started'][i] == 0):
                meter_stop = currentTx['meter_stop'][i]
            else:
                meter_stop = int(read_power_meter((i + 1), 4, CTRATIO))
                currentTx['meter_stop'][i] = meter_stop

            if(currentTx['datetime_stop'][i] != 0):
                timestamp = currentTx['datetime_stop'][i]
            else:
                timestamp = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                currentTx['datetime_stop'][i] = timestamp


            request = call.StopTransactionPayload(
                meter_stop=meter_stop,
                timestamp=timestamp,
                transaction_id=transaction_id,
                reason=reason,
            )

            response = await self.call(request)

            if(currentTx['started'][i] == 1):
                GPIO.setmode(GPIO.BOARD)

                GPIO.setup(pin1, GPIO.OUT)
                GPIO.setup(pin2, GPIO.OUT)
                GPIO.setup(pin3, GPIO.OUT)
                GPIO.setup(pin4, GPIO.OUT)
                GPIO.setup(pin5, GPIO.OUT)
                GPIO.setup(pin6, GPIO.OUT)

                turn_off_relay(i)

                GPIO.output(pins[i], 1)
                await asyncio.sleep(2)
                GPIO.output(pins[i], 0)
                GPIO.cleanup()

                currentTx["started"][i] = 0
                db.update_switchpos((i + 1), 0)
                if(db.check_auth_id(currentTx['token_id'][i]) != True):
                    db.store_auth_cache(currentTx["token_id"][i])
                
                db.stop_transaction(meter_stop, date_time.strftime("%Y-%m-%d %H:%M:%S"), transaction_id_cs=transaction_id)

            currentTx["connected"][i] = 0
            currentTx["txid"][i] = 0
            currentTx['txid_off'][i] = 0
            currentTx["idinterval"][i] = 0
            currentTx["token_id"][i] = 0
            currentTx['meter_start'][i] = 0
            currentTx['meter_stop'][i] = 0
            currentTx['datetime_start'][i] = 0
            currentTx['datetime_stop'][i] = 0

            db.delete_transaction(transaction_id)


            print("STOP TRANSACTION REQ SUCCESS")
            # print(currentTx)

            return response

    #########################################
    # RECEIVING REQUEST FROM CENTRAL SYSTEM #
    #########################################
    @on(enums.Action.RemoteStartTransaction)
    def recv_remote_start(self, id_tag, connector_id):
        """Receiving Remote Start Transaction Command"""
        if(db.check_if_operative(connector_id) == 'Operative'):
            currentTx['connected'][connector_id - 1] = 1

            turn_on_relay(connector_id - 1)
            db.update_switchpos(connector_id, 1)

            result = call_result.RemoteStartTransactionPayload(
                status=enums.RemoteStartStopStatus.accepted
            )

        elif(db.check_if_operative(connector_id) == 'Inoperative'):
            turn_off_relay(connector_id - 1)
            db.update_switchpos((connector_id), 0)

            result = call_result.RemoteStartTransactionPayload(
                status=enums.RemoteStartStopStatus.rejected
            )
        
        return result

    @on(enums.Action.RemoteStopTransaction)
    def recv_remote_stop(self, transaction_id):
        """Receiving Remote Stop Transaction Command"""
        if transaction_id in currentTx['txid']:
            i = currentTx['txid'].index(transaction_id)

            if (db.check_if_operative(i + 1) == "Operative"):

                return call_result.RemoteStopTransactionPayload(
                    status=enums.RemoteStartStopStatus.accepted
                )
        
            elif (db.check_if_operative((i + 1)) == "Inoperative"):
                turn_off_relay(i)
                db.update_switchpos((i + 1), 0)

                return call_result.RemoteStopTransactionPayload(
                    status=enums.RemoteStartStopStatus.rejected
                )
            

    #########################################
         # LOCAL/OFFLINE TRANSACTIONS #
    #########################################

    
    async def local_start_transaction(self, connector_id, id_tag):
        """Function to start Transaction Locally"""
        if(db.check_if_id_exists(id_tag)):

            offline_transaction_id = (db.get_latest_id() + 1)
            date_time = datetime.now()
            GPIO.setmode(GPIO.BOARD)

            GPIO.setup(pin1, GPIO.OUT)
            GPIO.setup(pin2, GPIO.OUT)
            GPIO.setup(pin3, GPIO.OUT)
            GPIO.setup(pin4, GPIO.OUT)
            GPIO.setup(pin5, GPIO.OUT)
            GPIO.setup(pin6, GPIO.OUT)

            turn_on_relay(connector_id - 1)
                
            GPIO.output(pins[connector_id - 1], 1)
            await asyncio.sleep(2)
            GPIO.output(pins[connector_id - 1], 0)
            GPIO.cleanup()

            db.update_switchpos(connector_id, 1)

            currentTx['started'][connector_id - 1] = 1
            currentTx['idinterval'][connector_id - 1] = 1
            currentTx['txid_off'][connector_id - 1] = offline_transaction_id
            currentTx['meter_start'][connector_id - 1] = int(read_power_meter(connector_id, 4, CTRATIO))
            currentTx['datetime_start'][connector_id - 1] = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            currentTx['token_id'][connector_id - 1] = id_tag
            # print(currentTx)

            db.start_transaction(offline_transaction_id, id_tag, connector_id, int(read_power_meter(connector_id, 4, CTRATIO)), date_time.strftime("%Y-%m-%d %H:%M:%S"))
            if(db.check_auth_id(id_tag) != True):
                db.store_auth_cache(id_tag)

            token_pending[connector_id - 1] = id_tag


            print("LOCAL START FINISHED")

            return 1

    # MENGHENTIKAN TRANSACTION SECARA LOCAL
    async def local_stop_transaction(self, id_tag, emergency=0):
        """Function to stop Transaction Locally"""
        if(emergency == 1):
            all_relay_off()
            for x in range(6):
                db.update_switchpos(x + 1, 0)

        if id_tag in currentTx['token_id']:
            i = currentTx['token_id'].index(id_tag)
            date_time = datetime.now()
            GPIO.setmode(GPIO.BOARD)

            GPIO.setup(pin1, GPIO.OUT)
            GPIO.setup(pin2, GPIO.OUT)
            GPIO.setup(pin3, GPIO.OUT)
            GPIO.setup(pin4, GPIO.OUT)
            GPIO.setup(pin5, GPIO.OUT)
            GPIO.setup(pin6, GPIO.OUT)

            turn_off_relay(i)

            GPIO.output(pins[i], 1)
            await asyncio.sleep(2)
            GPIO.output(pins[i], 0)
            GPIO.cleanup()

            if(currentTx['txid'][i] != 0):
                if(emergency == 1):
                    txid_emergency_pending.append(currentTx['txid'][i])
                else:
                    txid_pending.append(currentTx["txid"][i])

            if id_tag in token_pending:
                token_pending.remove(id_tag)
            
            if(db.check_auth_id(currentTx['token_id'][i]) != True):
                db.store_auth_cache(currentTx['token_id'][i])

            db.update_switchpos((i + 1), 0)
            currentTx['started'][i] = 0 
            currentTx['txid_off'][i] = 0
            currentTx['meter_stop'][i] = int(read_power_meter(i + 1, 4, CTRATIO))
            currentTx['meter_start'][i] = 0
            currentTx['token_id'][i] = 0
            currentTx['datetime_start'][i] = 0 
            currentTx['datetime_stop'][i] = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")


            db.stop_transaction(currentTx['meter_stop'][i], date_time.strftime("%Y-%m-%d %H:%M:%S"), id_tag=id_tag)


        print("LOCAL STOP")
        # print(currentTx)

        return 1
            
    #########################################
                # RFID SCANNING #
    #########################################'

    async def rfid_start_stop(self, is_online, emergency=0):
        """ Algorithm to determine action after RFID Scanned """
        if(emergency==1):
            # print("emergency stop")

            if(is_online == 1):
                for tx in currentTx['txid']:
                    if(tx != 0):
                        # print("emergency stop")
                        await self.send_stop_transaction(tx, 2)
            elif(is_online == 0):
                for id in currentTx['token_id']:
                    if(id != 0):
                        # print("emergency stop")
                        await self.local_stop_transaction(id, 1)

            return 1
        
        if(is_online == 0):
            print("rfid_start_stop")

        rfid = SimpleMFRC522()

        id, text = rfid.read(timeout=0.5)
        if(id != None):
            id = str(id)
            print(id)

            if id in currentTx['token_id']:
                if(is_online == 1):
                    i = currentTx['token_id'].index(id)
                    print("masuk online stop")
                    await self.send_stop_transaction(currentTx['txid'][i], 0)

                    return 1
                elif(is_online == 0):
                    print("masuk local stop")
                    await self.local_stop_transaction(id)

                    return 1
                
            for j in range(1, 7):
                if((db.check_switchpos(j) == "Close") 
                   and (db.check_if_operative(j) == "Operative")):
                    
                    if (is_online == 1):
                        print("masuk is online")
                        if(db.find_values("configcp", "LocalPreAuthorize", "idconfig", 1) == 1 and db.check_id_in_auth_cache(id) == True):
                            print("masuk sini")

                            connector_id = j
                            currentTx['token_id'][connector_id - 1] = id
                            currentTx["connected"][connector_id - 1] = 1

                            print("masuk online start pre authorized")
                            await self.send_start_transaction(connector_id, id, 0)
                            return 1
                            
                        else:
                            print("masuk authorize req")
                            request = call.AuthorizePayload(
                                id_tag=id
                            )

                            response = await self.call(request)

                            if(response.id_tag_info['status'] == 'Accepted'):
                                print('Authorization Success')
                                connector_id = j

                                currentTx['token_id'][connector_id - 1] = id
                                currentTx["connected"][connector_id - 1] = 1

                                print("masuk online start")
                                await self.send_start_transaction(connector_id, id, 0)
                                return 1
                            
                            else:
                                print("CARD REJECTED")
                                return 0
                                                       
                    elif(is_online == 0):
                        
                        if(db.find_values("configcp", "LocalAuthorizeOffline", "idconfig", "1")):
                            if(db.check_if_id_exists(id) and db.check_id_status(id) == "Accepted"):
                                connector_id = j

                                currentTx['token_id'][connector_id - 1] = id
                                currentTx["connected"][connector_id - 1] = 1

                                print("masuk offline start")
                                await self.local_start_transaction(connector_id, id)
                                return 1
                            
                            elif(db.check_id_status(id) != "Accepted"):
                                print("ID Rejected")
                                return 0
                            
                        elif (db.find_values("configcp", "AllowOfflineTxForUnknownId", "idconfig", 1) == 1):

                            if(db.find_values("configcp", "LocalPreAuthorize", "idconfig", 1) == 1 and db.check_id_in_auth_cache(id) == True):
                                connector_id = j
                                currentTx['token_id'][connector_id - 1] = id

                                print("masuk local start unknown {}".format(connector_id))
                                await self.local_start_transaction(connector_id, id)
                                return 1


    async def rfid_interval(self):
        """ Make Interval to keep scanning for RFID Cards """
        print("RFID INTERVAL")
        await asyncio.sleep(12)
        n = 1


        while True:
            # print("RFID")
            n += 1
            # await asyncio.sleep(2)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(emergency_pin, GPIO.IN)

            if(GPIO.input(emergency_pin) == 0):
                print("EMERGENCY!!!!")
                await self.rfid_start_stop(self.cp_online, 1)
                GPIO.cleanup()
                await asyncio.sleep(2)
                
                continue
            
            await self.rfid_start_stop(self.cp_online)
            await asyncio.sleep(1)

    async def check_ongoing_transaction(self, sleep):
        await asyncio.sleep(sleep)
        await self.heartbeat_req()

        print("CHECK TRANSACTION")

        if(len(txid_pending) > 0):

            for token in txid_pending:
                if token != 0:
                # print("detected stop transac")
                    await self.stop_transaction_req(token, 0)

        if (len(txid_emergency_pending) > 0):
            for token in txid_emergency_pending:
                if token != 0:
                # print("detected emergency stop transac")
                    await self.stop_transaction_req(token, 2)
            
        for i, token in enumerate(token_pending):
            if(token != 0):
                currentTx['connected'][i] = 1   
                await self.start_transaction_req((i + 1), token, 0)
                token_pending[i] = 0

        txid_pending.clear()
        
        print("CHECK TRANSACTION DONE")
            
class OfflineOperation():
    def __init__(self):
        pass

    async def offline_start_transaction(self, connector_id, id_tag):
        if(db.check_if_id_exists(id_tag)):

            offline_transaction_id = (db.get_latest_id() + 1)
            date_time = datetime.now()
            GPIO.setmode(GPIO.BOARD)

            GPIO.setup(pin1, GPIO.OUT)
            GPIO.setup(pin2, GPIO.OUT)
            GPIO.setup(pin3, GPIO.OUT)
            GPIO.setup(pin4, GPIO.OUT)
            GPIO.setup(pin5, GPIO.OUT)
            GPIO.setup(pin6, GPIO.OUT)

            turn_on_relay(connector_id - 1)
            
            GPIO.output(pins[connector_id - 1], 1)
            await asyncio.sleep(2)
            GPIO.output(pins[connector_id - 1], 0)
            GPIO.cleanup()

            db.update_switchpos(connector_id, 1)

            currentTx['started'][connector_id - 1] = 1
            currentTx['idinterval'][connector_id - 1] = 1
            currentTx['token_id'][connector_id - 1] = id_tag
            currentTx['txid_off'][connector_id - 1] = offline_transaction_id
            currentTx['meter_start'][connector_id - 1] = int(read_power_meter(connector_id, 4, CTRATIO))
            currentTx['datetime_start'][connector_id - 1] = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            db.start_transaction(offline_transaction_id, id_tag, connector_id, int(read_power_meter(connector_id, 4, CTRATIO)), date_time.strftime("%Y-%m-%d %H:%M:%S"))
            
            if(db.check_auth_id(id_tag) != True):
                db.store_auth_cache(id_tag)
            token_pending[connector_id - 1] = id_tag

            print("OFFLINE START")
            print(currentTx)

            return 1

    # MENGHENTIKAN TRANSACTION SECARA BENAR-BENAR OFFLINE
    async def offline_stop_transaction(self, id_tag, emergency=0):

        if(emergency == 1):
            all_relay_off()
            for x in range(6):
                db.update_switchpos(x + 1, 0)

        if id_tag in currentTx['token_id']:
            i = currentTx['token_id'].index(id_tag)
            date_time = datetime.now()
            GPIO.setmode(GPIO.BOARD)

            GPIO.setup(pin1, GPIO.OUT)
            GPIO.setup(pin2, GPIO.OUT)
            GPIO.setup(pin3, GPIO.OUT)
            GPIO.setup(pin4, GPIO.OUT)
            GPIO.setup(pin5, GPIO.OUT)
            GPIO.setup(pin6, GPIO.OUT)
            
            turn_off_relay(i)

            GPIO.output(pins[i], 1)
            await asyncio.sleep(2)
            GPIO.output(pins[i], 0)
            GPIO.cleanup()

            if(currentTx['txid'] != 0):
                if(emergency == 1):
                    txid_emergency_pending.append(currentTx['txid'][i])
                else:
                    txid_pending.append(currentTx["txid"][i])

            db.update_switchpos((i + 1), 0)


            currentTx['meter_stop'][i] = int(read_power_meter(i+1, 4, CTRATIO))
            currentTx['txid_off'][i] = 0
            currentTx['idinterval'][i] = 0
            currentTx['meter_start'][i] = 0
            currentTx['started'][i] = 0
            currentTx['datetime_start'][i] = 0
            currentTx['datetime_stop'][i] = date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            currentTx['token_id'][i] = 0
            currentTx['connected'][i] = 0

            if id_tag in token_pending:
                token_pending.remove(id_tag)

            db.stop_transaction(currentTx['meter_stop'][i], date_time.strftime("%Y-%m-%d %H:%M:%S"), id_tag=id_tag)
            
            if(db.check_auth_id(currentTx['token_id'][i]) != True):
                db.store_auth_cache(currentTx['token_id'][i])

        print("OFFLINE STOP")
        print(currentTx)

        return 1

    async def rfid_interval(self):
        await asyncio.sleep(12)
        n = 1


        while True:
            # print("RFID")
            n += 1

            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(emergency_pin, GPIO.IN)
            if(GPIO.input(emergency_pin) == 0):
                print("EMERGENCY!!!!")
                await self.rfid_check(0.05, 1)
                GPIO.cleanup()
                await asyncio.sleep(2)
                continue

            await self.rfid_check(0.05)
            await asyncio.sleep(0.8)

    async def rfid_check(self, timeout, emergency=0):

            if(emergency==1):
                print("emergency stop")
                for id in currentTx['token_id']:
                    if(id != 0):
                        print("emergency stop")
                        await self.offline_stop_transaction(id, 1)
                return 1

            print("rfid_check")
            rfid = SimpleMFRC522()
            id, text = rfid.read(timeout=timeout)

            if(id != None):
                id = str(id)
                print(id)

                if id in currentTx['token_id']:
                    print("masuk offline stop")
                    await self.offline_stop_transaction(id)
                    return 1
                
                for j in range(1, 7):
                    if((db.check_switchpos(j) == "Close") and (db.check_if_operative(j) == "Operative")):
                        if(db.find_values("configcp", "LocalAuthorizeOffline", "idconfig", "1")):
                            if(db.check_if_id_exists(id) and db.check_id_status(id) == "Accepted"):
                                connector_id = j

                                currentTx['token_id'][connector_id - 1] = id
                                currentTx["connected"][connector_id - 1] = 1

                                print("masuk offline start")
                                await self.offline_start_transaction(connector_id, id)
                                return 1
                            elif(db.check_if_id_exists(id) and db.check_id_status(id) != "Accepted"):
                                print("ID Rejected")
                                
                        elif (db.find_values("configcp", "AllowOfflineTxForUnknownId", "idconfig", 1) == 1):
                            if(db.check_if_id_exists(id)):
                                continue

                            if(db.find_values("configcp", "LocalPreAuthorize", "idconfig", 1) == 1):
                                if(db.check_id_in_auth_cache(id) == True):
                        
                                    connector_id = j
                                    currentTx['token_id'][connector_id - 1] = id

                                    print("masuk local start unknown {}".format(connector_id))
                                    await self.offline_start_transaction(connector_id, id)
                                    return 1