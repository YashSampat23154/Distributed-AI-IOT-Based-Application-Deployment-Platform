import os
import loggingMessage as logfile
from globalVariables import *

#VM details needed from the caller:
#1. vm password
#2. vm name
#3. vm ip
#4. Container id/name needed

# node_id is the key linked to the 1,2,3
def reinitiate_container(container_name, node_id):

    filter = {"node_name": node_id} # Takes O(log n)

    # Check whether this entry exists
    nodeInfo = vmCollection.find_one(filter)

    # If the entry exists, get the values
    if nodeInfo is not None:
        vm_name = nodeInfo["user_name"]
        vm_ip = nodeInfo["ip"]
        vm_pswd = nodeInfo["password"]
        commands = list()
        commands.append(f"docker stop {container_name}")
        commands.append(f"docker start {container_name}")
        commands.append("docker ps -a")
        commands.append("exit")
        command = ';'.join(commands)
        try:
            os.system(f"sshpass -p {vm_pswd} ssh {vm_name}@{vm_ip} '" + command + "'")
        except:
            log_message=f' Unable to run scripts at node with {node_id} is not found'
            logfile.log_message('monitoring-fault-tolerance','ERROR',log_message)

    # If the document does not exist.
    else : 
        log_message=f' The entry in DB for node with {node_id} is not found'
        logfile.log_message('monitoring-fault-tolerance','ERROR',log_message)

    return



# reinitiate_container('cont_ldap','sid_node') #just for testing purposes.. The specified container id made to run