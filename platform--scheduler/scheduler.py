import heapq
from datetime import datetime
import pymongo
import threading
import time
from kafkaHandler import Producer, Consumer
import json
from crontab import CronTab
import getpass
import os
# from dotenv import load_dotenv
import copy
import heartbeatGenerator as heartbeat
import globalVariables
from loggingMessage import log_message





MONGO_SERVER_URL = "mongodb+srv://pranshu_mongo:iasproject@cluster0.svcqjdj.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB_NAME = "IAS_test_1"
MONGO_COLLECTION_NAME_S = "start_scheduling"
MONGO_COLLECTION_NAME_T = "terminate_scheduling"
MONGO_COLLECTION_NAME_SCH = "scheduler_status"
PRODUCER_TO_DEPLOYER="schedulerToDeployer"
CONSUMER_SCHEDULER="scheduler"
CONSUMER_RESPONSE_FROM_DEPLOYER="deployerToScheduler"


"""
//NOTE - Assumption of scheduler
# ! Assumptions
------------
REQUEST FORMAT:- request_id, appId,serviceName,startTime,endTime,scheduleType,isPeriodic,periodicity
1) * in service id of request means to run all the servicess
2) Type of schedule type will specify whether to start a service or end it
3) Start time and End time are data time formats in case of periodic they are just time
4) start time =0 means we have to deploy service now ..end time=0 means that this process doesn't require ending hence will not be pushed on the end_queue
5) Will work in two modes:- reinitialization and first startup
6) schedule will be of two type 0 or 1
        0--> terminate
        1--> end

"""


class start_request:
    def __init__(self, args):

        if len(args)>2:
            self.request_id = args[0]
            self.appId = args[1]
            self.serviceName = args[2]
            self.startTime = args[3]
            self.endTime = args[4]
            self.scheduleType=args[5]
            self.isPeriodic=args[6]
            self.periodicity=args[7]

        if len(args)==2:
            self.request_id=args[0]
            self.appId = args[1]["appId"]
            self.serviceName = args[1]["serviceName"]
            self.appName = args[1]["appName"]
            self.startTime = args[1]["startTime"]
            self.endTime = args[1]["endTime"]
            self.scheduleType=args[1]["scheduleType"]
            self.isPeriodic=args[1]["isPeriodic"]
            self.periodicity=args[1]["periodicity"]
            self.now=args[1]["now"]
            # self.accessToken=args[1]["accessToken"]
            self.cron=0


    # Define the comparison function for priority comparison
    def __lt__(self, other):
        return self.startTime < other.startTime

class end_request:
    def __init__(self, args):
        #request_id, appId,serviceName,startTime,endTime
        
        if len(args)>2:
            self.request_id = args[0]
            self.appId = args[1]
            self.serviceName = args[2]
            self.startTime = args[3]
            self.endTime = args[4]
            self.scheduleType=args[5]
            self.isPeriodic=args[6]
            self.periodicity=args[7]

        if len(args)==2:
            self.request_id=args[0]
            self.appId = args[1]["appId"]
            self.appName = args[1]["appName"]
            self.serviceName = args[1]["serviceName"]
            self.startTime = args[1]["startTime"]
            self.endTime = args[1]["endTime"]
            self.scheduleType=args[1]["scheduleType"]
            self.isPeriodic=args[1]["isPeriodic"]
            self.periodicity=args[1]["periodicity"]
            self.now=args[1]["now"]
            # self.accessToken=args[1]["accessToken"]
            self.cron=0

            

    # Define the comparison function for priority comparison
    def __lt__(self, other):
        return self.endTime < other.endTime

class CRON:
    def __init__(self):
        self.username = getpass.getuser()
        self.cron = CronTab(self.username)
    def make_a_cron(self,commands,comment,periodicity,value,time):
        # job = self.cron.new(command=commands)
        string = time[3:5] + " " +  time[:2]
        if periodicity==1:
            print("daily")
            string = string + " * * *"
        elif periodicity==2:
            string = string + " * * " + str(value)
        else:
            string = string + " * " + str(value) + " *"
        job = self.cron.new(command=commands)
        job.setall(string)  # Set the cron schedule
        job.set_comment(str(comment))  # Set the comment for the cron job
        self.cron.write()

        
    def remove_a_cron(self,comment):
        job = self.cron.find_comment(str(comment))
        self.cron.remove(job)
        self.cron.write()


