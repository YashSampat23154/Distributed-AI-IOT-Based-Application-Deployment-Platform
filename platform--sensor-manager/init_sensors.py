import json
import pymongo

with open ('sensor_config.json', 'r') as file:
    json_data = file.read ()

json_data = json.loads (json_data)

upload_data = json_data ['sensors']

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["sensordb"]
mycol = mydb["sensors"]

mycol.insertmany (upload_data)