import pymongo
import logger as logger

MONGO_SERVER_URL= 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'
MONGO_DB_NAME = 'IAS_test_1'

client = pymongo.MongoClient(MONGO_SERVER_URL)

'''
entry = {
  "password" : "",
  "node_name": "",
  "ip": "",
  "user_name": "",
  "status" : ""
}
'''

# Creating a new database if not found
db_object = client[MONGO_DB_NAME]

node_collection_obj = db_object['nodeDB']

def get_node_info(node_name):

    node_data = node_collection_obj.find_one({"node_name": node_name})

    return node_data

