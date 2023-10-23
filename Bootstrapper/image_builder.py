import os
from datetime import datetime
import logger as logger

# service_registry

def build_image(service_name, folder_path):

    print(f'Building image for platform service[{service_name}]')
    logger.log_message('DEBUG', f'Building image for platform service[{service_name}]')

    image_name = f"{service_name}_{datetime.now().strftime('%Y%m-%d%H-%M%S')}"

    print(f"Image name generated image[{image_name}]")
    logger.log_message('INFO', f"Image name generated image[{image_name}]")

    command = f'docker build -t {image_name}:latest ./{folder_path}'
    os.system(command)

    print(f'Image built successfully for platform service[{service_name}]')
    logger.log_message('DEBUG', f'Image built successfully for platform service[{service_name}]')

    return image_name


def push_docker_image(image_name, acr_info, service_name):

    print(f'Pushing image to ACR for platform service[{service_name}]')
    logger.log_message('DEBUG', f'Pushing image to ACR for platform service[{service_name}]')

    # with these name the image will be stored inside ACR
    # path where image is stored inside ACR
    acr_image_path = acr_info["login_server"] + "/" + image_name

    print(f'ACR image path[{acr_image_path}]')
    logger.log_message('INFO', f'ACR image path[{acr_image_path}]')

    # image-tagging before pushing to ACR
    os.system(f"docker tag {image_name}:latest {acr_image_path}:latest")
    
    # give docker access to the private ACR
    os.system(f"docker login {acr_info['login_server']} --username {acr_info['username']} --password {acr_info['password']}")
    print('ACR login successfull')
    logger.log_message('INFO', 'ACR login successfull')

    # push the tagged image to ACR
    os.system(f"docker push {acr_image_path}:latest")
    print(f"Image {image_name} pushed to ACR successfully!!")
    logger.log_message('INFO', f"Image {image_name} pushed to ACR successfully for platform service[{service_name}]")
    
    # revoke the docker access from the private ACR
    os.system(f"docker logout {acr_info['login_server']}")
    print("Logged out from ACR!!")
    logger.log_message('INFO', "Logged out from ACR!!")
    # print(logout_status)

    # remove image from the container storage after pushing it to ACR
    # image_remove_status = os.popen(f"docker rmi {acr_image_path}:latest", 'r', 1).read()
    # print(f"image {acr_image_path} removed successfully from local !! status : {image_remove_status}")
    # image_remove_status = os.popen(f"docker rmi {image_name}:latest", 'r', 1).read()
    # print(f"image {image_name} removed successfully from local !! status : {image_remove_status}")

    return acr_image_path
