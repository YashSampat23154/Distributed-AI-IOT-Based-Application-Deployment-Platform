import os
from datetime import datetime
import logger as logger
import time

def run_docker_image(acr_info, service_info, contanarized_app_port, acr_image_path, service_name):

    node_info = service_info["node_info"]
    node_port = service_info["port"]

    print(f"Application/service deployment request recieved for platform service[{service_name}]")
    logger.log_message('DEBUG', f"Application/service deployment request recieved for platform service[{service_name}]")

    # generate new unique container name dynamically
    # acr_image_path = acr_info['login_server'] + '/' + image_name:latest
    # container_name = cnt_service_name_current_time
    current_time = datetime.now().strftime('%d-%m-%Y-%H-%M-%S-%f')
    container_name = f"cnt_{service_name}_{current_time}"

    logger.log_message('INFO', f'container name formed container[{container_name}]')

    commands = list()

    # give docker access to the private ACR
    commands.append(f"docker login {acr_info['login_server']} --username {acr_info['username']} --password {acr_info['password']}")
    
    # pull docker image from ACR
    commands.append(f"docker pull {acr_image_path}:latest")

    # deploy the pulled image on container
    # print(f"docker run -d -p {node_port}:{contanarized_app_port} --name {container_name} {acr_image_path}:latest")

    # un-comment the code of passing node_name, container_name and container_up_time
    container_up_time = datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f")

    if service_name == 'deployer':
        commands.append(f"docker run -d -p {node_port}:{contanarized_app_port} -e node_name={node_info['node_name']} -e container_name={container_name} -e container_up_time={container_up_time} -v $(pwd)/platform-deployer/services:/deployer/services --name {container_name} {acr_image_path}:latest")
        # commands.append(f"docker run -d -p {node_port}:{contanarized_app_port} -e ip={node_info['ip']} -e user_name={node_info['user_name']} -e password={node_info['password']} -v $(pwd)/platform-deployer/services:/deployer/services --name {container_name} {acr_image_path}:latest")
    else:
        commands.append(f"docker run -d -p {node_port}:{contanarized_app_port} -e node_name={node_info['node_name']} -e container_name={container_name} -e container_up_time={container_up_time} --name {container_name} {acr_image_path}:latest")
        # commands.append(f"docker run -d -p {node_port}:{contanarized_app_port} --name {container_name} {acr_image_path}:latest")

    # display the images in that VM/node
    commands.append("docker images")

    # display the containers in running state in that VM/node
    commands.append("docker ps")

    # revoke the docker access from the private ACR
    commands.append(f"docker logout {acr_info['login_server']}")

    # close ssh server connection with the VM/node
    commands.append("exit")

    command = ';'.join(commands)

    os.system(f"ssh-keyscan -H {node_info['ip']} >> ~/.ssh/known_hosts")

    os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} '" + command + "'")

    time.sleep(1)

    # check that is container really running
    # is these code running properly? Do stress testing
    container_status = os.popen(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} " +  "'docker inspect -f '{{.State.Status}}' " + container_name  + ";exit'", 'r', 1).read()

    container_status = container_status.split('\n')[0]

    if container_status == 'running':
        print(f"container_status => {container_status}")
        print(f"Deployment done successfully for platform service[{service_name}]")
        container_id = os.popen(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} " +  "'docker container ls --quiet --filter name=^" + container_name  + "$;exit'", 'r', 1).read()
        logger.log_message('DEBUG', f"Deployment done successfully container_status[{container_status}] for platform service[{service_name}]")
        return True, container_name, container_up_time, container_id

    print(f"Service not deployed for platform service[{service_name}]!! Some error in the code!!")
    logger.log_message('DEBUG', f"Service not deployed for platform service[{service_name}]")

    return False, None, None, None
