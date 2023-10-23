import pymongo
from bson.json_util import dumps, loads
from flask import jsonify

'''

format of the log stored in db
log_entry = {
        "subsystemName" : "Monitoring",
        "containerUpTime" : "xyz",
        "date": dateAndTime.strftime("%Y-%m-%d"),
        "time": dateAndTime.strftime("%H:%M:%S"),
        "severity": messageContents[0],
        "message": messageContents[1]
    }

Real logs as a sentence:
[severity] : [date][time] => <message>

containerUpTime : 'dd-mm-yyyy-H-M-S-MS'

'''

# Connect to python applicaiton

client = pymongo.MongoClient("mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority")

# Creating a new database if not found
db_object = client["LOGS"]


def get_updated_logs(subsystem_name, subsystem_start_time):

    # generate collection name
    log_collection_name = f"log-{subsystem_name}"

    print(log_collection_name)

    # get the collection object
    log_collection = db_object[log_collection_name]

    print(db_object.list_collection_names())

    # firstly select the logs based on given subsystemName and containerUpTIme

    # filteration conditions
    filter = {
        "subsystem_name" : subsystem_name,
        "container_up_time" : subsystem_start_time
    }

    # it will return the object of cursor
    logs_cursor = log_collection.find(filter, {'_id': 0}).sort([
            ('date', pymongo.ASCENDING),
            ('time', pymongo.ASCENDING)])


    logs = [log for log in logs_cursor]

    live_logs = {"logs" : logs}

    return jsonify(live_logs)
