from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json

class Producer:
    """
    A class for handling Kafka Producer.
    """

    def __init__(self, bootstrap_servers):
        """
        Initialize Kafka producer with given bootstrap_servers
        :param bootstrap_servers: List of Kafka broker addresses.
        """
        self.producer = None
        while True:
            try:
                self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=self.json_serializer)
                break
            except:
                pass

    def json_serializer(self,data):
        return json.dumps(data).encode("utf-8")

    def send_message(self, topic, message):
        """
        Send message to Kafka topic.
        :param topic: Kafka topic name.
        :param message: Message to be sent.
        :return: None
        """
        try:
            self.producer.send(topic, message)
            self.producer.flush()
        except KafkaError as ke:
            print(f'Error while sending message to topic {topic}: {ke}')


    def close(self):
        """
        Close Kafka producer.
        :return: None
        """
        self.producer.close()


class Consumer:
    """
    A class for handling Kafka Consumer.
    """

    def __init__(self, bootstrap_servers, topic, group_id=None):
        """
        Initialize Kafka Consumer with given bootstrap_servers and group_id.
        :param bootstrap_servers: List of Kafka broker addresses.
        :param topic: Kafka topic name to consume from.
        :param group_id: Consumer group ID.
        """
        self.consumer = None
        while True:
            try:
                self.consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers, group_id=group_id)
                self.consumer.subscribe(topic)
                break
            except:
                pass

    def consume_message(self, auto_commit=True):
        """
        Consume messages from Kafka topic.
        :param auto_commit: If True, consumer offsets will be committed automatically.
        :param timeout_ms: Maximum time to block waiting for messages (in milliseconds).
        :return: Message consumed from Kafka topic.
        """
        try:
            for message in self.consumer:
                if auto_commit:
                    self.consumer.commit()
                return json.loads(message.value)

        except KeyboardInterrupt:
            pass
        except KafkaError as ke:
            print(f'Error while consuming message from topic: {ke}')


    def close(self):
        """
        Close Kafka Consumer.
        :return: None
        """
        self.consumer.close()
