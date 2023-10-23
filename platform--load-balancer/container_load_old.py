import paramiko

def get_containerwise_load(hostip, uname, password):
    host = hostip
    username = uname
    password = password

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, username=username, password=password)

    stdin, stdout, stderr = ssh_client.exec_command('docker stats') # ID Name CPU Mem/Lim Mem% 
    output = stdout.readlines()
    
    image_redeploy = []
    for i in range(2, len(output) - 1):
        cpu_use = float(output[i].split()[3][:-1])
        mem_use = float(output[i].split()[7][:-1])

        load = 2*(cpu_use*mem_use)/(cpu_use + mem_use)

        if(load > 50):
            image_redeploy.append(output[i].split()[0])


    ssh_client.close()

    return image_redeploy

