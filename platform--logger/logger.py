# How to run : 

# Command : python3 logger.py

# Kafka topics that will be create for logging: "logs"


from kafka import KafkaConsumer
from time import sleep
import json
import threading
from kafka.errors import KafkaError
from globalVariables import *
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


# All variable declaration.
kafkaIp = str(kafka_Container_Details['ip'])
kafkaPortNo = str(kafka_Container_Details['port'])
kafkaGroupId = "log-group"

kafkaTopicName = ["log-monitoring-fault-tolerance", "log-deployer", "log-sensor-manager", "log-load-balancer", "log-node-manager", "log-scheduler", "log-validator-workflow", "log-bootstrapper", "log-api-gateway", "log-ldap"]


def storeLogs(fileName) : 

    loggingCollection = logger_DB[fileName]

    while(True) :

        try : 


            # retrieve all documents in the collection
            logs = list(loggingCollection.find())

            # Real logs as a sentence:
            # [subsystem_name] : [container_up_time] : [severity] : [date][time] => <message>

            # write the documents to a text file
            with open(fileName, "w") as f:
                for log in logs:
                    message = str(log["subsystem_name"]) + " : " + str(log["container_up_time"]) + " : " + str(log["severity"]) + " : "+ str(log["date"]) + " " + str(log["time"]) +  " => " + str(log["message"])
                    f.write(str(message) + "\n")

            # upload the text file to Azure Blob Storage
            connection_string = "DefaultEndpointsProtocol=https;AccountName=applicationrepo326;AccountKey=90h6wbX3Ky2xC2wsMmuWip3XmncCZBdeZgutxJa2L3ngru5IVVlZ0HI2aWXrnw53HM9fVXzaR4Og+ASt4pPSoA==;EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            container_client = blob_service_client.get_container_client("log-storage")
            blob_client = container_client.get_blob_client(fileName)

            with open(fileName, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            sleep(60)
        
        except : 
            print("An error has occured while uploading logs to the blob storage.")

    


def logSystem (kafkaTopicName) :
    
    consumer = KafkaConsumer(kafkaTopicName, group_id=kafkaGroupId, bootstrap_servers=[kafkaIp+":"+kafkaPortNo])
    
    try:
        for message in consumer:

            messageContents = json.loads(message.value)
            loggingCollection = logger_DB[f"log-{messageContents['subsystem_name']}"]
            loggingCollection.insert_one(messageContents)

    except KeyboardInterrupt:
        pass
    except KafkaError as kError:
        print(f'Error while consuming messages from topics {kafkaTopicName}: {kError}')

    sleep(10)


for topic in kafkaTopicName :
    t1 = threading.Thread(target=logSystem, args=(topic, ))
    t1.start()
    t2 = threading.Thread(target=storeLogs, args=(topic, ))
    t2.start()