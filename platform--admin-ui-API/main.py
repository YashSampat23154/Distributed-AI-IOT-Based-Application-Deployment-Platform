from flask import Flask, request
import logs_filter
import instances_filter
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


@app.route("/live-logs", methods = ['GET'])
def get_all_logs():

    subsystem_name = request.args["subsystem_name"]
    subsystem_start_time = request.args["start_time"]

    print(subsystem_name)
    print(subsystem_start_time)

    logs = logs_filter.get_updated_logs(subsystem_name, subsystem_start_time)
    logs.headers.add("Access-Control-Allow-Origin", "*")


    return logs

@app.route("/get_subsystem_instances", methods = ['GET'])
def subsystem_details():
    
    subsystem_name = request.args["subsystem_name"]

    instances = instances_filter.get_instances(subsystem_name)
    instances.headers.add("Access-Control-Allow-Origin", "*")


    return instances


# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host = "0.0.0.0", port = 5000, debug=True)

