from kafka import KafkaProducer
from datetime import datetime
import json
import global_variables

kafkaIp = "20.2.81.4"
kafkaPortNo = "19092"
producerForLogging = KafkaProducer(bootstrap_servers = [kafkaIp+":"+kafkaPortNo], api_version=(0, 10, 1))

'''
log_entry = {
        "subsystem_name" : "Monitoring",
        "container_up_time" : "xyz",
        "date": dateAndTime.strftime("%Y-%m-%d"),
        "time": dateAndTime.strftime("%H:%M:%S"),
        "severity": messageContents[0],
        "message": messageContents[1]
    }
'''

# send the logging message on log-deployer topic to logger service
def log_message(severity, msg):

    loggingTopic = f"log-{global_variables.subsystem}"

    cur_time = datetime.now()

    log_entry = {
        "subsystem_name" : global_variables.subsystem,
        "container_up_time" : global_variables.CONTAINER_UP_TIME,
        "date": cur_time.strftime("%Y-%m-%d"),
        "time": cur_time.strftime("%H:%M:%S"),
        "severity": severity,
        "message": msg
    }

    while True:
        try:
            # producing log_entry to the logger
            producerForLogging.send(loggingTopic, json.dumps(log_entry).encode('utf-8'))
            break
        except:
            pass




# print(datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"))
