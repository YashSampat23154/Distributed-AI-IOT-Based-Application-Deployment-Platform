from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/get_sensors', methods=['GET', 'POST'])
def get_sensors():
    f = open('sensor_url.json')
    data = json.load(f)
    # print(data)
    return jsonify(data)



@app.route('/get_nodes')
def get_nodes():
    import json
    f = open('nodes_url.json')
    data = json.load(f)
    # print(data)
    return jsonify(data)

@app.route('/get_locations')
def get_loc():
    import json
    f = open('locations.json')
    data = json.load(f)
    # print(data)
    return jsonify(data)

@app.route('/get_sensor_description', methods=['GET', 'POST'])
def get_description():
    sensor_instance = request.args.get('instance')
    # print(sensor_instance)
    f = open('descriptor_url.json')
    data = json.load(f)
    # print(data)
    return jsonify(data[sensor_instance])

@app.route('/channels/<sensor_instance>', methods=['GET', 'POST'])
def send_data(sensor_instance):
    # print(sensor_instance)
    with open(os.path.join(os.getcwd(), "SENSOR_DATA", sensor_instance+".json"), 'r') as openfile:
         json_object = json.load(openfile)
 
    # print(json_object)
    return json_object






import pymongo
from pymongo import MongoClient
import json
import time
import threading
from datetime import datetime
import os
from env import config
# print(datetime.utcnow().isoformat())
# print(datetime.utcnow().replace(tzinfo=pytz.utc))

mongo_uri = config ['mongouri']
client = MongoClient()
db=client['platform']
coll=db['sensor_application_mapping']
topic_coll=db['user_topics']
meta_col=db['meta']
sensors=db['sensors']
sensors_instances_meta=db['sensors_instances_meta']


def generate_sensor_data(sensor_instance_name, delay, data, second_data):
    
    sensor_data_response = {}
    # f = open(os.path.join(os.getcwd(), "SENSOR_DATA", sensor_instance_name+".json"), "w")
    # f.close()
    sensor_data_response['channel']={}
    sensor_data_response['feeds']=[]
    sensor_data_response['channel']['id']=sensor_instance_name


    data_count = 0
    while(True):
        data_ob = {
            "created_at" : int(time.time())
        }

        if data_count%7==0:
            data,second_data = second_data,data
        data_ob["field1"] = data    
        
        sensor_data_response['feeds'] = [data_ob] + sensor_data_response["feeds"]
        # print(sensor_data_response)

        with open(os.path.join(os.getcwd(), "SENSOR_DATA", sensor_instance_name+".json"), "w") as outfile:
            json.dump(sensor_data_response, outfile)
        data_count +=1
        time.sleep(delay)


# generate_sensor_data("SE-01-H101", 1, 7)

sensor_list = [
    {
        "sensor" : "SE-01-H101",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "SE-02-H101",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "SE-03-H101",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "SE-01-H102",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "SE-02-H102",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "SE-03-H102",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "AQ-01-H101",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "AQ-02-H101",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "AQ-03-H101",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "AQ-01-H102",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "AQ-02-H102",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "AQ-03-H102",
        "data": 7,
        "second_data": 4
    },
    {
        "sensor" : "REM-01-H101",
        "data": 1,
        "second_data": 0

    },
    {
        "sensor" : "REM-01-H102",
        "data": 1,
        "second_data": 0
    },
]

for sensor in sensor_list:
    threading.Thread(target=generate_sensor_data, args=(sensor['sensor'],10,sensor['data'], sensor['second_data'])).start()


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True,port=5000)