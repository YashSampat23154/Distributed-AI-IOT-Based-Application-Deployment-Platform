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

1. 
endpoint = /live-logs/<subsystem_name>/<start_time>
method = GET
response_format = json
response = {
    "logs" : [
        {
            log_entry
        },
        {
            log_entry
        },
        ....
    ]
}

2. endpoint = /get_subsystem_instances/<subsystem_name>
method = GET
response_format = json
response = {
    "subsystem_name" : "node-manager",
    "instances" : [
        {
            "instance_name" : "node-manager_<container_up_time>"
        },
        {
            "instance_name" : "node-manager_<container_up_time>"
        },
        {
            "instance_name" : "node-manager_<container_up_time>"
        }
        ....
    ]
}

3. Format of logs to display on UI

Real logs as a sentence:
[severity] : [date][time] => <message>