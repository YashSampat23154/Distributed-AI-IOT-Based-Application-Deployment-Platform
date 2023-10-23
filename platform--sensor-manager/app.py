from flask import Flask, jsonify, request, render_template
import sys
import json
import pymongo
from pymongo import MongoClient
import threading
from kafka import KafkaProducer,KafkaConsumer
import re
from kafka.admin import KafkaAdminClient, NewTopic
import logging
import certifi
import requests
from collections import defaultdict
import datetime
from time import sleep
import time
import threading
from datetime import datetime, timezone
# import numpy as np
from env import config

MAX_SIZE_COLL = 10000

######### INTEGRATION GLOBALS ########
import os

node_name = os.getenv('node_name')
container_name = os.getenv('container_name')
container_up_time = os.getenv('container_up_time')
####################################

from pymongo import MongoClient
MONGO_CONNECTION_URL = config['MONGO_CONNECTION_URL']
MONGO_DB_NAME = config['MONGO_DB_NAME']
mongo = MongoClient(MONGO_CONNECTION_URL, tlsCAFile=certifi.where())
db = mongo[MONGO_DB_NAME]

serviceRegistory = db["service_registry"]
containerDetails = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'kafka'})

kafkaIp = containerDetails['ip']
kafkaPortNo = str(containerDetails['port'])

sensorApiGateway = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'sensor-api-gateway'})
proxy = "http://"+ sensorApiGateway['ip'] + ":" + str(sensorApiGateway["port"])

######### INTEGRATION FUNCTIONS #########
def sendheartBeat(kafkaTopicName, containerName, node_name) : 

    producer = KafkaProducer(bootstrap_servers=[kafkaIp+":"+kafkaPortNo],api_version=(0, 10, 1))
    
    heartbeat = {
        "container_name" : containerName,
        "node_name" : node_name,
    }

    # i = 1

    while True:
        try:
            heartbeat["current_time"] = time.time()
            producer.send(kafkaTopicName, json.dumps(heartbeat).encode('utf-8'))
            # print("heartbeatsent",i)
            # i += 1
        except:
            pass

        sleep(60)

heartbeat_thread = threading.Thread(target=sendheartBeat, args=("heartbeat-monitoring", container_name, node_name, ))

# kafkaIp = "localhost"
# kafkaPortNo = "9092"
producerForLogging = KafkaProducer(bootstrap_servers=[kafkaIp+":"+kafkaPortNo],api_version=(0, 10, 1))


# Send the logging message for logging. 
def log_message(subsystem, severity, msg):

    cur_time = datetime.now()

    log_entry = {
        "subsystem_name" : subsystem,
        "container_up_time" : container_up_time, 
        "date": cur_time.strftime("%Y-%m-%d"),
        "time": cur_time.strftime("%H:%M:%S"),
        "severity": severity,
        "message": msg
    }

    while True:
        try:
            producerForLogging.send("log-"+subsystem, json.dumps(log_entry).encode('utf-8'))
            break
        except:
            pass
#########################################


######## LOGGING SUPPORT ###################

def follow():
    fname = open ("sensor.log","r")
    fname.seek(0, os.SEEK_END)
    while True:
        line = fname.readline()      
        if not line:
            time.sleep(0.1)
            continue

        log_message ('platform-sensor-manager', 'DEBUG', line)

follow_thread = threading.Thread (target=follow)
###############################################

