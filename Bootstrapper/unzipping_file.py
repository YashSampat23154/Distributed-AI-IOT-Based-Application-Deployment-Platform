#It will take the file name to unzip as an argument.
import json
from zipfile import ZipFile
import os
from pathlib import Path
import logger as logger


def generate_dockerfile(app_sevice_name):
    
    print(f"Dockerfile generation started for app_service[{app_sevice_name}]")
    logger.log_message('DEBUG', f"Dockerfile generation started for app_service[{app_sevice_name}]")

    service_folder_name = unzipping(app_sevice_name)

    file = open(f'{service_folder_name}/config.json')
    
    data = json.load(file)

    docker_file_path = f'{service_folder_name}/Dockerfile'

    # delete the Dockerfile if already present
    delete_the_file(docker_file_path)

    # This is the port at which application service will be listening inside container
    contanarized_app_port = data["port"]

    print("making file")
    with open(os.open(docker_file_path, os.O_CREAT | os.O_WRONLY, 0o777), "a") as f:
        with open("Templates/dockerfile.template", "r") as l:
                code_template = l.read()
                print(f'This is the code template{code_template}')
                install_cmd = data["command"]
                splitted = install_cmd.split()
                splitted = json.dumps(splitted)
                code = code_template.format(data["language"],data["workdir"],".",data["workdir"],data["package_installation_cmd"],splitted)
                f.write(code)   
        l.close()
    f.close()

    print(f"Dockerfile generated successfully for app_service[{app_sevice_name}]")
    logger.log_message('DEBUG', f"Dockerfile generated successfully for app_service[{app_sevice_name}]")

    return service_folder_name, contanarized_app_port


def delete_the_file(file_to_delete):
    check = Path(file_to_delete)
        
    if(check.is_file()):
        os.remove(file_to_delete)

    return     

def delete_the_directory(folder_name_to_delete):
    check = Path(folder_name_to_delete)
    
    if(check.is_dir()):
        print("Present")
        command = "rm -r " + folder_name_to_delete
        os.system(command)
        print("Deleted the folder") 
    
    return


def unzipping(file_to_unzip):

    print(f'Unziiping the file[{file_to_unzip}]')
    logger.log_message('DEBUG', f'Unzipping the file[{file_to_unzip}]')

    folder_name = file_to_unzip.split(".")[0]

    delete_the_directory(folder_name)
    
    with ZipFile(file_to_unzip, 'r') as f:
        f.extractall(folder_name)

    print(f'File un-zipping completed for file[{file_to_unzip}]')
    logger.log_message('DEBUG', f'File un-zipping completed for file[{file_to_unzip}]')

    return folder_name
