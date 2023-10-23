import os
from datetime import datetime
import logger as log


def run_docker_image(acr_info, node_info, contanarized_app_port, acr_image_path, app_name, service_name):

    print(f"Deploying image started for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Deploying image started for app[{app_name}] service[{service_name}]")

    now = datetime.now()
    current_time = now.strftime("%d_%m_%Y_%H_%M_%S_%f")

    # generate new unique container name dynamically
    # container_name = cnt_{app_name}_{service_name}_{app_id}_current_time
    container_name = f'cnt_{(acr_image_path.split("/")[1]).split(":")[0]}_{current_time}'

    log.log_message('INFO', f'container name formed container[{container_name}]')
    print(f'container name formed container[{container_name}]')

    print(f'app port[{contanarized_app_port}]')
    log.log_message('INFO', f'app port[{contanarized_app_port}]')

    commands = list()

    # give docker access to the private ACR
    commands.append(f"docker login {acr_info['login_server']} --username {acr_info['user_name']} --password {acr_info['password']}")
    
    # pull docker image from ACR
    commands.append(f"docker pull {acr_image_path}")
    
    # run docker image
    # change docker run if request is for platform sub-systems/services
    commands.append(f"docker run -d -p {node_info['port']}:{contanarized_app_port} --name {container_name} {acr_image_path}")

    # dislay the list of images on given VM
    commands.append("docker images")

    # display the running containers on VM
    commands.append("docker ps")

    # revoke the docker access from the private ACR
    commands.append(f"docker logout {acr_info['login_server']}")

    # logging out from the VM
    commands.append("exit")

    command = ';'.join(commands)

    os.system(f"ssh-keyscan -H {node_info['ip']} >> ~/.ssh/known_hosts")
    
    # execute the commands on azure VM power-shell
    os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} '" + command + "'")

    # check that is container really running
    # is these code running properly? Do stress testing
    container_status = os.popen(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} " +  "'docker inspect -f '{{.State.Status}}' " + container_name  + ";exit'", 'r', 1).read()

    container_status = container_status.split('\n')[0]

    if container_status == 'running':
        print(f"container_status => {container_status}")
        print(f"Deployment done successfully for app[{app_name}] service[{service_name}]")
        # get the container id of the container 
        container_id = os.popen(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} " +  "'docker container ls --quiet --filter name=^" + container_name  + "$;exit'", 'r', 1).read()
        log.log_message('DEBUG', f"Deployment done successfully container_status[{container_status}] for app[{app_name}] service[{service_name}]")
        return True, container_name, container_id

    print(f"Service not deployed for app[{app_name}] service[{service_name}]!! Some error in the code!!")
    log.log_message('DEBUG', f"Service not deployed for app{app_name} service[{service_name}]")

    return False, None, None
