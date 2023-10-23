# How to run : 

# Command : python3 monitoring.py

# Eg : 

# For logging the first istance of monitoring we'll write : 
# python3 monitoring.py 


from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import threading
import time
from time import sleep
from kafka.errors import KafkaError
import random
from loggingMessage import *
from fault_tolerance import *
from platform_services import *
from heartbeatGenerator import *
import json


########### For Mongo Database ############################


# Create a new collection called "standardMonitoring" and "alertedMonitoring" in the 'IAS_PROJECT' database
standardMonitoringCollection = monitoring_DB["standardMonitoring"]
alertedMonitoringCollection = monitoring_DB["alertedMonitoring"]
statusCollection = monitoring_DB["containerStatus"]



##########    VARIABLE DECLARATIONS    ##########

# If the time since the last message received by service is > notifyTime then we'll send a message to the platform Admin via the notification service.
notifyTime = 150

# If the time since the last message received by service is > killTime then we'll pass the service along with its information to the Fault Tolerance system which will deal with it.
killTime = 300

# To connect to the kafka stream
kafkaIp = str(kafka_Container_Details['ip'])
kafkaPortNo = str(kafka_Container_Details['port'])
kafkaTopicName = ["heartbeat-monitoring-fault-tolerance", "heartbeat-deployer", "heartbeat-sensor-manager", "heartbeat-load-balancer", "heartbeat-node-manager", "heartbeat-scheduler", "heartbeat-validator-workflow", "heartbeat-developer", "heartbeat-api-gateway"]
kafkaGroupId = "Monitoring"

# Setting up logging credentials : 
producerForLogging = KafkaProducer(bootstrap_servers=[kafkaIp+":"+kafkaPortNo],api_version=(0, 10, 1))



##########    Sending data for monitoring    ##########


monitoringThread = threading.Thread(target=sendheartBeat, args=("heartbeat-monitoring-fault-tolerance", container_name, node_name, ))
monitoringThread.start()


##########    THREAD FUNCTION IMPLEMENTATION    ##########

# Function for monitoring the containers that haven't send their heartbeat for more than 250 seconds. In case these systems don't sent a heartbeat for 500 seconds then they are to be declared dead and their container has to be restarted.

def alertedMonitoring():

    try : 

        while (True):

            # Made filter on the basis of time difference
            current_time = time.time()
            filter_to_kill = {"$expr": {"$gt": [{"$subtract": [float(current_time), {"$toDouble": "$current_time"}]}, killTime]}}
            
            # Retrieve all subsystems documents that match the filter
            documents_to_remove = alertedMonitoringCollection.find(filter_to_kill)

            # Iterating over the documents that will be send to the fault tolerance system to be deleted. 
            for container in documents_to_remove:
                
                log_message("monitoring-fault-tolerance", "CRITICAL", "The susbsystem having container name - {} and node name - {} has be scheduled to be deleted.".format(container["container_name"], container["node_name"]))
                
                # Change the status of the container to 1, to indicate that it has been send for restarting.

                statusFilter = {"container_name": container["container_name"]}
                update = {"$set": {"status": 1}}
                statusCollection.update_one(statusFilter, update)

                # Send all these subsystems to the Fault Tolerance subsystem to kill them. 
                reinitiate_container(container["container_name"], container["node_name"])
                
                alertedMonitoringCollection.delete_one(container)

            sleep(30)

    except :
        
        log_message("monitoring-fault-tolerance", "ERROR", "An issue has occured in alertedMonitoring")

        

# Function for monitoring the containers that haven't send their heartbeat for more than 250 seconds. In case these systems don't sent a heartbeat for 250 seconds then they are to be shifted with the alerted monitoring db and a notification has to be sent to the platform admin that this particular subsystem isn't acting well. 

