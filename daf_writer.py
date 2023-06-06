import requests
from scanner import BLELS
from pymongo import MongoClient
from datetime import datetime
import time

# EDIT THIS FOR AZ
location = "AZ"

if location == "NS":
    CONTAINER_ID = 19
    EXPERIMENT_ID = 36
elif location == "AZ":
    CONTAINER_ID = 24
    EXPERIMENT_ID = 37
else:
    print("UNKNOWN LOCATION")
    exit()

# EDIT THIS 24-27 NS, 28-31 AZ
SENSOR_BOARD_ID = 24
COMPANY_ID = 8
CONTROLLER_ID = 15
SLEEP_TIME = 50
URL = 'https://data-analytic-framework.oa.r.appspot.com/api/v1/'
CONNECTION_STRING_MONGO =   "mongodb+srv://daf:MonBelLimar@dafreports.c1nehuc.mongodb.net/?retryWrites=true&w=majority"
CNT_NUMBER = 1000

def connect_mongo():
    return MongoClient(CONNECTION_STRING_MONGO)

def get_sensors():
    endpoint_url = f'{URL}sensors/board-search/{SENSOR_BOARD_ID}'
    
    sensors = requests.get(url = endpoint_url).json()['sensors']
    sensors_dict = {sensor['name']:sensor['id'] for sensor in sensors}
    return sensors_dict

scanner = BLELS()

cnt = 0
local_device_dict = {}
while True:
    print(f"ROUND: {cnt}")
    devices = scanner.scan()
    measurement_time = datetime.now()
    sensors_dict = get_sensors()
    items = []
    for device in devices:
        if device['addr'] not in sensors_dict:
            print(f"Device: {device['addr']} not a beacon or controller.")
            continue
        sensor_id = sensors_dict[device['addr']]
        item = {
            "value" : float(device['rssi']),                                              
            "sensor_id": sensor_id,
            "container_id": CONTAINER_ID,
            "experiment_id": EXPERIMENT_ID,
            "created_on": measurement_time,
            "company_id": COMPANY_ID,
            "sensor_board_id": SENSOR_BOARD_ID                                                    
            }
        print(item)
        items.append(item)
    if items:
        with connect_mongo() as conn:
            return_val = conn['daf']['reports_production3'].insert_many(items)
    # Local devices now
    cnt += 1
    for existing_device in local_device_dict:
        if existing_device in [device['addr'] for device in devices]:
            local_device_dict[existing_device].append(1)
        else:
            local_device_dict[existing_device].append(0)
    new_local_devices = {device['addr'] for device in devices}.difference(local_device_dict.keys())
    for new_device in new_local_devices:
        local_device_dict[new_device] = [1]
    if cnt >= CNT_NUMBER:
        cnt = 0
        print(local_device_dict)
        with open("local_logs.txt", "a") as local_file:
            local_file.write(datetime.now().isoformat() + "\n")
            for existing_device in local_device_dict:
                data_size = len(local_device_dict[existing_device])
                percentage = sum(local_device_dict[existing_device])/data_size
                if percentage > 0.8 and data_size/CNT_NUMBER > 0.5:
                    local_file.write(f"{existing_device}: {percentage}\n")
        local_device_dict = {}
    print(f"Sleeping for {SLEEP_TIME}s")
    time.sleep(SLEEP_TIME)