import json
import os
import unzip_folder as unzip
import delete_things as delete_this
import logger as log

def generate_docker_file(app_name, service_name, app_sevice_name):
     
    print(f"Generating docker file for file[{app_sevice_name}] app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Generating docker file for file[{app_sevice_name}] app[{app_name}] service[{service_name}]")    

    # service_folder_name = app_id--service_name
    service_folder_name = unzip.unzipping(app_sevice_name)

    app_folder_path = f"./services/{service_folder_name}"

    file = open(app_folder_path + "/" + "config.json")
    data = json.load(file)

    docker_file_path = app_folder_path + "/" + "Dockerfile"

    delete_this.delete_the_file(docker_file_path)
    
    #This is the port at which our application will run on the VM
    contanarized_app_port = data["port"]

    log.log_message('INFO', f"Port on which app is listening is port[{contanarized_app_port}]")

    with open(os.open(docker_file_path, os.O_CREAT | os.O_WRONLY, 0o777), "a") as file:
        with open("Templates/dockerfile.template", "r") as l:
                code_template = l.read()
                install_cmd = data["command"]
                splitted = install_cmd.split()
                splitted = json.dumps(splitted)
                code = code_template.format(data["language"],data["workdir"],".",data["workdir"],data["package_installation_cmd"],splitted)
                file.write(code)   
        l.close()
    file.close()
    
    print(f"Docker file generated for file[{app_sevice_name}] app[{app_name}] service[{service_name}]")
    log.log_message('DEBUG', f"Docker file generated for file[{app_sevice_name}] app[{app_name}] service[{service_name}]")

    return service_folder_name, contanarized_app_port

