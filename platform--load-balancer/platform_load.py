from kafkaHandler import Producer
from pymongo import MongoClient
from container_load import get_containerwise_load
from time import sleep
from loggingMessage import log_message

# CONNECTION_STRING = "mongodb+srv://root:rp123123@lab8.qnzi7qu.mongodb.net/?retryWrites=true&w=majority"
CONNECTION_STRING = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
nodeDB = client['IAS_test_1']["nodeDB"]
serviceDb = client['IAS_test_1']["service_registry"]


def check_plateform_load(overload_topic,kafka_main_server):
    print("Load Container started")
    producer_lb = Producer(bootstrap_servers=kafka_main_server)
    sleep(150)

    while True:
    # for i in range(1):
        print("Check for conatiner load")
    # for i in range(5):
        # log_message("load-balancer", "DEBUG", "Checking load for containers")
        available_nodes = nodeDB.find({"status": "active"})
        nodes =  []
        for node in available_nodes:
            # print(node)
            nodes.append(node)
        print(nodes)
        for node1 in nodes:
            # print(node1)
            answer = get_containerwise_load(hostip=node1["ip"],uname=node["user_name"],password=node1["password"])
            print(answer)
            for container in answer:
                response = serviceDb.find({"app_name":"platform", "container_id":container})
                services =  []
                for service in response:
                    services.append(service)
                
                if len(services) > 0:
                    message = node1
                    message['container_id'] = container
                    message['appName'] = services[0]['app_name']
                    message['serviceName'] = services[0]['service_name']
                    message['appId'] = services[0]['app_id']
                    message['scheduleType'] = 'run'
                    message['kafkaTopic'] = 'DeployerResponseToLoadBalanxer'
                    print("Message Sent to deployer : \n \n",message)
                    producer_lb.send_message(overload_topic,message=message)

        sleep(120)


# if __name__ == "__main__":
#     print("Started")
#     check_plateform_load("Hello123",['20.2.81.4:19092'])
