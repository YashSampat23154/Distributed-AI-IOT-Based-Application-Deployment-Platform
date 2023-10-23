import pymongo
import logger as logger

MONGO_SERVER_URL= 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'
MONGO_DB_NAME = 'IAS_test_1'

client = pymongo.MongoClient(MONGO_SERVER_URL)

'''
entry = {
  "app_name" : "",
  "service_name": "",
  "app_id": "",
  "port": "",
  "container_up_time": "",
  "container_name": ""
  "node_name": "",
  "ip": ""
}
'''

# Creating a new database if not found
db_object = client[MONGO_DB_NAME]

service_collection_obj = db_object['service_registry']

def get_service_info(app_id, service_name):

    service_data = service_collection_obj.find_one({"app_id": str(app_id), "service_name":service_name})

    return service_data

