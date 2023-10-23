import os
import time
import math
import json
import random
import threading
import requests
from oneM2M_functions import *
import os
from dotenv import load_dotenv

load_dotenv()


server = os.getenv("ONEM2M_SERVER")
cse = os.getenv("CSE")
subscribe_link=os.getenv("SUBSCRIBE_LINK")

print(server)



def create_resource_tree(resource_tree_name):
    lbl_ae = ["Label-1", "Label-2"]
    if resource_tree_name == "":
        resource_tree_name = "DEFAULT_LOCATION"
    create_ae(server+cse, resource_tree_name, lbl_ae)



total = 0

def create_node(ae,node_container_name, sensor_label):

    global total
    lbl_cnt = ["CNT-Label-1", "CNT-Label-2"]
    create_cnt(server+cse+ae, node_container_name, lbl_cnt)   #node

    
    descriptor_container_name = "Descriptor"
    create_cnt(server+cse+ae + "/" + node_container_name, descriptor_container_name, lbl_cnt)  #descriptor

    data_container_name = "Data"
    create_cnt(server+cse+ae + "/" + node_container_name, data_container_name, lbl_cnt) #data

    content_instance = ""
    create_data_cin(server+cse+ae + "/" + node_container_name +"/"+ descriptor_container_name, content_instance, sensor_label) #descriptor container

    total +=1
    

    headers = {
            'X-M2M-Origin': 'admin:admin',
            'Content-Type': 'application/json;ty=23'
            } 
    payload = {
        "m2m:sub": {
            "rn": "Sub-DW",
            "nct": 2,
            "nu": subscribe_link
        }
    }

    response = requests.request("POST", server+cse+ae + "/" + node_container_name +"/"+ data_container_name, headers=headers, json=payload)
    return response.text



def create_mock_devices():  
    # Opening JSON file
    f = open('sensor_config.json')
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    sensor_url_data = {}
    
    # Iterating through the json
    # list
    for location_data in data['Sensor_meta']:
        # print(i)
        create_resource_tree(location_data['Location'])
        # print(f' location = {location_data['Location']}')
        for sensor in location_data['Sensors']:
            print(sensor['sensor_id'])
            print(sensor['sensor_label'])
            create_node(location_data['Location'],sensor['sensor_id'], sensor['sensor_label'])
            sensor_ob = {
                "url": server +cse + location_data['Location'] +'/'+ sensor['sensor_id'] + '/Data',
                "sensor_label": sensor['sensor_label'],
            }
            sensor_url_data[sensor['sensor_id']] = sensor_ob
            # break
        # break
    
    f.close()
    
    with open("sensor_url_data.json", "w") as outfile:
        json.dump(sensor_url_data, outfile)


create_mock_devices()

print(f'total devices = {total}')