logging.basicConfig(filename="sensor.log",level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
def get_epoch_time (timestring):
    dtformat = datetime.strptime (timestring, "%Y-%m-%dT%H:%M:%S")
    epochtime = (dtformat - datetime(1970, 1, 1, tzinfo = timezone.utc)).total_seconds()
    return int (epochtime)

def get_data_from_req(channel):
    print("Data request from ", channel)
    curr_date_time=datetime.now()
    date,time=str(curr_date_time).split()
    
    new_url = proxy + config ['data_channels']+channel
    response = requests.request("GET", new_url)
    res=response.json()
    channels=res['channel']
    feeds=res['feeds']
    node_label=channel+"$"
    data={}
    data_db={}
    for keys in feeds[0].keys():
        if str(keys).startswith('field') and channels.get(keys) != None:
            data[channels[keys]]=feeds[0][keys]
            data_db[channels[keys]]=feeds[0][keys]
        else:
            data[keys]=feeds[0][keys]
            data_db[keys]=feeds[0][keys]
            if keys == "created_at" :
                data['epoch_time']=feeds[0][keys]
                data_db['epoch_time']=feeds[0][keys]

    ls=list(topic_coll.find({'topic_name': {'$regex': re.compile(r""+node_label)}}))
    
    for x in ls:
        threading.Thread( target = dump_data , args=(x['topic_name'],data)).start()
    
    try:       
        db.validate_collection(channel)
    except pymongo.errors.OperationFailure:
        print("Creating collection: ", channel)
        db.create_collection (channel, capped=True, size=MAX_SIZE_COLL)    
    db[channel].insert_one(data_db)

def get_last_k (k, channel):
    mongo_cursor = db [channel].find ().sort ([('epoch_time', pymongo.DESCENDING)])
    items_list = list (mongo_cursor)

    return items_list [:k]

def get_data():
    while True:
        topics=list(topic_coll.find())
        topic_set={i['topic_name'].split('.')[-1] for i in topics}
        for topic in topic_set:
            # print("Fetching Data : ", topic)  
            threading.Thread (target=get_data_from_req,kwargs={'channel':topic}, daemon=True).run()
        sleep(10)


mongo_uri = config ['mongouri']
kafka_platform_ip = kafkaIp + ':' + kafkaPortNo
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())

db=client['platform']
coll=db['sensor_application_mapping']
topic_coll=db['user_topics']
meta_col=db['meta']
sensors=db['sensors']
sensors_instances_meta=db['sensors_instances_meta']

#DATA API SAMPLE QUERY
# https://iudx-rs-onem2m.iiit.ac.in/channels/WM-WF-PH03-00/feeds?start=2023-01-06T20:20:01Z
# config ['data_channels'] + sensor_id + '/feeds?start=' + datetime_tzformat

app = Flask(__name__)

try:
    admin_client = KafkaAdminClient(bootstrap_servers=[kafka_platform_ip],)
    print("Kafka connected :", kafka_platform_ip)
except Exception as e:
    print ("KAFKA connection failure:" , e)

def getAllSensors():
    new_url = proxy+config ['sensors_url']
    response = requests.request("GET", new_url)
    print("Fetching all sensors")
    return response.json()

def getAllNodes():
    new_url = proxy+config ['nodes_url']
    response = requests.request("GET", new_url)
    print("Fetching all nodes")
    # print(response.json())
    return response.json()

def get_sensor_descriptor(instance):
    new_url= proxy+config['descriptor_url']+"?instance="+instance
    response = requests.request("GET",new_url)
    print("Fetching description: ", instance)
    return response.json()

def add_instance_to_db(d):
    desc=get_sensor_descriptor(d["sensor_instance_name"])
    # d["Latitude"]=desc["Node Location"]["Latitude"]
    # d["Longitude"]=desc["Node Location"]["Longitude"]
    d["location"]=desc["location"]

    sensors_instances_meta.insert_one(d)
    print("Adding sensor instance to database: ", d['sensor_instance_name'])

def init():
    print("Initializing Sensor Manager")
    
    sensors_meta=getAllSensors()
    sensors.drop()
    for i in sensors_meta.keys():
        sensors.insert_one({"sensor_name":i,"labels":sensors_meta[i]})
    sensors_instance=getAllNodes()
    sensors_instances_meta.drop()
    sensor_meta_dict=defaultdict(list)
    for attr in sensors_instance:
        for instances in sensors_instance[attr]:
            sensor_meta_dict[instances].append(attr)
    for keys in sensor_meta_dict:
        sensor_type=keys.split('-')[0]
        threading.Thread( target = add_instance_to_db , kwargs={"d":{"sensor_instance_name":keys,"sensor_type":sensor_type,"labels":sensor_meta_dict[keys]}}).start()
    print("Initialization Completed")

