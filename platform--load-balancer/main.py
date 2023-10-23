from kafkaHandler import Producer, Consumer
import threading
from loadHelper import check_all_usage,request_new_node, change_response_format,get_best_node
from heartbeatGenerator import sendheartBeat
from globalVariables import *
from loggingMessage import log_message
from platform_load import check_plateform_load
from pymongo import MongoClient

print("Started")

MONGO_CONNECTION_URL = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "IAS_test_1"
mongo = MongoClient(MONGO_CONNECTION_URL)
db = mongo[MONGO_DB_NAME]

serviceRegistory = db["service_registry"]
containerDetails = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'kafka'})
print(containerDetails)

kafka_server_ip = containerDetails['ip']
kafka_server_port = containerDetails['port']
kafka_server_main = [f'{kafka_server_ip}:{kafka_server_port}']


# -------------------- Kafka topics and server details -------------------------
deployer_request_topic = "getNodeRequest"
deployer_response_topic = "bestNodeResponse"

nm_request = "getNodeDetailsRequest"
nm_response = "nodeDetailsResponse"

new_node_request = "getNewNodeRequest"
new_node_response = "newNodeResponse"

logger_topic = "log-LoadBalancer-1"

container_overload_topic = "containerOverload"

load_limit = 1000.0
log_message("load-balancer", "DEBUG", "Started")

"""
Function that handles request from deployer
"""
def process_deployer_message(message):

    print(message)
    log_message("load-balancer", "DEBUG", "Read Message from deployer")
    try:
        #  Request to node manager
 
        producer_nm = Producer(bootstrap_servers=kafka_server_main)

        nodedetail_request_message = {
            "sender_name" : "load_balncer",
            "req_detail" : "getNodeDetails",
            "response" : "None"
        }
        print(nodedetail_request_message)
        producer_nm.send_message(nm_request, nodedetail_request_message)
        # producer_nm.flush()
        producer_nm.close()      

        print("Waiting for node details...")
        log_message("load-balancer", "DEBUG", "Read Message from deployer")
        # Replay from node manager

        consumer_nm = Consumer(bootstrap_servers=kafka_server_main, topic=nm_response, group_id="consumer-process-deployer-message")

        node_details_message = consumer_nm.consume_message()
        print(node_details_message)
        log_message("load-balancer", "DEBUG", "Read Message from deployer")
        consumer_nm.close()

        if check_all_usage(node_details_message["response"],load_limit) :
        #  If all node are used over limit
            print("Usage overload-> Request for new node")
            log_message("load-balancer", "DEBUG", "Read Message from deployer")
            new_node = request_new_node(new_node_request,new_node_response,kafka_server_main)

            if new_node is None:
            # No new node available
                print("new node not found")
                log_message("load-balancer", "DEBUG", "New node not found")
                if len(node_details_message["response"]) > 0:
                    # Return onr from existing ones
                    best_node = get_best_node(node_details_message["response"])
                    best_node_op = change_response_format(best_node)
                    print(best_node_op)
                    log_message("load-balancer", "DEBUG", "Sending node from exising ones")
                    
                    producer_dp = Producer(bootstrap_servers=kafka_server_main)
                    producer_dp.send_message(deployer_response_topic, best_node_op)
                    producer_dp.close()
                    log_message("load-balancer", "DEBUG", f'sending node to deployer:{best_node_op}' )
                else:
                    # neithe new nor exising available
                    print("No nodes available to serve")
                    log_message("load-balancer", "CRITICAL", "No Nodes Available")

            else:
                # Return new node to deployer
                print("Sending new node to Deployer")
                new_node_res = change_response_format(new_node)
                log_message("load-balancer", "DEBUG", f'sending new node: {new_node_res}')
                producer_dp = Producer(bootstrap_servers=kafka_server_main)
                producer_dp.send_message(deployer_response_topic, new_node_res)
                producer_dp.close()


        else:
            # Return best node to deployer
            print("Normal case - sending best node to deployer")
            log_message("load-balancer", "DEBUG", f'Normal Case')
            best_node = get_best_node(node_details_message["response"])
            best_node_op = change_response_format(best_node)
            print(best_node_op)
            log_message("load-balancer", "DEBUG", f'Sending Node to deployer: {best_node_op}')
            producer_dp = Producer(bootstrap_servers=kafka_server_main)
            producer_dp.send_message(deployer_response_topic, best_node_op)
            producer_dp.close()


    except Exception as e:
        print(f"Error while processing message of deployer : { node_details_message } : {e}")
        log_message("load-balancer", "ERROR", f'Processing message from deployer{message}')
        # consumer_nm.seek(message.topic_partition, message.offset)
        return

print("T1")

""" Thread check for container overload """
platform_t = threading.Thread(target=check_plateform_load, args=(container_overload_topic,kafka_server_main, ))
platform_t.start()

log_message("load-balancer", "DEBUG", "Conatainer thread started")
print("T1 started")

""" Heartbeat and Logger Code """

heartbeat_thread = threading.Thread(target=sendheartBeat, args=("heartbeat-load-balancer", container_name, node_name, ))
heartbeat_thread.start()

log_message("load-balancer", "DEBUG", "Heartbeat thread started")

print("T2 Started")
"""Main Thread Listening from deployer"""

consumer_nm = Consumer(bootstrap_servers=kafka_server_main, topic=deployer_request_topic, group_id="consumer-load-balancer")

# consumer = KafkaConsumer(
#     deployer_request_topic,
#     bootstrap_servers=kafka_server_main, auto_offset_reset='earliest', group_id="consumer-group-b")

# message = "INFO:" + "Consumer from deplyer is created."
# log_producer.send(logger_topic, json.dumps(message).encode('utf-8'))

while True:
    try:
        print("Read Message from deployer")
        log_message("load-balancer", "DEBUG", "Read Message from deployer")
        message = consumer_nm.consume_message()
        thread = threading.Thread(target=process_deployer_message, args=(message,))
        thread.start()
        # process_deployer_message(message)

    except Exception as e:
        print(f"Error while consuming messages from deployer: {e}")
        log_message("load-balancer", "ERROR", "Error while consuming message from deployer")
        consumer_nm.close()
        consumer_nm = Consumer(bootstrap_servers=kafka_server_main,topic=deployer_request_topic, group_id="consumer-load-balancer")