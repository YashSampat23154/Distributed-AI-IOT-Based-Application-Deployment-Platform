from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import requests
import zipfile
import os 
import jsonschema
import json
import shutil
import uuid
from pymongo import MongoClient
from workflowEngine import generateWorkflow
from loggingMessage import log_message
from globalVariables import *
from heartbeatGenerator import sendheartBeat

import threading
t1 = threading.Thread(target=sendheartBeat, args=("heartbeat-monitoring", container_name, node_name, ))
t1.start()

mongo = MongoClient(MONGO_CONNECTION_URL)
db = mongo[MONGO_DB_NAME]

appCollection = db["applications"]
blobCollection = db["blobStorage"]
serviceRegistory = db["service_registry"]
containerDetails = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'kafka'})

# Creating a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)


app = Flask(__name__)
def folder_to_json(path):
    folder_dict = {}
    for entry in os.scandir(path):
        if entry.is_file():
            folder_dict[entry.name] = None
        elif entry.is_dir():
            folder_dict[entry.name] = folder_to_json(entry.path)

    return folder_dict

def validateFileSchema(zipPath, fileName) -> bool:
    contractPath = os.getcwd() + "/contracts/" + fileName
    contractSchema = open(contractPath)
    contractSchema = json.load(contractSchema)

    filePath = os.getcwd() + zipPath + fileName    
    if os.path.exists(filePath) == False:
        return False, filePath+ " file missing"
    
    fileSchema = open(filePath)
    fileSchema = json.load(fileSchema)
    # print("fileSchema: ", fileSchema)

    # Validate the JSON data against the schema
    try:
        jsonschema.validate(instance = fileSchema, schema = contractSchema)
        return True, "valid"
        # print("JSON data is valid")
    except jsonschema.exceptions.ValidationError as e:
        return False, e.message
        # print("JSON data is invalid: " + e.message)

def validateDir(structureJson, zipStructure) -> bool:
    keys = zipStructure.keys()

    for file in structureJson["files"]:
        if file not in keys or zipStructure[file] != None:
            print(f'{file} missing...')
            return False

    for dir in structureJson["directories"]:
        # print(dir)
        if dir["name"] not in keys or zipStructure[dir["name"]] == None:
            return False
        
        if validateDir(dir, zipStructure[dir["name"]]) == False:
            return False;

    return True        

def generateDirStructure(zipPath, fileName):
    
    filePath = os.path.join(zipPath, fileName)        
    fileSchema = open(filePath)
    fileSchema = json.load(fileSchema)

    dirStructure = []
    services = {}
    services["name"] = "services"
    services["files"] = []
    services["directories"] = []
    # print(fileSchema["Application_Name"]["Services"])
    for service in fileSchema["services"]:
        serviceData = {}
        serviceData["directories"] = []
        serviceData["name"] = service["name"]
        serviceData["files"] = service["files"]
        services["directories"].append(serviceData)
    dirStructure.append(services)
    
    workflows = {}
    workflows["name"] = "workflows"
    workflows["files"] = []
    workflows["directories"] = []
    for workflow in fileSchema["workflows"]:
        workflows["files"].append(workflow)
    dirStructure.append(workflows)    
    return dirStructure

