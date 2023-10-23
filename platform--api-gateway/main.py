from flask import Flask, abort, request , jsonify
import requests
from pymongo import MongoClient
import os
from kafkaHandler import Producer
from loggingMessage import log_message
import json
import certifi
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from heartbeatGenerator import sendheartBeat
from globalVariables import *
import threading
t1 = threading.Thread(target=sendheartBeat, args=("heartbeat-monitoring", container_name, node_name, ))
t1.start()

# CONNECTION_STRING = "mongodb+srv://root:rp123123@lab8.qnzi7qu.mongodb.net/?retryWrites=true&w=majority"
CONNECTION_STRING = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

serviceDb = client['IAS_test_1']["service_registry"]

containerDetails = serviceDb.find_one({'app_name': 'platform', 'service_name' : 'kafka'})

kafka_server_ip = containerDetails['ip']
kafka_server_port = str(containerDetails['port'])
bootstrap_servers = [f'{kafka_server_ip}:{kafka_server_port}']
print("bootstrap servers: ",bootstrap_servers)

@app.route('/services', methods=['POST'])
def serviceReq():
    # api gateway url which will then forward to ip:port of the service container 
    # and then sendback the response

    service_request = request.get_json()

    print("inside api gateway serviceReq ", service_request)
    IPPort = serviceDb.find_one({'app_id': service_request['app_id'], 'service_name' : service_request['service']})
    print(IPPort)

    url = f"http://{IPPort['ip']}:{IPPort['port']}/"

    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data = json.dumps(service_request), headers = headers)
    return (response.content, response.status_code, response.headers.items())

@app.route('/getAppId', methods=['POST'])
def getAppId():
    data = request.get_json()
    applicationsDB = client['IAS_test_1']['applications']
    appData = applicationsDB.find({'applicationName':data["applicationName"]})
    return jsonify({"appId": appData["appId"]})

@app.route('/login', methods=['POST'])
def login():
    service_request = request.get_json()
    IPPort = serviceDb.find_one({'app_id': service_request['app_id'], 'service_name' : service_request['ldap']})

    url = f"http://{IPPort['ip']}:{IPPort['port']}/login"
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data = json.dumps(service_request), headers = headers)
    return (response.content, response.status_code, response.headers.items())

@app.route('/register', methods=['POST'])
def register():
    service_request = request.get_json()
    IPPort = serviceDb.find_one({'app_id': service_request['app_id'], 'service_name' : service_request['ldap']})

    url = f"http://{IPPort['ip']}:{IPPort['port']}/register"
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data = json.dumps(service_request), headers = headers)
    return (response.content, response.status_code, response.headers.items())

@app.route(f'/<string:path>', methods=['POST'])
def append_strings(path):
    log_message("api-gateway", "DEBUG", "/ -- requested")
    if request.method == 'POST':
    # fetch ip and ports from the database
        req_msg = request.get_json()
        print(req_msg)
        log_message("api-gateway", "DEBUG",f'/{path} -- {req_msg}')
        system_name1 = req_msg.get("system_name")
        service_name1 = req_msg.get("service_name")
        # path = req_msg.get("path")
        parameters = req_msg.get("parameters")
        if system_name1 == "app" :
          log_message("api-gateway", "DEBUG", "/upload -- Application requested")
          available_service = serviceDb.find({"app_id":req_msg.get("app_id") , "service_name" : service_name1})
        else :
          log_message("api-gateway", "DEBUG", "/upload -- Platform subsystem requested")
          available_service = serviceDb.find({"app_name":"platform","service_name" : service_name1 })
        
        services =  []
        for service in available_service:
            services.append(service)
    
        if len(services) > 0 :
            log_message("api-gateway", "DEBUG",f'/{path} -- service available')
            selected_service = services[0]
            req_url = f'http://{selected_service["ip"]}:{selected_service["port"]}/{path}'
            if req_msg.get("req_type") == "GET":
                log_message("api-gateway", "DEBUG",f'/{path} -- GET request')
                response = requests.get(req_url)
                return response.content
            elif req_msg.get("req_type") == "POST" :
                log_message("api-gateway", "DEBUG",f'/{path} -- POST request')
                data = parameters
                response = requests.post(req_url, json=data)
                return response.content
        else:
            log_message("api-gateway", "WARNING",f'/{path} -- service not available')
            abort(404)
    log_message("api-gateway", "WARNING", "/ -- NOT A POST REQUEST")
    return jsonify({"message":"bad request"})
    
    # path = "service1"
    # data1 = {"name":"shukan"}
    # req_url = f'http://127.0.0.1:5000/{path}'
    # response = requests.post(req_url,json=data1)
    # if request.method == 'GET':
    #     # req_url = f'http://{selected_service["ip"]}:{selected_service["port"]}/'
    #     response = requests.get(req_url)
    #     return response.content
    # elif request.method == 'POST':
    #     # data = request.json
    #     # req_url = f'http://{selected_service["ip"]}:{selected_service["port"]}/'
    #     response = requests.post(req_url,json=data1)
    #     return response.content
    # return response.content


