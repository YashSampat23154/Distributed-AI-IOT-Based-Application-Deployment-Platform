from pymongo import MongoClient
CONNECTION_STRING = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "IAS_test_1"
# return nodeDB
def get_nodeDB():
    client = MongoClient(CONNECTION_STRING)
    return client[DATABASE_NAME]["nodeDB"] 

def get_service_registryDB():
    client = MongoClient(CONNECTION_STRING)
    return client[DATABASE_NAME]["service_registry"] 

def get_portDB():
    client = MongoClient(CONNECTION_STRING)
    return client[DATABASE_NAME]["portDB"] 

def free_node(node_name):
    nodeDB = get_nodeDB()
    find_rec = {"node_name":node_name}
    new_val = {"status":"free"}
    nodeDB.update_one(find_rec, new_val)

def get_free_node():
    nodeDB = get_nodeDB()
    node = nodeDB.find_one({"status":"free"})
    return node

def make_node_active(node_name):
    nodeDB = get_nodeDB()
    find_rec = {"node_name":node_name}
    new_val = {"status":"active"}
    nodeDB.update_one(find_rec, new_val)

def get_used_port(node_name):
    portDB = get_portDB()
    ports = portDB.find({"node_name": node_name})
    sended_ports = []
    for p in ports:      
        sended_ports.append(p['port'])
    return sended_ports

def add_port(node_name, port):
    portDB = get_portDB()
    portDB.insert_one({"node_name": node_name, "port" : port})

