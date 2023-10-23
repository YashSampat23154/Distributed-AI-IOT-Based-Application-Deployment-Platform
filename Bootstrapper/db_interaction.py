from pymongo import MongoClient
import logger as log

MONGO_SERVER_URL = 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'
MONGO_DB_NAME = "IAS_test_1"
MONGO_COLLECTION_NAME = "app_service_deployer_data"

def getDBAndCollectionList():

    client = MongoClient(MONGO_SERVER_URL)
    db = client[MONGO_DB_NAME]
    
    return db, db.list_collection_names()

def getCollection():
    
    db, list_of_collections = getDBAndCollectionList()
    collection = None
    
    if MONGO_COLLECTION_NAME not in list_of_collections:
        collection = db.create_collection(MONGO_COLLECTION_NAME)
    
    else:
        collection = db[MONGO_COLLECTION_NAME]
    
    return collection

def getAppData(app_id, service_name):

    collection = getCollection()
    appData = collection.find_one({"app_id": str(app_id), "service_name":service_name})

    return appData, (appData != None)


def getPlatformData(service_name):

    collection = getCollection()
    platformData = collection.find_one({"app_name": 'platform', "service_name":service_name})

    return platformData, (platformData != None)


def setAppdata(app_id, app_name, service_name, acr_img_path, port):
    print(f'Storing ACR-image info into db for app[{app_name}] service[{service_name}]')
    log.log_message('DEBUG', f'Storing ACR info into db for app[{app_name}] service[{service_name}]')

    collection = getCollection()
    json_data = {"app_id":str(app_id), "app_name":app_name, "service_name":service_name, "acr_img_path":acr_img_path, "port":port}
    
    insert_status = collection.insert_one(json_data) != None

    if insert_status == True:
        print(f'ACR-Info stored successfully into db for app[{app_name}] service[{service_name}]')
        log.log_message('DEBUG', f'ACR-image Info stored successfully in db for app[{app_name}] service[{service_name}]')
    
    else:
        print(f'Storing ACR-image Info in db failed for app[{app_name}] service[{service_name}]')
        log.log_message('ERROR', f'Storing ACR-image Info in db failed for app[{app_name}] service[{service_name}]')

    return insert_status
