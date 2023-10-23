from kafka import KafkaProducer
from datetime import datetime
import json
from globalVariables import *
from pymongo import MongoClient
import certifi

# All variable declaration.
CONNECTION_STRING = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
serviceDb = client['IAS_test_1']["service_registry"]
containerDetails = serviceDb.find_one({'app_name': 'platform', 'service_name' : 'kafka'})
kafkaIp = containerDetails['ip']
kafkaPortNo = str(containerDetails['port'])

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
log_message("monitoring", "DEBUG", "1st msg send for logging :) ")
log_message("fault-tolerance", "DEBUG", "1st msg send for logging :) ")
log_message("deployer", "DEBUG", "1st msg send for logging :) ")
log_message("sensor-manager", "DEBUG", "1st msg send for logging :) ")
log_message("load-balancer", "DEBUG", "1st msg send for logging :) ")
log_message("node-manager", "DEBUG", "1st msg send for logging :) ")
log_message("scheduler", "DEBUG", "1st msg send for logging :) ")
log_message("validator-workflow", "DEBUG", "1st msg send for logging :) ")
