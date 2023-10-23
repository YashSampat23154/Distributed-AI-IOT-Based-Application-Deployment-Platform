import paramiko
import re

def get_containerwise_load(hostip, uname, password):
    host = hostip
    username = uname
    password = password

    try :
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host, username=username, password=password)

        print("Connection done")
        stdin, stdout, stderr = ssh_client.exec_command('docker ps') # ID Name CPU Mem/Lim Mem% 
        # print(stdout)
        containers = stdout.readlines()
        # output = stdout.readlines()
        image_redeploy = []

        for container in containers[1:]:

            container_id = re.findall(r'\w{12}', container)[0]
            print(container_id)
            stdin, stdout, stderr = ssh_client.exec_command(f'docker stats --no-stream {container_id}')
            stats = stdout.readlines()[1]

            cpu_usage = re.search(r'(\d+\.\d+)%', stats).group(1)
            
            cpu_usage = float(cpu_usage)

            # if cpu_usage > 80.0 :
            image_redeploy.append(container_id)
            # print(stats)

        return image_redeploy
      
    except Exception as e:
        print("Something unexpected",e)
        ssh_client.close()
        return []