import os
import service_registry
from datetime import datetime
import global_variables

def start_kafka_server(node_info):

    print('Deploying kafka server')

    os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} 'mkdir kafka;exit'")

    os.system(f"sshpass -p {node_info['password']} scp -r $PWD/docker-compose.yml {node_info['user_name']}@{node_info['ip']}:~/kafka")

    os.system(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} 'cd kafka;docker compose up -d;docker ps;exit'")

    container_id = os.popen(f"sshpass -p {node_info['password']} ssh {node_info['user_name']}@{node_info['ip']} " +  "'docker container ls --quiet --filter name=^redpanda-0$;exit'", 'r', 1).read()

    print(f"container id of kafka : {container_id}")    

    service_entry = {
            "app_name" : "platform",
            "service_name": 'kafka',
            "app_id": datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f"),
            "port": 19092,
            "container_up_time": global_variables.CONTAINER_UP_TIME,
            "container_name": 'redpanda-0',
            "node_name": node_info['node_name'],
            "ip": node_info['ip'],
            "container_id": container_id
    }

    service_registry.add_service_info(service_entry)

    print("Kafka server started")

