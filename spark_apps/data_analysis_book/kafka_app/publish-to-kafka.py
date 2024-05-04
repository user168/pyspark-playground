# Method posts events to Kafka Server
# run command in kafka server to create topic : 
# ./usr/bin/kafka-topics --create --topic device_data --bootstrap-server kafka:9092 
from kafka import KafkaProducer, KafkaConsumer
import time
import random

# Generate random events data
import datetime
import time
import uuid
import random
import json

event_status: list = ["SUCCESS", "ERROR", "STANDBY"] + [None]
device_id: list = ['D' + str(_id).rjust(3, '0') for _id in range(1, 6)] + [None]
customer_id: list = ["CI" + str(_id).rjust(5, '0') for _id in range(100, 121)]


# Generate event data from devices
def generate_events(offset=0):
    _event = {
        "eventId": str(uuid.uuid4()),
        "eventOffset": offset,
        "eventPublisher": "device",
        "customerId": random.choice(customer_id),
        "data": {
            "devices": [
                {
                    "deviceId": random.choice(device_id),
                    "temperature": random.randint(0, 30),
                    "measure": "C",
                    "status": random.choice(event_status)
                } for i in range(random.randint(0, 3))
            ],
        },
        "eventTime": str(datetime.datetime.now())
    }

    return json.dumps(_event)



# if __name__ == "__main__":
#     _offset = 10000
#     while True:
#         print(generate_events(offset=_offset))
#         time.sleep(random.randint(0, 5))
#         _offset += 1



__bootstrap_server = "localhost:9092"


def post_to_kafka(data):
    print('data: '+ str(data))
    producer = KafkaProducer(bootstrap_servers=__bootstrap_server)
    producer.send('devices', key=b'device', value=data)
    #producer.flush()
    producer.close()
    print("Posted to topic")


if __name__ == "__main__":
    _offset = 10000
    while True:
        post_to_kafka(bytes(str(generate_events(offset=_offset)), 'utf-8'))
        time.sleep(random.randint(2, 5))
        _offset += 1