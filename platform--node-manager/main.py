from kafkaHandler import Producer, Consumer
from pymongo import MongoClient
from node_details import get_node_details, create_new_node
from db_queries import get_service_registryDB, get_nodeDB
import json
import random
import threading
from loggingMessage import *
from heartbeatGenerator import *
from globalVariables import *
# GLOBAL VARS
# kafka_server_main = ['20.2.81.4:19092']
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
kafka_server_main = [kafka_string]

def send_the_heartbeat():
    sendheartBeat("heartbeat-node-manager", container_name, node_name)

'''
function listening for messages in getNewNodeRequest kafka topic
'''
def get_free_node():
    # producer consumer for bestNode req resp
    producer_newNode = Producer(bootstrap_servers=kafka_server_main)
    consumer_newNode = Consumer(bootstrap_servers=kafka_server_main, topic="getNewNodeRequest", group_id="consumer-get-free-node")
    
    log_message("node-manager", "DEBUG", "Started consuming the request for new Node")

    while True:
        message = consumer_newNode.consume_message()
        print("get request for free node")
        reply = {}
        reply["sender_name"] = 'node_manager'
        reply["req_detail"] = None
        resp = []
        node, port = create_new_node()
        
        log_message("node-manager", "DEBUG", f"Got the node details: {node, port}")
        
        if(node and port):
            resp.append({"ip" : node["ip"], "port" : port, "nodeName" : node["nodeName"], "password" : node["password"]})
    
        reply["response"] = resp    
        print(reply)
        producer_newNode.send_message("newNodeResponse", reply)

    # Close the consumer connection
    consumer_free_node.close()

'''
function listening for messages in getNodeDetailsRequest kafka topic
'''
def listen_getNode_topic(): 
    # producer consumer for getnode req resp
    producer_getNode = Producer(bootstrap_servers=kafka_server_main)
    consumer_getNode = Consumer(bootstrap_servers=kafka_server_main, topic="getNodeDetailsRequest", group_id="consumer-listen-getNode-topic")

    log_message("node-manager", "DEBUG", "Started consuming the request for Node details")

    nodeDB = get_nodeDB() # get nodeDB
    while True:
        message = consumer_getNode.consume_message()
        
        reply = {}
        reply["sender_name"] = 'node_manager'
        reply["req_detail"] = None
        resp = []
        nodes = nodeDB.find({"status": "active"})

        try:
            pass
            for node in nodes:      
                if node["status"] == "active":
                    node_details = get_node_details(node["node_name"], node['ip'], node['user_name'], node['password'])
                    log_message("node-manager", "DEBUG", f"Got the Node details {node_details}")
                    resp.append({"vm_cpu_usage":node_details[0], "ram_usage":node_details[1], "ip" : node["ip"], "port" : node_details[2], "user_name" : node["user_name"] ,"node_name" : node["node_name"], "password" : node["password"]})


        except Exception as e:
            print(f"Error while fetching node's details : {e}")
            log_message("node-manager", "DEBUG", f"Error while fetching node's details : {e}")



        reply["response"] = resp
        print(reply)
        producer_getNode.send_message("nodeDetailsResponse", reply)
        print("reply sended to kafka topic")
        log_message("node-manager", "DEBUG", "Node details sent to kafka topic : nodeDetailsResponse")
        
    
    # Close the consumer connection
    consumer_getNode.close()

'''
function listening for messages in getServiceDetailsRequest kafka topic
'''
def get_service_topic(): 
    # consumer for getnode req resp
    consumer_getService = Consumer(bootstrap_servers=kafka_server_main, topic="getServiceDetailsRequest", group_id="consumer-get-service-topic")
    log_message("node-manager", "DEBUG", "Service registry started")
    
    service_registryDB = get_service_registryDB() # get service_registryDB
    
    while True:
        message = consumer_getService.consume_message()

        try:
            service_registryDB.insert_one(message)
            log_message("node-manager", "DEBUG", f"Registering app : {message['app_id']}, service : {message['service_name']}")

        except Exception as e:
            print(f"Error while inserting service details in service_registry : {e}")
            log_message("node-manager", "DEBUG", f"Error while inserting service details in service_registry : {e}")

    
    # Close the consumer connection
    consumer_getNode.close()

if __name__ == "__main__": 
    # add threading on listen_getnode_topic and bestnode function
    log_message("node-manager", "DEBUG", "---------- Node Manager Started ----------")

    thread1 = threading.Thread(target=listen_getNode_topic, args=())
    thread1.start()

    thread2 = threading.Thread(target=get_free_node, args=())
    thread2.start()

    thread3 = threading.Thread(target=send_the_heartbeat, args=())
    thread3.start()

    thread4 = threading.Thread(target=get_service_topic, args=())
    thread4.start()


    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

