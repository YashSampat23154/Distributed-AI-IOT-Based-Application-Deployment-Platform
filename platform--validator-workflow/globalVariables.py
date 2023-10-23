import os

node_name = os.getenv('node_name')
container_name = os.getenv('container_name')
container_up_time = os.getenv('container_up_time')

MONGO_CONNECTION_URL = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "IAS_test_1"

connect_str = "DefaultEndpointsProtocol=https;AccountName=applicationrepo326;AccountKey=90h6wbX3Ky2xC2wsMmuWip3XmncCZBdeZgutxJa2L3ngru5IVVlZ0HI2aWXrnw53HM9fVXzaR4Og+ASt4pPSoA==;EndpointSuffix=core.windows.net"
container_name = "appdb"