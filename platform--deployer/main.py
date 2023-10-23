#THIS WILL EXECUTE ALL THE CODES NEED TO DEPLOY AN APPLICATION.
from kafka_talks import send_using_kafka
from kafka_talks import receive_using_kafka
import threading, global_variables, deployer
from dbinteraction import getAppData, setAppdata
import logger as log
import global_setup
import heartbeatGenerator as heartbeat

global_setup.setup_global_env()


print("[+] Deployer server listening....")
log.log_message('DEBUG', "[+] Deployer server listening....")

def initiating_deployer_process(scheduler_request):    

    app_id = scheduler_request['appId']
    app_name = scheduler_request['appName']
    service_names = scheduler_request['serviceName']
    schedule_type = scheduler_request['scheduleType']

    services_failed = list()

    print(f"Starting deployer process for app[{app_name}] app_id[{app_id}]")
    log.log_message('DEBUG', f"Starting deployer process for app[{app_name}] app_id[{app_id}]")

    for service_name in service_names:
        service_status = True

        # code for just building an docker image if already not built
        if schedule_type == 'build':
            service_status = deployer.serve_build_request(app_id, app_name, service_name)

        # run the image of given app_name, service_name which is already stored in ACR
        elif schedule_type == 'run':
            service_status = deployer.serve_run_request(app_id, app_name, service_name)

        # build the image if already not built and then run the image stored in ACR
        elif schedule_type == 'build-run':
            service_status = deployer.serve_build_and_run_request(app_id, app_name, service_name)

        # start the container after doing proper validation of container existence
        elif schedule_type == 'start':
            pass

        # start the container after doing proper validation of container existence
        elif schedule_type == 'stop':
            service_status = deployer.serve_build_and_run_request(app_id, app_name, service_name)

        if service_status == False:
            services_failed.append(service_name)

    # send failure message seperately for each service

    print(f"sending response to scheduler : \n {scheduler_request}")
    
    if not services_failed:
        scheduler_request['status'] = True
    
    else:
        scheduler_request['status'] = False
        scheduler_request['services'] = services_failed
    
    send_using_kafka("deployerToScheduler", scheduler_request)
    print(f"message sent sucessfully!! to scheduler")


# Thread is created for heartbeat monitoring
t1 = threading.Thread(target=heartbeat.sendheartBeat, args=("heartbeat-deployer", global_variables.container_name, global_variables.node_name, ))
t1.start()


# start point of the code listening to the scheduler request
while True:
    print("Waiting for scheduler request")
    log.log_message('DEBUG', "Waiting for scheduler request")
    scheduler_request = receive_using_kafka("schedulerToDeployer")

    '''
        scheduler_request = {
            'appId' : unique application id
            'appName' : application-name given by app-developer
            'serviceName' : list of service-name of applicaion,
            'scheduleType' : 'build', 'build-run', 'start', 'stop', 'run'
            'accessToken' : token coming from the requester which I will send in response back
            'kafkaTopic' : 'response-scheduler' requester will send the kafka-topic name
            'cron' : true/false
        }
    '''

    # zip name = appId--serviceName.zip

    print(f"Request consumed from scheduler => {scheduler_request}")
    log.log_message('DEBUG', f"Request consumed from scheduler => {scheduler_request}")

    # initiating_deployer_process(scheduler_request)
    threading.Thread(target = initiating_deployer_process, args = (scheduler_request, )).start()
