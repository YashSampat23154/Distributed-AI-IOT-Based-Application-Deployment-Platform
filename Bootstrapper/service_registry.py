import pymongo
import logger as logger

MONGO_SERVER_URL= 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'
MONGO_DB_NAME = 'IAS_test_1'

client = pymongo.MongoClient(MONGO_SERVER_URL)

'''
service_info_entry = {
  "app_name" : "",
  "service_name": "",
  "app_id": "",
  "port": "",
  "container_up_time": "",
  "container_name": "",
  "container_id": "",
  "node_name": "",
  "ip": ""
}
'''

# Creating a new database if not found
db_object = client[MONGO_DB_NAME]

collection_obj = db_object['service_registry']

def delete_entries():
    collection_obj.delete_many({})

def add_service_info(service_info_entry):

    insert_status = collection_obj.insert_one(service_info_entry) != None

    if insert_status == True:
        print(f'Info stored into service registry for platform service[{service_info_entry["service_name"]}]')
        # logger.log_message('DEBUG', f'Info stored into service registry for platform service[{service_info_entry["service_name"]}]')
    
    else:
        print(f'Storing Info into service registry failed for platform service[{service_info_entry["service_name"]}]')
        # logger.log_message('ERROR', f'Storing Info into service registry failed for platform service[{service_info_entry["service_name"]}]')

    print('returning')
    return insert_status