def dump_data(topic, data ): 
    # print("Producing data in:", topic)
    producer = KafkaProducer(bootstrap_servers=[kafka_platform_ip])
    producer.send(topic, bytes(str(data),"utf-8")) 
    producer.flush()

def get_distance(x1,y1, x2, y2):
    return ((float(x1)-float(x2))**2+(float(y1)-float(y2))**2)**0.5	

def get_nearest_sensor(latitude,longitude,sensors,k=10):
    sensors_instances=[]
    for i in sensors:
        sensors_instances.append(i['sensor_instance_name'])
    
    if len(sensors)<=k:
        return sensors_instances
    else:
        sensors_dist=[]
        for i in sensors:
            sensors_dist.append(get_distance(latitude,longitude,i['Latitude'],i["Longitude"]))
        sensors_instances=np.array(sensors_instances)
        return list(sensors_instances[np.argsort(sensors_dist)[:k]])
    
def get_services_sensors(app_id,services):
    service_list=[]
    topics_name=[]
    location_data = requests.request("GET", proxy+config['location_url'])
    location_data=location_data.json()
    print(location_data['locations'])
    try:
        for data in services:
            services_sensors={}
            services_sensors['service']=data['name']
            services_sensors['sensor']=data ['sensors']
            services_sensors['topic_list']={}
            for sensor in services_sensors['sensor']:
                topic_instance=[]
                sensor_type=sensor['sensor_type']
                num_of_sensors=sensor["num_of_sensors"]
                # latitude=sensor['Latitude']
                # longitude=sensor['Longitude']
                for location in location_data['locations']:
                    # location = sensor["location"]
                    # sensorlist=list(sensors_instances_meta.find({'sensor_type': sensor_type },{"sensor_instance_name":1,"Latitude":1,"Longitude":1}))
                    sensorlist=list(sensors_instances_meta.find({"$and":[{"sensor_type": sensor_type}, {"location": location}]}))
                    required_sensors = min(len(sensorlist), num_of_sensors)
                    sensorlist = sensorlist[:required_sensors]
                    for sensor_instance in sensorlist:
                        topic = app_id + "." + services_sensors['service'] + "." + sensor_instance['sensor_instance_name']
                        topics_name.append({"topic_name":topic,"app_id":app_id,"service_id":services_sensors['service'],"sensor_id":sensor_instance['sensor_instance_name'],"sensor_type":sensor_type})
                        topic_instance.append(topic)

                    # for sensor_instance in  get_nearest_sensor(latitude,longitude,sensorlist,num_of_sensors):
                    #     topic=app_id+"."+services_sensors['service']+"."+sensor_instance
                    #     topics_name.append({"topic_name":topic,"app_id":app_id,"service_id":services_sensors['service'],"sensor_id":sensor_instance,"sensor_type":sensor_type})
                    #     topic_instance.append(topic)
                    services_sensors['topic_list'][sensor_type]=topic_instance
            service_list.append(services_sensors)
    except Exception as e:
        print("Error in creating service topics: ",e)
    return service_list,topics_name
        

def add_topics_to_db(topics):
    user_topics=[]
    topics_list=[]
    topic_set=set(admin_client.list_topics())
    print(topic_set)
    for i in topics:
        topic=list(topic_coll.find(i))
        if len(topic) == 0:
            topic_coll.insert_one(i)
            user_topics.append(i['topic_name'])
            if i['topic_name'] not in topic_set:
                print("topic name: ",i['topic_name'])
                topics_list.append(NewTopic(name=i['topic_name'], num_partitions=2, replication_factor=1))
    return topics_list,user_topics

# def create_kafka_topics(topic_list):
#     try:
#         admin_client.create_topics(new_topics=list(topic_list), validate_only=False)
#         print("Kafka topicz created")
#     except:
#         print("TOPIC CREATION FAILURE")

