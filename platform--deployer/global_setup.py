import global_variables
import os
import pymongo
import logger as logger

MONGO_SERVER_URL= 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'
MONGO_DB_NAME = 'IAS_test_1'

client = pymongo.MongoClient(MONGO_SERVER_URL)

'''
entry = {
    "ip" : "",
    "user_name" : "",
    "password" :  "",
    "node_name": ""
}
'''

# Creating a new database if not found
db_object = client[MONGO_DB_NAME]

node_db = db_object['nodeDB']

def setup_global_env():

    print('Setting up global variables and env variables')

    # set-up global variables by fetching it from env
    global_variables.node_name = os.getenv('node_name')
    global_variables.container_name = os.getenv('container_name')
    global_variables.CONTAINER_UP_TIME = os.getenv('container_up_time')

    # get node info from node-db
    global_variables.node_info = node_db.find_one({'node_name' : global_variables.node_name})

    if global_variables.node_info == None:
        print(f'Node info not found into nodeDB for node[{global_variables.node_name}]')
        logger.log_message('ERROR', f'Node info not found into nodeDB for node[{global_variables.node_name}]')
    else:
        print(f'Node info found successfully into nodeDB for node[{global_variables.node_name}]')
        logger.log_message('DEBUG', f'Node info found successfully into nodeDB for node[{global_variables.node_name}]')

    os.system(f"apt-get update;apt-get -y install vim;apt-get install sshpass;mkdir /root/.ssh && chmod 0700 /root/.ssh;ssh-keyscan -H {global_variables.node_info['ip']} >> ~/.ssh/known_hosts")

    print('Deployer set-up completed for global variables and env variables')
    logger.log_message('DEBUG','Deployer set-up completed for global variables and env variables')
