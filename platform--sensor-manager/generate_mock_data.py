import logging
import json
import time
import requests
import random
import threading

def generate_sensor_data(sensor_id):
    f = open('sensor_url_data.json')
    data = json.load(f)
    sensor_data = data[sensor_id]
    f.close()

    url = sensor_data['url']
    sensor_label = sensor_data['sensor_label']

    no_of_params = len(sensor_label)
    _data_cin = [int(time.time()), random.randint(0, 1)]
    
    for count in range(no_of_params-2):
        _data_cin.append(random.randint(1, 400))
    
    headers = {
      'X-M2M-Origin': 'admin:admin',
      'Content-Type': 'application/json;ty=4'
    }  
    payload = {
        "m2m:cin": {
            "con": "{}".format(_data_cin),
            "lbl": sensor_label,
            "cnf": "text"
        }
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.text)
    return response.status_code

def generate_live_sensor_data(sensor_id, delay):
    for i in range(3):
        generate_sensor_data(sensor_id)
        time.sleep(delay)
        
f = open('sensor_url_data.json')
data = json.load(f)
f.close()

for sensor in data:
    t = threading.Thread(target=generate_live_sensor_data, args=(sensor, 10))
    t.start()