class Scheduler:

    def __init__(self):
        # load_dotenv()
        self.client = pymongo.MongoClient(MONGO_SERVER_URL)
        self.database_s = self.client[MONGO_DB_NAME][MONGO_COLLECTION_NAME_S]
        self.database_t = self.client[MONGO_DB_NAME][MONGO_COLLECTION_NAME_T]
        self.database_sch = self.client[MONGO_DB_NAME][MONGO_COLLECTION_NAME_SCH]
        self.to_be_scheduled=[]
        self.to_be_terminated=[]
        self.semaphore_on_scheduled = threading.Semaphore(1)
        self.semaphore_on_terminating = threading.Semaphore(1)


        self.db = self.client[MONGO_DB_NAME]
        serviceRegistory = self.db["service_registry"]
        containerDetails = serviceRegistory.find_one({'app_name': 'platform', 'service_name' : 'kafka'})
        print(containerDetails)
        kafkaIp = containerDetails['ip']
        kafkaPortNo = str(containerDetails['port'])
        ipport=str(kafkaIp) +":"+ str(kafkaPortNo)
        self.bootstrap_servers = [ipport]
        self.consumer_request = Consumer(bootstrap_servers=self.bootstrap_servers, topic=CONSUMER_SCHEDULER, group_id="consumer-scheduler-request")
        self.producer = Producer(bootstrap_servers=self.bootstrap_servers)
        # !Meet Bros
        self.consumer_response = Consumer(bootstrap_servers=self.bootstrap_servers, topic=CONSUMER_RESPONSE_FROM_DEPLOYER, group_id="consumer-scheduler-response")
