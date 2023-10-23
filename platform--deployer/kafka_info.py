
import pymongo

MONGO_SERVER_URL = 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'
MONGO_DB_NAME = "IAS_test_1"


client = pymongo.MongoClient(MONGO_SERVER_URL)

# Creating a new database if not found
db_object = client[MONGO_DB_NAME]


def get_kafka_info():
    # setup kafka ip
    service_registry = db_object['service_registry']
    kafka_info = service_registry.find_one({'app_name' : 'platform', 'service_name': 'kafka'})

    return kafka_info
