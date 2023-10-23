import node_info 
import os

acr_info = {
    "login_server" : "testimages01.azurecr.io", 
    "username" : "testimages01", 
    "password" : "EnQFZBylKmDFlOEPuf1LQ3ZYvKxxlbb1Qd8uYdXGQw+ACRBcl3xB"
}

'''

node_1 = kafka, logger(8002)
node_2 = validator-workflow(8007), scheduler(8008)
node_4 = node-manager(8004), load-balancer(8005)
node_5 = monitoring-fault-tolerance(8009), api-gateway(8013)
node_6 = deployer(8006), paltform-ui(8005), platform-backend(8003), sensor-manager(8012), sensor-api-gateway(8025)

'''


platform_services = {

    "platform-ui" : {
        "port" : 8005,
        "node_info" : node_info.node_6
    },
    "platform-backend" : {
        "port" : 8011,
        "node_info" : node_info.node_6
    },
    "deployer" : {
        "port" : 8006,
        "node_info" : node_info.node_6
    },
    "logger" : {
        "port" : 8002,
        "node_info" : node_info.node_1
    },
    "api-gateway": {
        "port": 8013,
        "node_info": node_info.node_5
    },
    "node-manager" : {
        "port" : 8004,
        "node_info" : node_info.node_4

    },
    "load-balancer" : {
        "port" : 8005,
        "node_info" : node_info.node_4

    },
    "validator-workflow" : {
        "port" : 8007,
        "node_info" : node_info.node_2
    },
    "scheduler" : {
        "port" : 8008,
        "node_info" : node_info.node_2
    },
    "monitoring-fault-tolerance": {
        "port" : 8009,
        "node_info": node_info.node_5
    },
    "sensor-manager": {
        "port" : 8012,
        "node_info": node_info.node_6
    },
    "sensor-api-gateway": {
        "port": 8025,
        "node_info": node_info.node_6
    }

}

def setup_ssh(nodes):
    for node in nodes:
        print(f"\nsshkey scan setup for node : {node['ip']}\n")
        os.system(f"ssh-keyscan -H {node['ip']} >> ~/.ssh/known_hosts")