#--------------------------------------------------------------------------------------------------------------------

    def objecttojson(self,obj):
        request={
            "appId":obj.appId,
            "serviceName":obj.serviceName,
            "scheduleType":obj.scheduleType,
            "appName":obj.appName,
            "isPeriodic":obj.isPeriodic,
            "now":obj.now,
            "cron":obj.cron
        }
        return request

    def schedule_a_start_job(self,request_json):
        try:
            log_message("scheduler","DEBUG","Scheduling start of a job")
            request_on_db_s = self.database_s.insert_one(request_json)
            request_on_queue_s = start_request([request_on_db_s.inserted_id,request_json])
            print("[L+]Taking A Lock on scheduled @1")
            self.semaphore_on_scheduled.acquire()
            heapq.heappush(self.to_be_scheduled,request_on_queue_s)
            self.semaphore_on_scheduled.release()
            print("[L-]Releasing Lock on scheduled @1")
        except Exception as e:
            print(e)
            log_message("scheduler","ERROR","error occured at schedule_a_start_job: "+str(e)+" "+str(request_json))
            
            

    def add_scheduled_info_to_scheduledb(self,request_json):
        try:
            log_message("scheduler","DEBUG","Adding the service in DB")
            request_json["status"]="scheduled"
            request_on_db_sch = self.database_sch.insert_one(request_json)
            print(request_on_db_sch)
            print(request_on_db_sch.inserted_id)
            return str(request_on_db_sch.inserted_id)
        except Exception as e:
            print(e)
            log_message("scheduler","ERROR","error occured at add_scheduled_info_to_scheduledb: "+str(e)+" "+str(request_json))

    def schedule_a_end_job(self,request_json):
        try:
            log_message("scheduler","DEBUG","Scheduling end of a job")
            # print("[+]Checking for end time")
            request_on_db_t = self.database_t.insert_one(request_json)
            print("[L+]Taking lock on terminating queue @1")
            request_on_queue_t = end_request([request_on_db_t.inserted_id,request_json])
            self.semaphore_on_terminating.acquire()
            heapq.heappush(self.to_be_terminated,request_on_queue_t)
            self.semaphore_on_terminating.release()
            print("[L-]Releasing Lock on terminating @1")
        except Exception as e:
            log_message("scheduler","ERROR","error occured at schedule_a_end_job: "+str(e)+" "+str(request_json))

    def listen_request(self):
        print("[+]Starting the consumer")
        log_message("scheduler","DEBUG","Starting the scheduler")
        try:
            while True:
                request_json=self.consumer_request.consume_message()
                print("[+]Got A request")
                log_message("scheduler","DEBUG","Request Arrived!")
                # request_json=None
                # with open('test.json', 'r') as file:   
                #     request_json = json.load(file)
                # ? DEPLOY/TERMINATE NOW REQUESTS        
                if request_json["now"]==1:
                    if request_json["scheduleType"]==1:
                        print("[+]Deploy-Now Type Schedule")
                        log_message("scheduler","DEBUG","Deploy-Now Type Schedule")
                        currTime=time.time()
                        request_json["startTime"]=currTime
                        request_json["scheduleType"]="build-run"
                        self.schedule_a_start_job(request_json)
                        
                    else:
                        print("[+]Terminate Now request")
                        log_message("scheduler","DEBUG","Terminate-Now request")
                        request_json["endTime"]=currTime
                        request_json["scheduleType"]="stop"
                        self.schedule_a_end_job(request_json)
                else:
                    # ? DEPLOY-LATER/PERIODIC SCHEDULING
                    if request_json["scheduleType"]==1:
                        request_json["scheduleType"]="build-run"
                        # ? NON-PERIODIC SCHEDULING
                        if request_json["isPeriodic"]==0:
                            date_object = datetime.strptime(request_json["startTime"], "%Y-%m-%d %H:%M:%S")
                            request_json["startTime"]=datetime.timestamp(date_object)
                            self.schedule_a_start_job(request_json)
                            if request_json["endTime"]!=0:
                                date_object = datetime.strptime(request_json["endTime"], "%Y-%m-%d %H:%M:%S")
                                request_json["endTime"]=datetime.timestamp(date_object)
                                self.schedule_a_end_job(request_json)

                        # ? PERIODIC SCHEDULING
                        else:
                            # * Format:-self,commands,comment,periodicity,value,time
                            print("Periodic Scheduling")
                            log_message("scheduler","DEBUG","Periodic Scheduling")
                            services_=""
                            for i in request_json["serviceName"]:
                                services_=services_+i+" "
                            path_of_cwd=os.getcwd()
                            accessToken=self.add_scheduled_info_to_scheduledb(copy.deepcopy(request_json))
                            request_json["accessToken"] = accessToken
                            params_begin = str(request_json["appId"])+ " " + request_json["appName"] + " " + "begin-start" + " " + accessToken + " " + "1" + " " + services_
                            params_end = str(request_json["appId"])+ " " + request_json["appName"] + " " + "stop"+ " " + accessToken + " " + "1" + " " + services_
                            begin_command="python3 "+path_of_cwd+"/producer_for_cron.py " + params_begin
                            end_command="python3 "+path_of_cwd+"/producer_for_cron.py " + params_end
                            c_ron=CRON()
                            c_ron.make_a_cron(begin_command,request_json["appId"]+"_start",request_json["isPeriodic"],request_json["periodicity"],request_json["startTime"])
                            c_ron.make_a_cron(end_command,request_json["appId"]+"_end",request_json["isPeriodic"],request_json["periodicity"],request_json["endTime"])

                    
                    #// Terminate an application
                    # else:
                    #     # ? NON-PERIODIC
                    #     request_json["scheduleType"]="stop"
                    #     if request_json["isPeriodic"]==0:
                    #         date_object = datetime.strptime(request_json["startTime"], "%Y-%m-%d %H:%M:%S")
                    #         request_json["endTime"]=datetime.timestamp(date_object)
                    #         self.schedule_a_end_job(request_json)

                    #     # ? PERIODIC-SCHEDULING
                    #     else:
                    #         #// Format:-self,commands,comment,periodicity,value,time
                    #         services_=""
                    #         for i in request_json["serviceName"]:
                    #             services_=services_+i+""
                    #         params=request_json["appId"]+ " " + request_json["appName"] + " " + request_json["scheduleType"] + " " + services_
                    #         bcommand="python3 "+path_of_cwd+"/producer_for_cron.py " + params 
                    #         c_ron=CRON()
                    #         c_ron.make_a_cron(bcommand,request_json["appId"],request_json["isPeriodic"],request_json["periodicity"],request_json["startTime"])
        except Exception as e:
            log_message("scheduler","ERROR","error occured at listen_request thread: "+str(e)+" "+str(request_json))
            log_message("scheduler","CRITICAL","closing entire scheduler ")
            quit()


    def check_if_time_for_scheduling(self):
        print("[+]SCHEDULE queue thread start")
        log_message("scheduler","DEBUG","SCHEDULE queue thread start")
        while(True):
            while(True and len(self.to_be_scheduled)):
                print("Checking top of the schedule queue @2")
                smallest = self.to_be_scheduled[0]
                current_time = time.time()
                if smallest.startTime < current_time:
                    print("Sending request to kafka @2")
                    log_message("scheduler","DEBUG","Sending request to kafka(check start queue)")
                    request_for_depolyer=self.objecttojson(smallest)
                    accessToken=self.add_scheduled_info_to_scheduledb(copy.deepcopy(request_for_depolyer))
                    request_for_depolyer["accessToken"] = accessToken
                    print(request_for_depolyer)
                    print(type(request_for_depolyer))
                    self.producer.send_message(PRODUCER_TO_DEPLOYER, request_for_depolyer)
                    print("Taking A Lock on scheduled @2")
                    self.semaphore_on_scheduled.acquire()
                    heapq.heappop(self.to_be_scheduled)
                    self.semaphore_on_scheduled.release()
                    print("Releasing Lock on scheduled @2")
                    
                    print("deleting start request from db @2")
                    self.database_s.delete_one({"_id": smallest.request_id})

                else:
                    print("No request to schedule@2")
                    break
            time.sleep(1)
            
    def heat_beat_sender(self):
        print("starting heart-beat-sender")
        log_message("scheduler","DEBUG","starting heart-beat-sender")
        heartbeat.sendheartBeat("heartbeat-monitoring",globalVariables.node_name,globalVariables.container_name)

    def check_termination_queue(self):
        print("End queue thread start")
        log_message("scheduler","DEBUG","End queue thread start")
        while(True):
            while(True and len(self.to_be_terminated)):
                self.semaphore_on_terminating.acquire()
                smallest = heapq.heappop(self.to_be_terminated)
                self.semaphore_on_terminating.release()
                current_time = time.time()
                if smallest.endTime < current_time:
                    print("sending request to kafka @2")
                    log_message("scheduler","DEBUG","Sending request to kafka(check termination queue)")
                    request_for_depolyer=self.objecttojson(smallest)
                    accessToken=self.add_scheduled_info_to_scheduledb(copy.deepcopy(request_for_depolyer))
                    request_for_depolyer["accessToken"] = accessToken
                    self.producer.send_message("PRODUCER_TO_DEPLOYER", request_for_depolyer)
                    print("Taking A Lock on scheduled @2")
                    self.semaphore_on_scheduled.acquire()
                    heapq.heappop(self.to_be_scheduled)
                    self.semaphore_on_scheduled.release()
                    print("Releasing Lock on scheduled @2")
                    print("deleting start request from db @2")
                    self.database_s.delete_one({"_id": smallest.request_id})
                else:
                    print("No request to schedule")
                    # self.database_t.delete_one({"_id": smallest.request_id})
                    break
            time.sleep(1)


    def reponse_from_deployer(self):
        print("start response_listener thread")
        log_message("scheduler","DEBUG","start response_listener thread")
        while(True):
            response_json=self.consumer_response.consume_message()
            if response_json["scheduleType"]=="build-run":
                self.database_sch.collection.update_many(
                { "_id" : response_json["accessToken"]},
                { "$set" : { "status" : "running"} }
                )
            else:
                if response_json["cron"]==1:
                    if response_json["scheduleType"]=="build-run":
                        self.database_sch.collection.update_many(
                        { "_id" : response_json["accessToken"]},
                        { "$set" : { "status" : "scheduler"} }
                        )
                    else:
                        try:
                            c_ron=CRON()
                            c_ron.remove_a_cron(response_json["appId"]+"_start")
                            c_ron.remove_a_cron(response_json["appId"]+"_end")
                            self.database_sch.delete_many({"appId":response_json["appId"]})
                        except Exception as e:
                            log_message("scheduler","ERROR","response_from_deployer at removing cron : "+str(e)+" "+str(response_json))



                    

            



if __name__=="__main__" :
    myscheduler=Scheduler()
    accept_schedule_request=threading.Thread(target=myscheduler.listen_request)
    send_request_to_deployer_schedule=threading.Thread(target=myscheduler.check_if_time_for_scheduling)
    heart_beat_thread=threading.Thread(target=myscheduler.heat_beat_sender)
    send_request_to_deployer_terminate=threading.Thread(target=myscheduler.check_termination_queue)
    response_from_deployer=threading.Thread(target=myscheduler.reponse_from_deployer)
    
    accept_schedule_request.start()
    send_request_to_deployer_schedule.start()
    heart_beat_thread.start()
    send_request_to_deployer_terminate.start()
    response_from_deployer.start()

