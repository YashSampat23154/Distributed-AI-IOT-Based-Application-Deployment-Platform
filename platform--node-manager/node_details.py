import paramiko
from db_queries import *
from loggingMessage import *

def create_new_node():
    log_message("node-manager", "DEBUG", "Creating a new Node")
    node = get_free_node()
    container_port = None
    try:
        make_node_active(node["node_name"])
        host = node["ip"]
        username = node["user_name"]
        password = node["password"]
        node_name = node["node_name"]

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host, username=username, password=password)

        stdin, stdout, stderr = ssh_client.exec_command('sudo netstat -tulpn')
        output = stdout.readlines()

        used_ports = []
        for i in range(2, len(output)):
            used_ports.append(output[i].split()[3].split(':')[-1])
        
        # add already sended ports from the database.
        used_ports.extend(get_used_port(node_name))
        container_port = None
        for i in range(9000, 10000):
            if(i not in used_ports):
                container_port = i
                add_port(node_name, container_port)
                break
    except Exception as e:
            print(f"Error while creating new node : {e}")
            log_message("node-manager", "DEBUG", f"Error while creating new node : {e}")


    return node, container_port



def check_node(hostip, uname, password):    
    host = hostip
    username = uname
    password = password

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, username=username, password=password)


    stdin, stdout, stderr = ssh_client.exec_command('top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\\1/"')
    cpu_usage = float(stdout.read().decode('utf-8').strip())

    stdin, stdout, stderr = ssh_client.exec_command('docker ps')
    output = stdout.readlines()
    
    print(output)
    if(len(output) < 2):
        free_node(uname)



def get_node_details(node_name, hostip, uname, password):
    host = hostip
    username = uname
    password = password
    
    log_message("node-manager", "DEBUG", f"Fetching Details of Node : {node_name}")
    
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, username=username, password=password)


    stdin, stdout, stderr = ssh_client.exec_command('top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\\1/"')
    cpu_usage = float(stdout.read().decode('utf-8').strip())
    # print(stdout.read().decode('utf-8').strip())
    # print(cpu_usage)

    stdin, stdout, stderr = ssh_client.exec_command('top -bn1')
    output = stdout.readlines()
    # print(*output)
    usage = 0
    try:
        usage = 100 - float(output[2].split()[7])
    except:
        try:
            usage = 100 - float(output[2].split()[7])
        except:
            try:
                usage = 100 - float(output[2].split()[7])
            except Exception as e:
                print(f"Error while getting CPU usage : {e}")
                log_message("node-manager", "DEBUG", f"Error while getting CPU usage of Node : {node_name} : {e}")

    
    total_memory = float(output[3].split()[3])
    available_memory = float(output[3].split()[5])
    memory_usage_percentage = (total_memory - available_memory) / total_memory * 100
    print("memory usage:", memory_usage_percentage)
    
    stdin, stdout, stderr = ssh_client.exec_command('sudo netstat -tulpn')
    output = stdout.readlines()

    used_ports = []
    # print(*output)
    for i in range(2, len(output)):
        # print(output[i].split()[3].split(':')[-1])
        used_ports.append(output[i].split()[3].split(':')[-1])
    container_port = None
    used_ports.extend(get_used_port(node_name))

    for i in range(9000, 10000):
        if(i not in used_ports):
            container_port = i
            add_port(node_name, container_port)
            break
    
    print(container_port)



    ssh_client.close()

    return usage, memory_usage_percentage, container_port