import os
from pymongo import MongoClient
import logger as log

MONGO_SERVER_URL = 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'
MONGO_DB_NAME = "IAS_test_1"

client = MongoClient(MONGO_SERVER_URL)
db = client[MONGO_DB_NAME]

def setup_node_env(vm_list):

    for node_info in vm_list:
        
        print(f'Starting env setup for {node_info["ip"]}')

        os.system(f'ssh-keyscan -H {node_info["ip"]} >> ~/.ssh/known_hosts')

        os.system(f"sshpass -p {node_info['password']} scp -r ./node_env_setup.sh {node_info['user_name']}@{node_info['ip']}:~/.")

        os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} 'chmod 777 ./node_env_setup.sh'")

        os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} bash -s < ./node_env_setup.sh {node_info['ip']}")

        print(f'Env setup completed for {node_info["ip"]}')


def delete_node_entries():
    
    MONGO_COLLECTION_NAME = "nodeDB"
    collection = db[MONGO_COLLECTION_NAME]
    
    collection.delete_many({})


def delete_config_entries():
    
    MONGO_COLLECTION_NAME = "platform_config"
    collection = db[MONGO_COLLECTION_NAME]
    
    collection.delete_many({})

'''
node_info = {
    "user_name": "",
    "ip": "",
    "password": "",
    "node_name": "",
    "status": "active/inactive"
}
'''

def insert_nodes(nodes):

    # first clear all the previous entries from nodeDB collection
    delete_node_entries()

    MONGO_COLLECTION_NAME = "nodeDB"
    collection = db[MONGO_COLLECTION_NAME]

    for node in nodes:
        insert_status = collection.insert_one(node) != None

        if insert_status == True:
            print(f'Node-Info stored successfully into db for node[{node["ip"]}] ')
            log.log_message('DEBUG', f'Node-Info stored successfully in db for node[{node["ip"]}]')

        else:
            print(f'Storing Node-Info in db failed for node[{node["ip"]}]')
            log.log_message('ERROR', f'Storing Node-Info in db failed for node[{node["ip"]}]')


def insert_config_details(configurations):

    # first clear all the previous entries from platform_config collection
    delete_config_entries()
    
    MONGO_COLLECTION_NAME = "platform_config"

    collection = db[MONGO_COLLECTION_NAME]

    for config_info in configurations:
        insert_status = collection.insert_one(config_info) != None