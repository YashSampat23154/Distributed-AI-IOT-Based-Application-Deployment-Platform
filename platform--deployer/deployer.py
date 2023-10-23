import kafka_talks
import logger as log
import image_builder, image_deployer, os
from dbinteraction import getAppData, setAppdata
import global_variables
from datetime import datetime, time
import service_registry
import node_db


def serve_build_request(app_id, app_name, service_name):

    print(f"Start building image for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Start building image for app[{app_name}] service[{service_name}]")

    # first check that is image already built for the given app and service
    app_data, image_status = getAppData(app_id, service_name)

    if image_status == False:

        # build the image store to ACR, and get image_path and app_port
        acr_image_path, contanarized_app_port = image_builder.build_and_store_image(app_id, app_name, service_name)

        if acr_image_path != None and contanarized_app_port != None:
            # sid has to store these info into mongo-db
            dataInserted = setAppdata(app_id, app_name, service_name, acr_image_path, contanarized_app_port)

        print(f"Building image completed for app[{app_name}] service[{service_name}]")
        log.log_message('DEBUG', f"Building image completed for app[{app_name}] service[{service_name}]")
    
    else:
        print(f'Image already built and stored in ACR for app[{app_name}] service[{service_name}]')
        log.log_message('DEBUG', f'Image already built and stored in ACR for app[{app_name}] service[{service_name}]')


    print(f"Building image completed for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Building image completed for app[{app_name}] service[{service_name}]")

    return True

def serve_run_request(app_id, app_name, service_name):

    print(f"Request came for deploying app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Request came for deploying app[{app_name}] service[{service_name}]")

    # producing request to load-balancer for best node
    # change these request formats ask to advait bhai
    message = {"message":"Node Required"} 
    kafka_talks.send_using_kafka("getNodeRequest",message)

    print("Message produced to load-balancer.....")
    log.log_message('INFO', "Message produced to load-balancer.....")

    print("Waiting for reply from load-balancer.....")
    log.log_message('INFO', "Waiting for reply from load-balancer.....")

    # consuming the response from load-balancer
    node_info = kafka_talks.receive_using_kafka("bestNodeResponse")
    print("Reply from load-balancer = ", node_info)
    log.log_message('DEBUG', f"Reply from loab-balancer = {node_info}")

    # sid has to write query to fetch port and acr_image_path form mongo-db
    # first check that do we have image or not
    app_data, image_status = getAppData(app_id, service_name)

    if image_status == True:

        contanarized_app_port = app_data['port']
        acr_image_path = app_data['acr_img_path']

        deployment_status, container_name, container_id = image_deployer.run_docker_image(global_variables.acr_info, node_info, contanarized_app_port, acr_image_path, app_name, service_name)

        if deployment_status == True:
            # send success message to node-manager => jeet
            success_msg_node_manager =  {
                "app_name" : app_name,
                "service_name": service_name,
                "app_id": app_id,
                "port": node_info["port"],
                # format of container_up_time = 'dd-mm-yyyy-H-M-S-MS'
                "container_up_time": datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f"),
                "container_name": container_name,
                "node_name": node_info["node_name"],
                "ip": node_info["ip"],
                "container_id": container_id
            }

            print(f"sending response to node-manager : \n{success_msg_node_manager}")
            kafka_talks.send_using_kafka("getServiceDetailsRequest", success_msg_node_manager)
            print(f"message sent sucessfully!! to node-manager")

        else:
            # do something when failure happens
            # we can say to app-developer that some error is present in the code, service
            # cannot be deployed
            return False
    else:
        print(f'Image not found for app[{app_name}] service[{service_name}]')
        log.log_message('DEBUG', f'Image not found for app[{app_name}] service[{service_name}]')
        return False
    
    print(f"Request served for deploying app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Request served for deploying app[{app_name}] service[{service_name}]")

    return True

