from kafka import KafkaProducer
from datetime import datetime
import json
from pymongo import MongoClient
from globalVariables import *

MONGO_CONNECTION_URL = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "IAS_test_1"
mongo = MongoClient(MONGO_CONNECTION_URL)
db = mongo[MONGO_DB_NAME]

serviceRegistory = db["service_registry"]
containerDetails = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'kafka'})
print(containerDetails)

kafkaIp = containerDetails['ip']
kafkaPortNo = str(containerDetails['port'])
print(kafkaIp, kafkaPortNo)

kafka_string = kafkaIp + ":" + kafkaPortNo
# kafka_server_main = [kafka_string]


# kafkaIp = "20.2.81.4"
# kafkaPortNo = "19092"
producerForLogging = KafkaProducer(bootstrap_servers=[kafka_string],api_version=(0, 10, 1))


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


# Subsystem names should be : 
# For Monitoring : monitoring
# For Fault Tolerance : fault-tolerance
# For Deployer : deployer
# For Sensor Manager : sensor-manager
# For Load Balancer : load-balancer
# For Node Manager : node-manager
# For Scheduler : scheduler
# For App Controller : validator-workflow

# Severity types should be :
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL 

# Message can be any string.



# Eg : For testing purpose. Kindly remove from code while integrating. 
# log_message("node-manager", "DEBUG", "1st msg send for logging :) ")
