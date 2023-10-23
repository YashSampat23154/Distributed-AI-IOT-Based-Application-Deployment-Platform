from flask import request, jsonify
from pymongo import MongoClient

CONNECTION_STRING = 'mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority'

def get_service_registry():
    client = MongoClient(CONNECTION_STRING)
    return client['IAS_test_1']["service_registry"] 

service_registry_client = get_service_registry()
# node_db_client = MongoClient(CONNECTION_STRING)['IAS']['nodeDB']

def get_instances(subsystem_name):

    app_name = "platform"

    instances_info = dict()

    instances_info['subsystem_name'] = subsystem_name

    instances_info['instances'] = list()

    instances = service_registry_client.find({"app_name":app_name, "service_name" : subsystem_name})

    for instance in instances:
        instances_info['instances'].append({
            'instance_name' : f"{instance['service_name']}_{instance['container_up_time']}"
        })

    return jsonify(instances_info)