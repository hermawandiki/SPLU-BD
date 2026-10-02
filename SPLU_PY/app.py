
# an object of WSGI application 
from flask import Flask, redirect, url_for, render_template, request
import src.database as db
import sys

debug_mode = None
if(len(sys.argv) > 1):
   debug_mode = sys.argv[1]

app = Flask(__name__)   # Flask constructor 
  
# A decorator used to tell the application 
# which URL is associated function 
@app.route("/") 
def index(): 
   url_endpoint = db.find_values("detailcp", "endpointurl", "id", 2)
   cboxid = db.find_values("detailcp", "chargeboxid", "id", 2)
   cboxnum = db.find_values("detailcp", "cboxnum", "id", 2)
   cpmodel = db.find_values("detailcp", "cpmodel", "id", 2)
   cpnum = db.find_values("detailcp", "cpnum", "id", 2)
   cpvendor = db.find_values("detailcp", "cpvendor", "id", 2)
   fw_version = db.find_values("detailcp", "fwversion", "id", 2)
   iccid = db.find_values("detailcp", "iccid", "id", 2)
   imsi = db.find_values("detailcp", "imsi", "id", 2)
   meter_sn = db.find_values("detailcp", "metersn", "id", 2)
   meter_type = db.find_values("detailcp", "metertype", "id", 2)

   return render_template("index.html", **locals())  

@app.route("/save-cp-data", methods=["POST"])
def save_cp_data():
   if request.method == "POST":
      url_endpoint = request.form["url_endpoint"]
      cboxid = request.form["cboxid"]
      cboxnum = request.form["cboxnum"]
      cpmodel = request.form["cpmodel"]
      cpnum = request.form["cpnum"]
      cpvendor = request.form["cpvendor"]
      fw_version = request.form["fw_version"]
      iccid = request.form["iccid"]
      imsi = request.form["imsi"]
      meter_sn = request.form["meter_sn"]
      meter_type = request.form["meter_type"]

      if(url_endpoint != ""):
         db.change_values("endpointurl", url_endpoint)

      if(cboxid != ""):
         db.change_values("chargeboxid", cboxid)

      if(cboxnum != ""):
         db.change_values("cboxnum", cboxnum)

      if(cpmodel != ""):
         db.change_values("cpmodel", cpmodel)

      if(cpnum != ""):
         db.change_values("cpnum", cpnum)

      if(cpvendor != ""):
         db.change_values("cpvendor", cpvendor)

      if(fw_version != ""):
         db.change_values("fwversion", fw_version)

      if(iccid != ""):
         db.change_values("iccid", iccid)

      if(imsi != ""):
         db.change_values("imsi", imsi)

      if(meter_sn != ""):
         db.change_values("metersn", meter_sn)

      if(meter_type != ""):
         db.change_values("metertype", meter_type)

      # return render_template("index.html", **locals())
      return redirect(url_for("index"))

@app.route("/connector-status")
def connector_status():
   print("masuk fungsi ini")
   conn1 = db.check_switchpos(1)
   conn2 = db.check_switchpos(2)
   conn3 = db.check_switchpos(3)
   conn4 = db.check_switchpos(4)
   conn5 = db.check_switchpos(5)
   conn6 = db.check_switchpos(6)

   return render_template("conn.html", **locals())

@app.route("/get-config")
def get_config():
   GetConfigurationMaxKeys                   = db.getConfiguration("GetConfigurationMaxKeys")
   MeterValuesAlignedDataMaxLength           = db.getConfiguration("MeterValuesAlignedDataMaxLength")
   MeterValuesSampledDataMaxLength           = db.getConfiguration("MeterValuesSampledDataMaxLength")
   NumberOfConnectors                        = db.getConfiguration("NumberOfConnectors")
   ConnectorPhaseRotationMaxLength           = db.getConfiguration("ConnectorPhaseRotationMaxLength")
   StopTxnAlignedDataMaxLength               = db.getConfiguration("StopTxnAlignedDataMaxLength")
   StopTxnSampledDataMaxLength               = db.getConfiguration("StopTxnSampledDataMaxLength")
   SupportedFeatureProfilesMaxLength         = db.getConfiguration("SupportedFeatureProfilesMaxLength")
   LocalAuthListMaxLength                    = db.getConfiguration("LocalAuthListMaxLength")
   SendLocalListMaxLength                    = db.getConfiguration("SendLocalListMaxLength")
   ReserveConnectorZeroSupported             = db.getConfiguration("ReserveConnectorZeroSupported")
   ChargeProfileMaxStackLevel                = db.getConfiguration("ChargeProfileMaxStackLevel")
   ChargingScheduleAllowedChargingRateUnit   = db.getConfiguration("ChargingScheduleAllowedChargingRateUnit")
   ChargingScheduleMaxPeriods                = db.getConfiguration("ChargingScheduleMaxPeriods")
   ConnectorSwitch3to1PhaseSupported         = db.getConfiguration("ConnectorSwitch3to1PhaseSupported")
   MaxChargingProfilesInstalled              = db.getConfiguration("MaxChargingProfilesInstalled")
   
   return render_template("getconf.html", **locals())

