#!/bin/bash

sudo apt install net-tools

sudo apt -y install python3-pip

sudo apt-get update

# install package for ssh connection
sudo apt-get install sshpass

sudo pip install azure-storage-blob

sudo pip install python-dotenv

sudo pip install python-kafka

sudo pip install pymongo

# adding the fingerprint of out host IP to the remote network of VM	
# ssh-keyscan -H 20.193.154.7 >> ~/.ssh/known_hosts

# for bash script $1 = vm_host_ip
ssh-keyscan -H $1 >> ~/.ssh/known_hosts

# execute the below commands for docker enviornment setup

sudo apt-get update

sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg
    
sudo mkdir -m 0755 -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  
sudo apt-get update
 
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo apt  install -y docker-compose

# used for giving permission to the docker command to run as it needs root access or give the previledged access
# of the user from docker group.

sudo usermod -aG docker $USER
newgrp docker

# add code for adding platform-deployer/services/ folder
mkdir platform-deployer
cd platform-deployer
mkdir services