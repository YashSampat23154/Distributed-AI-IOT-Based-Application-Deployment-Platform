from flask import Flask, request, jsonify
import requests
import os 
import jsonschema
import json
import time
import certifi
from pymongo import MongoClient
from new_kf_handler import Producer, Consumer

MONGO_CONNECTION_URL = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "IAS_test_1"

mongo = MongoClient(MONGO_CONNECTION_URL, tlsCAFile=certifi.where())
db = mongo[MONGO_DB_NAME]
serviceRegistory = db["service_registry"]
containerDetails = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'api-gateway'})
print(containerDetails)
ipPort = containerDetails['ip'] + ":" + str(containerDetails['port'])
bootstrap_servers = [ipPort]

class Lib:
    # library function required by app server code to fetch the response for 
    # workflow after been received the requestId 
    
    def getResponse(self,requestId):
        col = db["responses"]

        response_data = None
        while response_data == None:
            response_data = col.find_one({"requestId" : requestId})
            print(response_data)
            time.sleep(10)
            
        return response_data

    # in the workflow to call various services use this library function
    # follow the req metadata: appId, serviceName, requestData(for the service)
    def serviceReq(self,requestData):
        # api gateway url which will then forward to ip:port of the service container 
        # and then sendback the response

        serviceRegistory = db["service_registry"]
        IPPort = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'api-gateway'})
        print(IPPort)

        headers = {'Content-type': 'application/json'}

        url = f"http://{IPPort['ip']}:{IPPort['port']}/services"
        response = requests.post(url, data = json.dumpss(requestData), headers=headers)
        return (response.content, response.status_code, response.headers.items())


    def temp(self,request):
        req = request.get_json()
        appId = req["appId"]
        name = req["serviceName"]
        data = req["requestData"]

        serviceRegistory = db["service_registry"]
        IPPort = serviceRegistory.find_one({'app_name': appId, 'service_name' : name})

        url = f"http://{IPPort['ip']}:{IPPort['port']}/services"
        response = requests.post(url, data = jsonify(data))
        return (response.content, response.status_code, response.headers.items())

    def get_topics(self,app_id,service,location):
        serviceRegistory = db["service_registry"]
        IPPort = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'api-gateway'})
        #request to api gateway
        # !path

        url = f"http://{IPPort['ip']}:{IPPort['port']}/get_registered_topics"
        data1={"app_id":app_id,"service":service}
        response = requests.post(url, data = data1)
        kafka_topics={}
        for key in response.keys():
            kafka_topics[key]=[]
            for j in response[key]:
                if location in j and service in j:
                    kafka_topics[key].append(j)
        return kafka_topics


    def fetch_data_object(self,topics):
        serviceRegistory = db["service_registry"]
        IPPort = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'api-gateway'})
        #request to api gateway
        # !path
        # url = f"http://{IPPort['ip']}:{IPPort['port']}/services"
        # response = requests.post(url, data = jsonify(data))
        topics_list=[]
        for key in topics.keys():
            for j in topics[key]:
                    topics_list.append(j)
        consumer = Consumer(bootstrap_servers=bootstrap_servers, topic=topics, group_id="consumer-group-a")
        return [len(topics_list),consumer]