@app.route("/change-config")
def show_change_config():
   AllowOfflineTxForUnknownId = bool(db.getConfiguration("AllowOfflineTxForUnknownId"))
   AuthorizationCacheEnabled = bool(db.getConfiguration("AuthorizationCacheEnabled"))
   AuthorizeRemoteTxRequests = bool(db.getConfiguration("AuthorizeRemoteTxRequests"))
   BlinkRepeat = db.getConfiguration("BlinkRepeat")
   ClockAlignedDataInterval = db.getConfiguration("ClockAlignedDataInterval")
   ConnectionTimeOut = db.getConfiguration("ConnectionTimeOut")
   HeartbeatInterval = db.getConfiguration("HeartbeatInterval")
   LightIntensity = db.getConfiguration("LightIntensity")
   LocalAuthListEnabled = bool(db.getConfiguration("LocalAuthListEnabled"))
   LocalAuthorizeOffline = bool(db.getConfiguration("LocalAuthorizeOffline"))
   LocalPreAuthorize = bool(db.getConfiguration("LocalPreAuthorize"))
   MaxEnergyOnInvalidId = db.getConfiguration("MaxEnergyOnInvalidId")
   MeterValuesAlignedData = db.getConfiguration("MeterValuesAlignedData")
   MeterValuesSampledData = db.getConfiguration("MeterValuesSampledData")
   MeterValueSampleInterval = db.getConfiguration("MeterValueSampleInterval")
   MinimumStatusDuration = db.getConfiguration("MinimumStatusDuration")
   ResetRetries = db.getConfiguration("ResetRetries")
   ConnectorPhaseRotation = db.getConfiguration("ConnectorPhaseRotation")
   StopTransactionOnEVSideDisconnect = bool(db.getConfiguration("StopTransactionOnEVSideDisconnect"))
   StopTransactionOnInvalidId = bool(db.getConfiguration("StopTransactionOnInvalidId"))
   StopTxnAlignedData = db.getConfiguration("StopTxnAlignedData")
   StopTxnSampledData = db.getConfiguration("StopTxnSampledData")
   TransactionMessageAttempts = db.getConfiguration("TransactionMessageAttempts")
   TransactionMessageRetryInterval = db.getConfiguration("TransactionMessageRetryInterval")
   UnlockConnectorOnEVSideDisconnect = bool(db.getConfiguration("UnlockConnectorOnEVSideDisconnect"))
   WebSocketPingInterval = db.getConfiguration("WebSocketPingInterval")
   IdToken = db.getConfiguration("IdToken")
   LastTagIdToken = db.getConfiguration("LastTagIdToken")

   return render_template("changeconf.html", **locals())