@app.route('/upload', methods=['POST'])
def upload():
    print("Req Received...")
    # print(request.files)
    log_message("validator-workflow", "DEBUG", "Upload req received..")
    if 'file' not in request.files:
        log_message("validator-workflow", "ERROR", "No file found in the request")
        return jsonify({'error': 'No file found in the request'})

    file = request.files['file']
    file.save(file.filename)
    print(file.filename)

    if not file.filename.endswith('.zip'):
        log_message("validator-workflow", "ERROR", "Uploaded file is not zip")
        return jsonify({'error': 'Uploaded file is not zip'})

    appName = file.filename.split(".zip")[0]
    
    if file.filename.endswith('.zip'):
        with zipfile.ZipFile(file, 'r') as zip:
            zip.extractall(appName)
            print("Zip File extracted")
        
        os.remove(os.path.join(os.getcwd(), file.filename))
        log_message("validator-workflow", "DEBUG", "appConfig.json format validated..")
                    
        appPath = os.path.join(os.getcwd(), appName)
        filePath = os.path.join(appPath, "appConfig.json")
        fileSchema = open(filePath)
        fileSchema = json.load(fileSchema)
        if(fileSchema["applicationName"] != appName):
            log_message("validator-workflow", "ERROR", "Zip filename not same as application name..")
            return jsonify({'error': "Zip filename not same as application name."})

        flag_appServer = False
        fileSchema["appId"] = str(uuid.uuid1()) 
        for service in fileSchema["services"]:
            if(service["name"] == "app"):
                flag_appServer = True

        if flag_appServer == False:
            log_message("validator-workflow", "ERROR", "Please include application server as a service with name 'app'.")
            return jsonify({'error': "Please include application server as a service with name 'app'."})
        
        data = open('contracts/zipfile.json')
        structureFile = json.load(data)
        dir = generateDirStructure(appPath, "appConfig.json")
        structureFile["directories"] = dir
        structureFile["files"] = []
        # print("req structure ", json.dumps(structureFile, indent=2))
        log_message("validator-workflow", "DEBUG", f'req structure acc to appConfig: {structureFile}')

        json_data = folder_to_json(appPath)
        # print("zip structure: ", json.dumps(json_data, indent=2))

        if validateDir(structureFile, json_data) == False:
            # If you are changing file structure change the appConfig.json also!!!
            log_message("validator-workflow", "ERROR", f'Invalid zip structure, some directories/files might be missing')
            return jsonify({'error': 'Invalid zip structure, some directories/files might be missing..', "dir": structureFile, "req": json_data})
        
    os.remove(os.path.join(appPath, "appConfig.json"))

    for workflow in fileSchema["workflows"]:
        temp = generateWorkflow(os.path.join(appPath, "workflows"), workflow.split(".")[0] + ".json")
        if temp != "success":
            log_message("validator-workflow", "ERROR", f'{temp}')
            return jsonify({'error' : temp})
        # appData["workflows"].append(workflowDict)

    tempUpload = uploadZipToAzure(fileSchema["appId"], appName, appPath, fileSchema)
    if tempUpload != "success":
        log_message("validator-workflow", "ERROR", f'{tempUpload}')
        pass
    else:
        log_message("validator-workflow", "DEBUG", f'Services/Workflows zip uploaded to blob and entry made in blobStorage collection.')
        pass

    try:
        log_message("validator-workflow", "DEBUG", f'Sensor data sending to SM: {fileSchema}')
        serviceRegistory = db["service_registry"]
        IPPort = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'sensor-manager'})
        url = f"http://{IPPort['ip']}:{IPPort['port']}/register"
        # url = f"http://192.168.54.219:5000/register"
        print(url, json.dumps(fileSchema,indent=2))
        res = requests.post(url, json = fileSchema)
        print("response from sm: ", res.status_code, res)
    except:
        log_message("validator-workflow", "ERROR", f'Error sending data to sensor manager..')
        print(f'Error sending data to sensor manager..')
        
    appCollection.insert_one(fileSchema)

    log_message("validator-workflow", "DEBUG", f'Zip file uploaded successfully, appId: sensorData["application_id"]')
    return jsonify({'message': 'Zip file uploaded successfully', "appId": fileSchema["appId"]})


def uploadZipToAzure(appId, applicationName, destination_path, fileSchema):
    try:
        servicesPath = os.path.join(destination_path, 'services')
        print(servicesPath)

        # for service in services:
        for ser in fileSchema['services']:
            service = os.path.join(destination_path, 'services', ser["name"])
            print(service)

            file = open(os.path.join(os.getcwd(), "contracts", "library.py"),"r")
            codelines = file.readlines()
            file.close()
            fileName =  os.path.join(service, "library.py")
            file = open(fileName,"w")
            file.writelines(codelines)
            file.close()
            
            file = open(os.path.join(os.getcwd(), "contracts", "new_kf_handler.py"),"r")
            codelines = file.readlines()
            file.close()
            fileName =  os.path.join(service, "new_kf_handler.py")
            file = open(fileName,"w")
            file.writelines(codelines)
            file.close()

            entryData = {}
            entryData["appId"] = appId
            entryData["applicationName"] = applicationName
            entryData["type"] = "service"
            entryData["name"] = ser["name"]

            shutil.make_archive(service, 'zip', service)
            # Upload the zip file to azure blob storage
            zipName = service + ".zip"
            print(zipName)
            blob_name = appId + "--" + ser["name"] + ".zip"
            blob_client = container_client.get_blob_client(blob_name)

            with open(zipName, "rb") as data:
                blob_client.upload_blob(data)
                
            log_message("validator-workflow", "DEBUG", f'blobData: {entryData}.')
            
            entryData["link"] = blob_client.url
            print(blob_client.url)
            blobCollection.insert_one(entryData)

            # delete the file from local storage
            print("deleting...")
            shutil.rmtree(service)
        
        workflowsPath = os.path.join(destination_path, 'workflows')
        for work in fileSchema["workflows"]:
            workflowName = work.split(".json")[0]
            workflow = os.path.join(destination_path, 'workflows', workflowName)
            print(workflow)
            entryData = {}
            entryData["appId"] = appId
            entryData["applicationName"] = applicationName
            entryData["type"] = "workflow"
            entryData["name"] = workflowName

            shutil.make_archive(workflow, 'zip', workflow)
            # Upload the zip file to azure blob storage

            zipName = workflow + ".zip"
            blob_name = appId + "--" + workflowName + ".zip"
            print(blob_name)
            blob_client = container_client.get_blob_client(blob_name)

            with open(zipName, "rb") as data:
                blob_client.upload_blob(data)
    
            entryData["link"] = blob_client.url
            print(blob_client.url)

            blobCollection.insert_one(entryData)
            log_message("validator-workflow", "DEBUG", f'blobData: {entryData}.')

            # delete the file from local storage
            print("deleting...")

        shutil.rmtree(destination_path)

        return "success"
    except:
        return "some error occured while uploading.. "

    
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    # app.run(debug = True)
    app.run(host = "0.0.0.0", port="8001", debug = True)
    