@app.route('/validator-workflow/upload', methods=['POST'])
def upload_zip():
  log_message("api-gateway", "DEBUG", "/upload -- requested")
  available_service = serviceDb.find({"app_name":"platform","service_name" : "validator-workflow" })
  print(request.files, request.files['file'].filename)
  file = request.files['file']
  file.save("./"+file.filename)

  with open(file.filename, 'rb') as f:
    file_data = f.read()

  data = {
    'file': (file.filename, file_data)
  }

  services =  []
  for service in available_service:
      print(service)
      services.append(service)

  if len(services) > 0 :
      log_message("api-gateway", "DEBUG", "/upload -- Service available")
      selected_service = services[0]
      req_url = f'http://{selected_service["ip"]}:{selected_service["port"]}/upload'
      if request.method == "POST":
        headers = {   "Content-Type": "multipart/form-data" }
        # response = requests.request(request.method, req_url, headers=headers, files=request.files)
        response = requests.request(request.method, req_url, files=data)
        os.remove(file.filename)
        log_message("api-gateway", "DEBUG", "/upload -- sending response")
        return (response.content, response.status_code, response.headers.items())
  else:
      abort(404)
  return jsonify({"message":"bad request"})



@app.route('/fetch-app-data')
@cross_origin()

def fetch_app_data():
    """
    Get information about an app by app developer ID.
    ---
    parameters:
      - name: app_developer_id
        in: query
        description: ID of the app developer
        required: true
        type: string
    responses:
      200:
        description: OK
        schema:
          type: list of objects
          properties:
            app_id:
              type: string
            app_name:
              type: string
            service_id:
              type: string
            sensors_registered:
              type: list
            status:
              type: string
    """

    app_developer_id = request.args.get("app_developer_id")
    print(app_developer_id)
    app_controller_url="mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(app_controller_url, tlsCAFile=certifi.where())

    app_controller_db = "IAS_test_1"
    collection_name = "applications"

    # Get a reference to the collection
    applications_collection = client[app_controller_db][collection_name]

    # Use the find method to retrieve all documents in the collection
    documents = applications_collection.find({"developer_id":  app_developer_id})

    CONNECTION_STRING = "mongodb+srv://admin:iasproject@cluster0.t5qnsna.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())

    sensors_collection = client['platform']['sensors_instances_meta']
  
    sensors_registered = sensors_collection.count_documents({})
    print("sensors registered: ",sensors_registered)
    response_list = []
    for document in documents:
        response_obj = {}
        response_obj['app_id'] = document['appId']
        response_obj['app_name'] = document['applicationName']
        response_obj['service_ids'] = []
        response_obj['sensors_registered'] = sensors_registered
        
        for service in document['services']:
            response_obj['service_ids'].append(service['name'])

        collection_name = "scheduler_status"
        scheduler_status = client[app_controller_db][collection_name]

        scheduled_app = scheduler_status.find({"appId":  document['appId']})

        response_obj['status'] = None

        for app in scheduled_app:
          print(app)
          response_obj['status'] = app['status']
          break

        if response_obj['status'] is None:
          response_obj['status'] = "registered"

        response_list.append(response_obj)

    return response_list


@app.route('/scheduler/scheduleApp', methods=['POST'])
def scheduleApp():
  log_message("api-gateway", "DEBUG", "/scheduler/scheduleApp requested")
  schedule_request = request.get_json()
  print(schedule_request)
  log_message("api-gateway", "DEBUG", f'/scheduler/scheduleApp  :{schedule_request}')
  producer = Producer(bootstrap_servers=bootstrap_servers)
  producer.send_message("scheduler", schedule_request)
  producer.close()
  log_message("api-gateway", "DEBUG", f'/scheduler/scheduleApp -- complete')
  return jsonify({"message": "App Schedule Request Sent Successfully"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8010,debug=True)
