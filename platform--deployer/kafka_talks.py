from kafkaHandler import Producer, Consumer
import global_variables, kafka_info

kafkaIp = kafka_info.get_kafka_info()['ip']
kafkaPortNo = str(kafka_info.get_kafka_info()['port'])

def send_using_kafka(topic,message):
   
    # waiting for kafka-server to start

    producer = Producer(bootstrap_servers=[kafkaIp+":"+kafkaPortNo])
    producer.send_message(topic, message)
    producer.close()


def receive_using_kafka(topic):

    # waiting for kafka-server to start

    consumer = Consumer(bootstrap_servers=[kafkaIp+":"+kafkaPortNo], topic=topic, group_id="consumer-deployer")
    message = consumer.consume_message()
    consumer.close()
    return message