def serve_build_and_run_request(app_id, app_name, service_name):

    print(f"Start build and run process for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Start build and run process for app[{app_name}] service[{service_name}]")

    # first check that is image already built for the given app and service
    app_data, image_status = getAppData(app_id, service_name)

    acr_image_path, contanarized_app_port = None, None
    
    print(f'app-data:  {app_data} image_status: {image_status}')
    if image_status == False:
        # build the image store to ACR, and get image_path and app_port
        acr_image_path, contanarized_app_port = image_builder.build_and_store_image(app_id, app_name, service_name)
    
    else:
        # fetch acr path and port info from db
        acr_image_path, contanarized_app_port = app_data['acr_img_path'], app_data['port']
    
    if acr_image_path != None and contanarized_app_port != None:
        
        # sid has to store these info into mongo-db
        dataInserted = setAppdata(app_id, app_name, service_name, acr_image_path, contanarized_app_port)
        print('Appservice data inserted in db(inside build-run): ', dataInserted)

        # producing request to load-balancer for best node
        message = {"message":"Node Required"} 
        kafka_talks.send_using_kafka("getNodeRequest",message)

        print("Message produced to load-balancer.....")

        print("Waiting for reply from load-balancer.....")

        # consuming the response from load-balancer
        node_info = kafka_talks.receive_using_kafka("bestNodeResponse")
        '''
            node_info = {
                "node_name" : "",
                "user_name" : "",
                "password" : "",
                "ip" : "",
                "port": ""
            }
        '''
        print(f"Reply from load-balancer = {node_info}")

        deployment_status, container_name, container_id  = image_deployer.run_docker_image(global_variables.acr_info, node_info, contanarized_app_port, acr_image_path, app_name, service_name)

        if deployment_status == True:
            # send success message to node-manager => jeet
            success_msg_node_manager =  {
                "app_name" : app_name,
                "service_name": service_name,
                "app_id": app_id,
                "port": node_info["port"],
                # format of container_up_time = 'dd-mm-yyyy-H-M-S-MS'
                "container_up_time": datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f"),
                "container_name": container_name,
                "node_name": node_info["node_name"],
                "ip": node_info["ip"],
                "container_id": container_id
            }

            print(f"sending response to node-manager : \n{success_msg_node_manager}")
            kafka_talks.send_using_kafka("getServiceDetailsRequest", success_msg_node_manager)
            print(f"message sent sucessfully!! to node-manager")
        
        else:
            # do something when failure happens
            # we can say to app-developer that some error is present in the code, service
            # cannot be deployed
            print(f"Some error occurred in code for app[{app_name}] service_name[{service_name}]!! Notify app-developer")
            log.log_message('ERROR', f"Some error occurred in code for app[{app_name}] service_name[{service_name}]!! Notify app-developer")
            return False
    
    else:
        print(f"ACR image path and app port not found for app[{app_name}] service[{service_name}]")
        log.log_message('ERROR', f"ACR image path and app port not found for app[{app_name}] service[{service_name}]")
        return False
    
    print(f"Build and run process completed for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Build and run process completed for app[{app_name}] service[{service_name}]")

    return True

def serve_stop_request(app_id, app_name, service_name):

    print(f"Start stop process for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Start stop process for app[{app_name}] service[{service_name}]")

    service_info = service_registry.get_service_info(app_id, service_name)

    if service_info != None:

        container_name = service_info['container_name']

        node_info = node_db.get_node_info(service_info['node_name'])

        container_status = os.popen(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} " +  "'docker inspect -f '{{.State.Status}}' " + container_name + "'", 'r', 1).read()

        container_status = container_status.split('\n')[0]

        if container_status == 'running':

            commands = list()

            commands.append(f"docker stop {container_name}")
            commands.append(f"docker rm {container_name}")
            commands.append('exit')

            command = ';'.join(commands)

            os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} '" + command + "'")

            time.sleep(1)

            container_status = os.popen(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} '" + "'docker inspect -f '{{.State.Status}}' " + container_name  + ";exit'", 'r', 1).read()

            container_status = container_status.split('\n')[0]

            if container_status == 'running':
                print("Container is not down...Still Running")
                log.log_message('INFO', "Container is not down...Still Running")

            else :
                print("Container stopped successfully")
                log.log_message('ERROR', f"Container stopped successfully for app[{app_name}] service[{service_name}]")
        else:
            print(f"Container[{container_name}] not available in running state for app[{app_name}] service[{service_name}]")
            log.log_message('ERROR', f"Container[{container_name}] not available in running state for app[{app_name}] service[{service_name}]")
            return False

    else:
        print(f"Service info not found for app[{app_name}] service[{service_name}]")
        log.log_message('ERROR', f"Service info not found for app[{app_name}] service[{service_name}]")
        return False

    print(f"Stop completed for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Stop process completed for app[{app_name}] service[{service_name}]")

    return True
        
def serve_start_request():
    pass




