from datetime import datetime
import download_from_blob as blob
import generate_dockerfile as dockerfile
import os
import global_variables
import logger as log


def build_and_push_image(app_id, app_name, service_name, app_folder_name, acr_info):

    node_info = global_variables.node_info

    print(f"Building image for app : {app_name} service : {service_name}")
    log.log_message('DEBUG', f"Building image for app[{app_name}] service[{service_name}]")

    now = datetime.now()
    current_time = now.strftime("%d_%m_%Y_%H_%M_%S_%f")
    # image_name = [app_name]_[service_name]_[app_id]:1.0_[current_time]
    image_name = f"{app_name}_{service_name}_{app_id}:1.0_{current_time}" # Add unique name here using time

    # path where image is stored inside ACR
    acr_image_path = acr_info["login_server"] + "/" + image_name

    print(f'arc_image_path formed for app[{app_name}] service[{service_name}]')
    log.log_message('INFO', f'arc_image_path formed for app[{app_name}] service[{service_name}]')

    commands = list()

    # go inside the platform-deployer/services folder/
    commands.append("cd platform-deployer/services/")

    # build docker image
    commands.append(f'docker build -t {image_name} ./{app_folder_name} -q')

    # image-tagging before pushing to ACR
    commands.append(f"docker tag {image_name} {acr_image_path}")
    
    # give docker access to the private ACR
    commands.append(f"docker login {acr_info['login_server']} --username {acr_info['user_name']} --password {acr_info['password']}")

    # push the tagged image to ACR
    commands.append(f"docker push {acr_image_path}")
    
    # revoke the docker access from the private ACR
    commands.append(f"docker logout {acr_info['login_server']}")

    # logging out from the VM
    commands.append("exit")

    command = ';'.join(commands)

    os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} '" + command + "'")


    # take the code of image removal from platform-initializer module

    # remove image from the container storage after pushing it to ACR
    # image_remove_status = os.popen(f"docker rmi {acr_image_path}", 'r', 1).read()
    # print(f"image {acr_image_path} removed successfully from local !! status : {image_remove_status}")
    # image_remove_status = os.popen(f"docker rmi {image_name}", 'r', 1).read()
    # print(f"image {image_name} removed successfully from local !! status : {image_remove_status}")

    log.log_message('INFO', f'ACR image path formed [{acr_image_path}]')

    print(f'Image built and pushed to ACR for app[{app_name}] service[{service_name}] with image_name[{image_name}]')
    log.log_message('DEBUG', f'Image built and pushed to ACR for app[{app_name}] service[{service_name}] with image_name[{image_name}]')

    return acr_image_path

def build_and_store_image(app_id, app_name, service_name):

    print(f"Start building and storing image for app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Start building and storing image for app[{app_name}] service[{service_name}]")

    # download the zip file from bolb storage
    # zip_name = app_id--service_name.zip
    zip_name = blob.download_the_zip_file(app_id, app_name, service_name)

    if zip_name != None:

        # generate dockerfile
        # service_folder_name = app_id--service_name
        service_folder_name, contanarized_app_port = dockerfile.generate_docker_file(app_name, service_name, zip_name)

        # push the image to ACR
        acr_image_path = build_and_push_image(app_id, app_name, service_name, service_folder_name, global_variables.acr_info)

        print(f'Image building and storing completed for app[{app_name}] service[{service_name}] !!')
        log.log_message('DEBUG', f'Image building and storing completed for app[{app_name}] service[{service_name}] !!')

        return acr_image_path, contanarized_app_port
    
    else:
        print(f'Image building failed due to null zip name for app[{app_name}] service[{service_name}]')
        log.log_message('ERROR', f'Image building failed due to null zip name for app[{app_name}] service[{service_name}]')

    return None, None


# check these code for better coding practice

# data = {"user": "pi",
#         "host": "172.16.0.141",
#         "password": "VerySecret",
#         "commands": " " .join(sys.argv[1:])}

# command = "sshpass -p {password} ssh {user}@{host} {commands}"
# os.system(command.format(**data))