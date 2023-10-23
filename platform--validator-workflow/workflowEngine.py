# We will provide api end points for our platform microservice...Therefore app developer will have to use those endpoints 
# and integrate in their code. Hence, there will not be any platform service in workflow..
import os
import json
import shutil

def generateWorkflow(dirPath, fileName):
    filePath = os.path.join(dirPath, fileName)
    # print("worklowengine: ", filePath)
    workflowJsonPath = filePath
    with open(workflowJsonPath, 'r') as f:
        data = json.load(f)
    if fileName.split(".json")[0] != data["workflowName"]:
        # print("filename and workflow name not matching")
        return f'filename and workflow name not matching for {data["workflowName"]}.'

    codelines = [ "from flask import Flask, request, jsonify\n",  "from library import serviceReq\n", "from dotenv import load_dotenv\n", 
        "from pymongo import MongoClient\n", "import threading\n", "import uuid\n\n", "load_dotenv()\n", "app = Flask(__name__)\n\n"]    
    codelines.append("def helper(workflowInputs):\n")
    codelines.append("    appId = workflowInputs[\"appId\"]\n")
    codelines.append("    requestId = workflowInputs[\"requestId\"]\n\n")

    services = data["services"]
    for service in services:
        line = "    " + service["serviceName"] + "JsonInput = { 'appId' : appId, 'serviceName' : '" + service["serviceName"] + "'"
        for i in range(len(service["parameters"])):
            line += ", "            
            par = service["parameters"][i]
            line += "\"" + par["name"] + "\" : "            
            if par["prevOutput"]:
                line += par["prevServiceName"] + "Output['" + par["prevOutputName"] + "']"
            else:
                line += "workflowInputs['"+ par["workflowInputName"] + "']"
        line += " }\n"
        codelines.append(line)

        line = "    " +  service["serviceName"] + "Output =  serviceReq(" + service["serviceName"] + "JsonInput )"
        codelines.append(line)
        codelines.append("\n\n")

    line  = "    response_data = { " 
    for i in range(len(data["workflowOuputs"])):
        out = data["workflowOuputs"][i]

        line += "'" +  out["parameterName"] + "' :" + out["serviceName"] + "Output['" + out["serviceParName"] + "']"
        if i + 1 < len(data["workflowOuputs"]):
            line += ", "
    line += " }\n\n"
    codelines.append(line)
    codelines.append("    mongo = MongoClient(\"mongodb+srv://pranshu_mongo:sexynaina@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority\")\n")
    codelines.append("    db = mongo[\"IAS_test_1\"]\n")
    codelines.append("    col = db[\"responses\"]\n\n")
    codelines.append("    data = { 'appId' : appId, 'requestId' : requestId, 'response_data' : response_data }\n")
    codelines.append("    col.insert_one(data)\n\n\n")

    lines = [ "@app.route('/', methods=['POST'])", "\n", "def workflow():", "\n\n", "    requestId = str(uuid.uuid1())\n", 
        "    workflowInputs = request.get_json()\n", "    workflowInputs[\"requestId\"] = requestId\n\n", "    t1 = threading.Thread(target=helper, args=(workflowInputs,))\n", "    t1.start()\n\n"]
    codelines += lines
    codelines.append("    response = jsonify({'message': 'Processing!', 'requestId' : requestId })\n")
    codelines.append("    response.status_code = 200\n") 
    codelines.append("    return response\n\n")


    codelines.append("if __name__ == '__main__':\n")
    codelines.append("    app.run(host = \"0.0.0.0\", port = \"8001\", debug = True)\n")

    dirPath = filePath.split(".json")[0]
    # print(dirPath)
    os.mkdir(dirPath)

    fileName =  os.path.join(dirPath, data["workflowName"] + ".py")
    file = open(fileName,"w")
    file.writelines(codelines)
    file.close()

    reqlines = ["Flask==2.2.3\n", "python-dotenv==1.0.0\n", "requests==2.28.2\n", "pymongo==4.3.3\n"]
    file = open(os.path.join(dirPath, "requirements.txt"),"w")
    file.writelines(reqlines)
    file.close()

    configLines = [ "{\n", "    \"language\": \"python:3.10-alpine\",\n", "    \"workdir\": \"/myapp\",\n",  "	\"port\": \"8001\",\n"]
    line = "    \"command\": \"python3 /myapp/" + data["workflowName"] + ".py\", \n"
    configLines.append(line)
    configLines.append("    \"packages_file_path\": \"/myapp/requirements.txt\", \n")
    configLines.append("    \"package_installation_cmd\": \"pip install -r /myapp/requirements.txt\"\n")
    configLines.append("}") 

    file = open(os.path.join(dirPath, "config.json"),"w")
    file.writelines(configLines)
    file.close()
    
    file = open(os.path.join(os.getcwd(), "contracts", "library.py"),"r")
    codelines = file.readlines()
    file.close()
    fileName =  os.path.join(dirPath, "library.py")
    file = open(fileName,"w")
    file.writelines(codelines)
    file.close()
    
    file = open(os.path.join(os.getcwd(), "contracts", "new_kf_handler.py"),"r")
    codelines = file.readlines()
    file.close()
    fileName =  os.path.join(dirPath, "new_kf_handler.py")
    file = open(fileName,"w")
    file.writelines(codelines)
    file.close()
    
    return "success"


if __name__ == "__main__":
    generateWorkflow(os.path.join(os.getcwd(), "contracts"),"sampleWorkflowInfo.json")