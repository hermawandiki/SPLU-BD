import mysql.connector
import datetime

mydb = mysql.connector.connect(
    host = "localhost",
    user = "splu_user",
    password = "splu_pass",
    database = "splu"
)   

if(mydb):
    print("Connected")

mycursor = mydb.cursor()

# AUTHORIZATIONS   
def store_auth_cache(id):
    query = "INSERT INTO authorizationcache (AuthorizationCache) VALUES ('{}');".format(id)
    mycursor.execute(query)
    mydb.commit()

def clear_auth_cache():
    query = "DELETE FROM authorizationcache"
    mycursor.execute(query)
    mydb.commit()

def check_id_in_auth_cache(id):
    lists = []
    query = "select count(AuthorizationCache) from authorizationcache"
    mycursor.execute(query)
    index = mycursor.fetchall()[0][0]

    query = "select AuthorizationCache from authorizationcache"

    for i in range(index):
        mycursor.execute(query)
        lists.append(mycursor.fetchall()[i][0])

    if str(id) in lists:
        mydb.commit()
        return True

def check_auth_id(id):
    lists = []
    query = "select count(AuthorizationCache) from authorizationcache"
    mycursor.execute(query)
    index = mycursor.fetchall()[0][0]

    query = "select AuthorizationCache from authorizationcache"

    for i in range(index):
        mycursor.execute(query)
        lists.append(mycursor.fetchall()[i][0])

    if str(id) in lists:
        mydb.commit()
        return True

# CONFIGURATION
def getConfiguration(key):
    # keys = []
    # for key in keys:
    mycursor.execute("SELECT {} FROM configcp WHERE idconfig = 1".format(key))
    result = mycursor.fetchone()[0]
    mydb.commit()
    # keys.append(str(mycursor.fetchone()[0]))
    return result

    # return keys

def changeConfiguration(key, value):
    query = "UPDATE configcp set {} = {} where idconfig = 1;".format(str(key), str(value))
    mycursor.execute(query)
    mydb.commit()

    if (getConfiguration(key) == value):
        return True

# CONNECTORS
def update_availability(id, availability):
    query = "update connector set status = '" + str(availability) + "' where id = " + str(id)
    mycursor.execute(query)
    mydb.commit()

def check_if_operative(id, gui=False):
    query = "select status from connector where id = " + str(id)
    mycursor.execute(query)
    result = mycursor.fetchall()

    #mydb.commit()
    if(gui == True):
        if(result[0][0] == "Operative"): 
            return "Available"
        elif(result[0][0] == "Inoperative"): 
            return "Unavailable"

    else:
        return result[0][0]

def check_switchpos(id):
    mycursor = mydb.cursor()
    query = "select switchpos from connector where id = " + str(id)
    mycursor.execute(query)
    result = mycursor.fetchone()[0]
    mydb.commit()
    return result

def update_switchpos(id, switchpos):
    # switchpos close = 0
    # switchpos open = 1
    if switchpos == 0:
        query = "update connector set switchpos = 'Close' where connector = " + str(id)
        mycursor.execute(query)
        mydb.commit()

    elif switchpos == 1:
        query = "update connector set switchpos = 'Open' where connector = " + str(id)
        mycursor.execute(query)
        mydb.commit()

def update_all_switchpos(switchpos):
    # switchpos close = 0
    # switchpos open = 1
    if switchpos == 0:
        query = "update connector set switchpos = 'Close'"
        mycursor.execute(query)
        mydb.commit()

    elif switchpos == 1:
        query = "update connector set switchpos = 'Open'"
        mycursor.execute(query)
        mydb.commit()

# LOCAL LIST
def insert_local_lists(list_version, local_authorization_list):
    for i, list in enumerate(local_authorization_list):
        insert_local_list(list_version, local_authorization_list[i])

def insert_local_list(list_version, list_auth):
    list_version = int(list_version)
    id_tag = list_auth['id_tag']
    status = list_auth['id_tag_info']['status']

    expiry_date = list_auth['id_tag_info']['expiry_date']
    format = "%Y-%m-%dT%H:%M:%S.%fZ"
    new_format = "%Y-%m-%d"
    expiry_date = datetime.datetime.strptime(expiry_date, format).strftime(new_format)
    # print("masuk fungsi")
    if len(list_auth['id_tag_info']) == 2:
        # print("masuk dua")
        query = "INSERT INTO locallist (listVersion, idTag, status, expirydate) VALUES ({}, '{}', '{}', '{}');".format(list_version, id_tag, status, expiry_date)      
        mydb.commit()
        # print(("INSERT INTO locallist (listVersion, idTag, status, expirydate) VALUES({}, {}, {}, {});").format(list_version, id_tag, status, expiry_date))
    elif len(list_auth['id_tag_info']) == 3:
        # print("masuk tiga")
        parent_id_tag = list_auth['id_tag_info']['parent_id_tag']
        query = "INSERT INTO locallist (listVersion, idTag, status, expirydate, parentIdTag) VALUES ({}, '{}', '{}', '{}', '{}');".format(list_version, id_tag, status, expiry_date, parent_id_tag)     
        mydb.commit()   
        # print(("INSERT INTO locallist (listVersion, idTag, status, expirydate, parentIdTag) VALUES({}, {}, {}, {}, {});").format(list_version, id_tag, status, expiry_date, parent_id_tag))

    mycursor.execute(query)
    mydb.commit()

