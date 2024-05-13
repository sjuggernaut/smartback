from kafka import KafkaConsumer,KafkaProducer

# producer = KafkaProducer(
#     bootstrap_servers=['kafka:29092'], acks="all"
# )
# producer.send('semgsensor-alerts-local', "message".encode("utf-8"))

import logging
# logging.basicConfig(level=logging.DEBUG)

consumer = KafkaConsumer('semgsensor-alerts-local', bootstrap_servers='kafka:29092', api_version=(0,10,1))
print(consumer)

logger = logging.getLogger(__name__)

for msg in consumer:
    print(msg.value)