@app.route("/save-config", methods=["POST"])
def save_config():

   if request.method == "POST":
   
      AllowOfflineTxForUnknownId = request.form["AllowOfflineTxForUnknownId"]
      AuthorizationCacheEnabled = request.form["AuthorizationCacheEnabled"]
      AuthorizeRemoteTxRequests = request.form["AuthorizeRemoteTxRequests"]
      BlinkRepeat = request.form["BlinkRepeat"]
      ClockAlignedDataInterval = request.form["ClockAlignedDataInterval"]
      ConnectionTimeOut = request.form["ConnectionTimeOut"]
      HeartbeatInterval = request.form["HeartbeatInterval"]
      LightIntensity = request.form["LightIntensity"]
      LocalAuthListEnabled = request.form["LocalAuthListEnabled"]
      LocalAuthorizeOffline = request.form["LocalAuthorizeOffline"]
      LocalPreAuthorize = request.form["LocalPreAuthorize"]
      MaxEnergyOnInvalidId = request.form["MaxEnergyOnInvalidId"]
      MeterValuesAlignedData = request.form["MeterValuesAlignedData"]
      MeterValuesSampledData = request.form["MeterValuesSampledData"]
      MeterValueSampleInterval = request.form["MeterValueSampleInterval"]
      MinimumStatusDuration = request.form["MinimumStatusDuration"]
      ResetRetries = request.form["ResetRetries"]
      ConnectorPhaseRotation = request.form["ConnectorPhaseRotation"]
      StopTransactionOnEVSideDisconnect = request.form["StopTransactionOnEVSideDisconnect"]
      StopTransactionOnInvalidId = request.form["StopTransactionOnInvalidId"]
      StopTxnAlignedData = request.form["StopTxnAlignedData"]
      StopTxnSampledData = request.form["StopTxnSampledData"]
      TransactionMessageAttempts = request.form["TransactionMessageAttempts"]
      TransactionMessageRetryInterval = request.form["TransactionMessageRetryInterval"]
      UnlockConnectorOnEVSideDisconnect = request.form["UnlockConnectorOnEVSideDisconnect"]
      WebSocketPingInterval = request.form["WebSocketPingInterval"]
      IdToken = request.form["IdToken"]
      LastTagIdToken = request.form["LastTagIdToken"]

      if(AllowOfflineTxForUnknownId != ""):
         if (AllowOfflineTxForUnknownId) == 'True':
            db.changeConfiguration('AllowOfflineTxForUnknownId', 1)
         else:
            db.changeConfiguration('AllowOfflineTxForUnknownId', 0)

      if(AuthorizationCacheEnabled != ""):
         if (AuthorizationCacheEnabled) == 'True':
            db.changeConfiguration('AuthorizationCacheEnabled', 1)
         else:
            db.changeConfiguration('AuthorizationCacheEnabled', 0)

      if(AuthorizeRemoteTxRequests != ""):
         if (AuthorizeRemoteTxRequests) == 'True':
            db.changeConfiguration('AuthorizeRemoteTxRequests', 1)
         else:
            db.changeConfiguration('AuthorizeRemoteTxRequests', 0)

      if(BlinkRepeat != ""):
         db.changeConfiguration('BlinkRepeat', BlinkRepeat)

      if(ClockAlignedDataInterval != ""):
         db.changeConfiguration('ClockAlignedDataInterval', ClockAlignedDataInterval)

      if(ConnectionTimeOut != ""):
         db.changeConfiguration('ConnectionTimeOut', ConnectionTimeOut)

      if(HeartbeatInterval != ""):
         db.changeConfiguration('HeartbeatInterval', HeartbeatInterval)

      if(LightIntensity != ""):
         db.changeConfiguration('LightIntensity', LightIntensity) 

      if(LocalAuthListEnabled != ""):
         if (LocalAuthListEnabled) == 'True':
            db.changeConfiguration('LocalAuthListEnabled', 1)
         else:
            db.changeConfiguration('LocalAuthListEnabled', 0)

      if(LocalAuthorizeOffline != ""):
         if (LocalAuthorizeOffline) == 'True':
            db.changeConfiguration('LocalAuthorizeOffline', 1)
         else:
            db.changeConfiguration('LocalAuthorizeOffline', 0)


      if(LocalPreAuthorize != ""):
         if (LocalPreAuthorize) == 'True':
            db.changeConfiguration('LocalPreAuthorize', 1)
         else:
            db.changeConfiguration('LocalPreAuthorize', 0)

      if(MaxEnergyOnInvalidId != ""):
         db.changeConfiguration('MaxEnergyOnInvalidId', MaxEnergyOnInvalidId) 
      
      if(MeterValuesAlignedData != ""):
         db.changeConfiguration('MeterValuesAlignedData', MeterValuesAlignedData) 

      if(MeterValuesSampledData != ""):
         db.changeConfiguration('MeterValuesSampledData', MeterValuesSampledData) 

      if(MeterValueSampleInterval != ""):
         db.changeConfiguration('MeterValueSampleInterval', MeterValueSampleInterval) 

      if(MinimumStatusDuration != ""):
         db.changeConfiguration('MinimumStatusDuration', MinimumStatusDuration) 

      if(ResetRetries != ""):
         db.changeConfiguration('ResetRetries', ResetRetries) 

      if(ConnectorPhaseRotation != ""):
         db.changeConfiguration('ConnectorPhaseRotation', ConnectorPhaseRotation) 


      if(StopTransactionOnEVSideDisconnect != ""):
         if (StopTransactionOnEVSideDisconnect) == 'True':
            db.changeConfiguration('StopTransactionOnEVSideDisconnect', 1)
         else:
            db.changeConfiguration('StopTransactionOnEVSideDisconnect', 0)

      if(StopTransactionOnInvalidId != ""):
         if (StopTransactionOnInvalidId) == 'True':
            db.changeConfiguration('StopTransactionOnInvalidId', 1)
         else:
            db.changeConfiguration('StopTransactionOnInvalidId', 0)

      if(StopTxnAlignedData != ""):
         db.changeConfiguration('StopTxnAlignedData', StopTxnAlignedData) 

      if(StopTxnSampledData != ""):
         db.changeConfiguration('StopTxnSampledData', StopTxnSampledData) 

      if(TransactionMessageAttempts != ""):
         db.changeConfiguration('TransactionMessageAttempts', TransactionMessageAttempts) 

      if(TransactionMessageRetryInterval != ""):
         db.changeConfiguration('TransactionMessageRetryInterval', TransactionMessageRetryInterval) 

      if(AllowOfflineTxForUnknownId != ""):
         if (UnlockConnectorOnEVSideDisconnect) == 'True':
            db.changeConfiguration('UnlockConnectorOnEVSideDisconnect', 1)
         else:
            db.changeConfiguration('UnlockConnectorOnEVSideDisconnect', 0)

      if(WebSocketPingInterval != ""):
         db.changeConfiguration('WebSocketPingInterval', WebSocketPingInterval)

      if(IdToken != ""):
         db.changeConfiguration('IdToken', IdToken)

      if(LastTagIdToken != ""):
         db.changeConfiguration('LastTagIdToken', LastTagIdToken)

      return redirect(url_for('show_change_config'))
   
@app.route('/about')
def about():
   return render_template("about.html")

if __name__=='__main__': 
   if(debug_mode == "debug"):
      app.run(host="0.0.0.0", debug=True)
   else:
      app.run(host="0.0.0.0") 