@app.route('/register', methods=['GET', 'POST'])
def register():
    data = request.get_json()
    print("data", data)
    # data=json_data['Application']
    user_id = data['developer_id']
    app_id = data['appId']

    services,user_topics=get_services_sensors(app_id,data['services'])
    doc=list(coll.find({"app_id":app_id}))
    if len(doc)>0:
        coll.update_one({"app_id":app_id},{"$set":{"app_id":app_id,"user_id":user_id,"services":services}})
    else:
        coll.insert_one({"app_id":app_id,"user_id":user_id,"services":services}).inserted_id
    topics_list,user_topics=add_topics_to_db(user_topics)   
    
    if len(topics_list) > 0:
        try:
            admin_client.create_topics(new_topics=topics_list, validate_only=False)
        except:
            print("TOPIC CREATION FAILURE")

    res = {"app_id":app_id,"user_id":user_id,"topics":user_topics,"services":services}
    print("App Registered: ", app_id)
    print("res", res)
    return res

@app.route('/get_registered_topics', methods=['GET', 'POST'])
def get_registered_topics():
    data=request.get_json()
    print(data)
    app_id = data['app_id']
    service_name= data['service']
    res=list(coll.find({"app_id":app_id}))
    if len(res) == 0:
        return { "Error": "App not found"}
    app_data = res[0]
    topics = {}
    for service_ob in app_data['services']:
        if service_ob['service'] == service_name :
            topics = service_ob['topic_list']
            break
    print('Sending registered topics for: ', app_id)
    return topics


init()
# def get_services_sensors_beta (app_id, services):
#     service_list=[]
#     topics_name=[]
    
#     for data in services:
#         services_sensors={}
#         services_sensors['service']=data['servicename']
#         services_sensors['sensor']=data ['sensor']

#         for sensor in services_sensors['sensor']:
#             sensor_id=sensor['sensor_id']
#             topic=app_id+"-"+services_sensors['service']+"-"+sensor_id
#             topics_name.append({"topic_name":topic})
            
#         service_list.append(services_sensors)
#     return service_list,topics_name

# @app.route('/register-beta', methods=['GET', 'POST'])
# def fun_beta():
#     json_data = request.get_json()
#     data=json_data['Application']
#     user_id = data['username']
#     app_id = data['application_id']
#     services,user_topics=get_services_sensors(app_id,data['services'])
#     doc=list(coll.find({"app_id":app_id}))
#     if len(doc)>0:
#         coll.update_one({"app_id":app_id},{"$set":{"app_id":app_id,"services":services}})
#     else:
#         coll.insert_one({"app_id":app_id,"services":services}).inserted_id
#     topics_list,user_topics=add_topics_to_db(user_topics)    
#     if len(topics_list) > 0:
#         admin_client.create_topics(new_topics=topics_list, validate_only=False)
        
#     res = {"app_id":app_id,"topics":user_topics,"services":services}
#     return res

# @app.route('/data', methods=['GET' ,'POST'])
# def data():
#     data = request.get_json()
#     data=data['m2m:sgn']
#     if data.get('m2m:vrq') != None:
#         verification_req=data['m2m:vrq']
#         msg="already verified"
#         if verification_req :
#             print("Verification Request Recived")
#             msg="success"
#         res = {
# 			'message' : msg,
# 		}
#         return jsonify(res)
#     else:
#         data=data['m2m:nev']['m2m:rep']['m2m:cin']
#         labels=data["lbl"]
#         node_label=labels[0]
#         labels = labels[1:]
#         print(node_label+" data recieved")
#         data_con = eval(data["con"])
#         sensor_data=dict(zip(labels, data_con))
        
#         node_label1=node_label+"$"
#         ls=list(topic_coll.find({'topic_name': {'$regex': re.compile(r""+node_label1)}}))
#         for x in ls:
#             t = threading.Thread( target = dump_data , args=(x['topic_name'],sensor_data))
#             t.start()
#         print("Success")
#         db[node_label].insert_one(sensor_data)
#         return {"msg":"success"}

@app.route ('/display', methods=['GET', 'POST'])
def display ():
    upload_data = list(sensors_instances_meta.find())
    # print (upload_data)
    return render_template ('sensors.html', sensorlist = upload_data)



# heartbeat_thread.run ()
# follow_thread.run ()
threading.Thread (target=get_data, daemon=True).start()

if __name__ == '__main__':
    print("running")
    print("Running 5000")
    app.run(host="0.0.0.0", debug=False,port=5000)   
