from kafkaHandler import Producer, Consumer
from loggingMessage import log_message

""" 
Checks all nodes are overloded or not 
"""
def check_all_usage(node_list,limit):
    """
    Function checks new free node required or not
    :param node_list: list of nodes details given by Node Manager
    :param limit: limit set (if all vm have more than limit then request new node)
    :return:bool(yes/no)
    """
    log_message("load-balancer", "DEBUG", "check_all_usage limit ...")
    for node in node_list:
        if node['vm_cpu_usage'] < limit:
            return False
    
    return True

""" 
Requests new node to node manager when all the nodes are overloaded 
"""
def request_new_node(new_node_request, new_node_response, kafka_server_main):
    """
    Function request new node and get new node
    :param:
    :return: json or none (node detail)
    """
    log_message("load-balancer", "DEBUG", "Reuesting new node")
    producer_nm = Producer(bootstrap_servers=kafka_server_main)

    req_msg = {
        "sender_name" : "load_balncer",
        "req_detail" : "getNewNode",
        "response" : "None"
    }
    producer_nm.send_message(new_node_request, req_msg)
    # producer_nm.flush()
    producer_nm.close()        

    log_message("load-balancer", "DEBUG", "Waiting for new node")
    # ------------------ Consume Node details from Node Manager ------------------
    consumer_nm = Consumer(bootstrap_servers=kafka_server_main, topic=new_node_response, group_id="consumer-request-new-node")

    message = consumer_nm.consume_message()
    consumer_nm.close()
    log_message("load-balancer", "DEBUG", "New Node recieved")
    if len(message["response"]) > 0 :
        log_message("load-balancer", "DEBUG", "New Node is available")
        return message["response"][0]
    else :
        log_message("load-balancer", "DEBUG", "New Node is not available")
        return None

""" 
Calculates best node give list of node details 
"""
def get_best_node(nodes_list):
    log_message("load-balancer", "DEBUG", "calculating best node")
    best_node = None
    min_load = 10000000
    
    for node in nodes_list:

        load = (2 * node['vm_cpu_usage'] * node['ram_usage']) / (node['vm_cpu_usage'] + node['ram_usage'])

        if(load < min_load) :
            min_load = load
            best_node = node

    return best_node

"""
Change Message format for deployer
"""
def change_response_format(input_node):
    """
    Returns json with detils required by deplyer 
    """
    ans = {}
    ans["ip"] = input_node["ip"]
    ans["user_name"] = input_node["user_name"]
    ans["password"] = input_node["password"]
    ans["port"] = input_node["port"]
    ans["node_name"] = input_node["node_name"]

    
    return ans
