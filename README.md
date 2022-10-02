# SmartBack



## Kafka Commands

Reference: https://medium.com/@TimvanBaarsen/apache-kafka-cli-commands-cheat-sheet-a6f06eac01b

Login to Kafka Container: ``docker-compose exec kafka bash``

- To list topics in the Kafka Container:
   - `docker-compose exec kafka bash`
   - `$KAFKA_HOME/bin/kafka-topics.sh --zookeeper zookeeper:2181 --list`
   

- To get the offset on a topic:
   - ``$KAFKA_HOME/bin/kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list kafka:9092 --topic semgsensor-alerts-local --partitions 0`` 


- To produce a message to a topic:
   - `` $KAFKA_HOME/bin/kafka-console-producer.sh --broker-list kafka:9092 --topic semgsensor-alerts-local``


- To consume a message from a topic (from beginning)
    - `` $KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic semgsensor-alerts-local --from-beginning ``

##### Authentication

https://simpleisbetterthancomplex.com/tutorial/2018/11/22/how-to-implement-token-authentication-using-django-rest-framework.html

### **To Connect to Kafka using Offset Explorer**

_Use the PlainText Host value in the Advanced tab for the Bootstrap Servers field:_

##### **Bootstrap Servers: 127.0.0.1:29094**

`KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://127.0.0.1:29094`


Consumption started after network is added for services: kafka and zookeeper like backend.