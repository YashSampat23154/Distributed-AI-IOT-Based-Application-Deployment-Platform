import sys
from kafka import KafkaConsumer
from kafkaHandler import Producer, Consumer
import json
import datetime
import os
from dotenv import load_dotenv


MONGO_SERVER_URL = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "IAS_test_1"
client = pymongo.MongoClient(MONGO_SERVER_URL)
db = client[MONGO_DB_NAME]
serviceRegistory = db["service_registry"]
containerDetails = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'kafka'})
kafkaIp = containerDetails['ip']
kafkaPortNo = str(containerDetails['port'])
ipport=str(kafkaIp) +":"+ str(kafkaPortNo)

#------------------------------------------------



class request_for_deployer():
    def __init__(self):
        # load_dotenv()
        self.bootstrap_servers = [ipport]
        self.producer = Producer(bootstrap_servers=self.bootstrap_servers)
        self.name_of_topic_sched = "PRODUCER_TO_DEPLOYER"
    def send(self,json_message):
        self.producer.send_message(self.name_of_topic_sched,json_message)
    #//* ALSO ADD PRODUCER FOR LOG FILE load_dotenv()

    pass


if __name__ == "__main__":
    try:
        #// SETTING THE SYS ARGS OF THE BASH FILE"""

        n = len(sys.argv)
        appId=sys.argv[1]
        appName=sys.argv[2]
        scheduleType=sys.argv[3]
        accessToken=sys.argv[4]
        services=[]
        for i in range(5, n):
            services.append(sys.argv[i])
        #// CREATING A DICT AND OBTAINING A JSON
        dict_for_request={}
        dict_for_request["appId"]=appId
        dict_for_request["appName"]=appName
        dict_for_request["scheduleType"]=scheduleType
        dict_for_request["accessToken"]=accessToken
        dict_for_request["serviceName"]=services
        json_for_request=dict_for_request
        
        #// MAKE A OBJECT AND SEND REQUEST TO DEPLOYER
        rfd=request_for_deployer()
        rfd.send(json_for_request)
    except Exception as e:
        with open("../logerror.txt","a") as file:
            err_log="Error occured @"+str(datetime.datetime.now())+" error is "+ str(e)
            file.write(err_log)