def check_if_id_exists(id):
    lists = []
    query = "select count(idTag) from locallist"
    mycursor.execute(query)
    index = mycursor.fetchall()[0][0]

    query = "select idTag from locallist"

    for i in range(index):
        mycursor.execute(query)
        lists.append(mycursor.fetchall()[i][0])

    if str(id) in lists:
        mydb.commit()
        return True
    
def check_id_status(id):
    query = "select status from locallist where idTag = " + str(id)
    mycursor.execute(query)
    result = mycursor.fetchall()
    mydb.commit()
    return result[0][0]

def check_kwh_quota(id):
    query = "select meterQuota from locallist where idTag = " + str(id)
    mycursor.execute(query)
    result = mycursor.fetchall()
    mydb.commit()
    return result[0][0]

def set_kwh_quota(id, value):
    query = "update locallist set meterQuota = " + str(value) + " where idTag = " + str(id)
    mycursor.execute(query)
    mydb.commit()

def add_new_idtag(id):
    query = "INSERT INTO locallist (listVersion, idTag, status, expirydate) VALUES ({}, '{}', '{}', '{}');".format(0, id, "Accepted", "2024-12-31")
    mycursor.execute(query)
    mydb.commit()

    if(check_if_id_exists(id)):
        return True

# TRANSACTIONS
def start_transaction(transaction_id, id_tag, connector_id, meter_start, date_time, transaction_id_cs=None):
    if(transaction_id_cs == None):
        query = "INSERT INTO transactions (transactionId, idTag, connector, meterStart, timeStart) VALUES ({}, '{}', {}, {}, '{}');".format(transaction_id, id_tag, connector_id, meter_start, date_time)
    else:
        query = "INSERT INTO transactions (transactionId, idTag, connector, meterStart, timeStart, transactionIdCS) VALUES ({}, '{}', {}, {}, '{}', {});".format(transaction_id, id_tag, connector_id, meter_start, date_time, transaction_id_cs)
    
    mycursor.execute(query)
    mydb.commit()

def update_transaction_id(transaction_id, transaction_id_cs):
    query = "UPDATE transactions SET transactionIdCS = {} WHERE transactionId = {};".format(transaction_id_cs, transaction_id)
    mycursor.execute(query)
    mydb.commit()

def get_latest_id():
    query = "SELECT MAX(id) from transactions;"
    mycursor.execute(query)
    result = mycursor.fetchall()[0][0]
    mydb.commit()
    return result

def stop_transaction(meter_stop, date_time, id_tag=None, transaction_id_cs=None):
    if(transaction_id_cs != None):
        query = "UPDATE transactions SET meterStop = {}, timeStop = '{}' WHERE transactionIdCS = {};".format(meter_stop, date_time, transaction_id_cs)
    elif(id_tag != None):
        query = "UPDATE transactions SET meterStop = {}, timeStop = '{}' WHERE (idTag = '{}' AND meterStop IS NULL);".format(meter_stop, date_time, id_tag)

    mycursor.execute(query)
    mydb.commit()

def delete_transaction(transaction_id_cs):
    query = "DELETE FROM transactions WHERE transactionIdCS = {};".format(transaction_id_cs)
    mycursor.execute(query)
    mydb.commit()


#============================== FIND VALUES ==============================?
def find_values(table, column, *argv, **kwargs):
    query = "SELECT {} FROM {} WHERE ".format(column, table)
    if len(argv) >= 1:
        query += "{} = {}".format(argv[0], argv[1])
    query += ";"

    # print(query)
    mycursor.execute(query)
    result = mycursor.fetchone()[0]
    mydb.commit()

    return result

#============================== CHANGE DETAIL CP ============================#
def change_values(key, value):
    query = "UPDATE detailcp set {} = '{}' where id = 2;".format(str(key), str(value))
    mycursor.execute(query)
    mydb.commit()

    if (find_values("detailcp", key, "id", 2) == value):
        return True


#============================ VARIABLES =================================#

meter_values_sampled_data = mycursor.execute("SELECT MeterValuesSampledData FROM configcp WHERE idconfig = 1")
meter_values_sampled_data = mycursor.fetchone()[0]
meter_values_sampled_data = meter_values_sampled_data.split(',')


#============================ ADD ON ======

def change_online_status(status):
    try:
        mycursor = mydb.cursor()
        mycursor.execute(
            "UPDATE chargebox SET online_status = %s WHERE id = 1",
            (status,)
        )
        mydb.commit()
    except Exception as e:
        print("DB change_online_status error:", e)