def standardMonitoring():

    try : 

        sleep(random.randint(0, 60))

        # print("Will finally enter the standard Monitoring code")

        while (True):
                
            # Notification when heartbeat time exceeds 150 and less than 300
            
            current_time = time.time()
            filter_for_notification = {"$expr": {"$gt": [{"$subtract": [float(current_time), {"$toDouble": "$current_time"}]}, notifyTime]}}

            # Retrieve all subsystems document that matches the filter
            subsystems_to_notify = standardMonitoringCollection.find(filter_for_notification)

            # Iterate over the documents and append container_name of the documents to the list
            for subsystem in subsystems_to_notify:
                
                log_message("monitoring-fault-tolerance", "WARNING", "The susbsystem having container name - {} and node name - {} hasn't responded in some time.".format(subsystem["container_name"], subsystem["node_name"]))
                
                alertedMonitoringCollection.insert_one(subsystem)
                
                standardMonitoringCollection.delete_one(subsystem)

                # Send message to the platform admin telling him that this particular node hasn't responded in quiet some time.
                send_mail("yashsampat23154@gmail.com" , "jeetshah141199@gmail.com", "hsdwiuartlwifmml", sub = "Suspicious behaviour of container.", body = "The container : {}, having node name : {} hasn't sent a heartbeat in some time.".format(subsystem["container_name"], subsystem["node_name"]))
            
            sleep(60)

    except :
        log_message("monitoring-fault-tolerance", "ERROR", "An issue has occured in standardMonitoring")




standardMonitoringThread = threading.Thread(target=standardMonitoring, args=[])
standardMonitoringThread.start()

alertedMonitoringThread = threading.Thread(target=alertedMonitoring, args=[])
alertedMonitoringThread.start()


##########    MONITORING SUBSYSTEM IMPLEMENTATION    ##########

def startMonitoring(kafkaTopicName): 

    try:

        consumer = KafkaConsumer(kafkaTopicName, group_id=kafkaGroupId, bootstrap_servers=[f"{kafkaIp}:{kafkaPortNo}"]) 

        for message in consumer:
        
            messageContents = json.loads(message.value)

            # print(messageContents["current_time"])
            
            # Define a filter for the subsystem/doc with the specified name
            monitoringFilter = {"_id": messageContents["container_name"]} # Takes O(log n)

            # Check whether this container already exists in alertedMonitoringCollection.
            existingInAlertedCollection = alertedMonitoringCollection.find_one(monitoringFilter)

            # If the container exists then remove it from the alteredMonitoringCollection
            if existingInAlertedCollection is not None:
                update = {"$set": {"current_time": messageContents["current_time"]}}
                alertedMonitoringCollection.delete_one(existingInAlertedCollection)

            # Check whether this container already exists in standardMonitoringCollection.
            existingInStandardCollection = standardMonitoringCollection.find_one(monitoringFilter)

            # If the subsystem exists, update its current_time field
            if existingInStandardCollection is not None:
                update = {"$set": {"current_time": messageContents["current_time"]}}
                standardMonitoringCollection.update_one(monitoringFilter, update)        

            # If the document does not exist, insert a new subsystem as new document if its time stamp is less than kill time.
            else : 
                messageContents["_id"] = messageContents["container_name"]
                standardMonitoringCollection.insert_one(messageContents)
            

            statusFilter = {"container_name": messageContents["container_name"]}
            existingInStandardCollection = statusCollection.find_one(statusFilter)

            if existingInStandardCollection is not None:
                update = {"$set": {"status": 0}}
                statusCollection.update_one(statusFilter, update)

            # If the document does not exist, insert a new subsystem as new document if its time stamp is less than kill time.
            else : 
                entry = {
                    "container_name" : messageContents["container_name"],
                    "status" : 0
                }
                statusCollection.insert_one(entry)
                log_message("monitoring-fault-tolerance", "INFO", "Monitoring has started for a new container named : {}".format(messageContents["container_name"]))

        
    except KeyboardInterrupt:
        pass

    except KafkaError as kError:
        log_message("monitoring-fault-tolerance", "ERROR", f'Error while consuming messages from topics {kafkaTopicName}: {kError}')


for topic in kafkaTopicName :
    t = threading.Thread(target=startMonitoring, args=(topic, ))
    t.start()