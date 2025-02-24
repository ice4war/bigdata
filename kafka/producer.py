import requests
import json
import time
from kafka import *
from kafka.admin import KafkaAdminClient, NewTopic

def url_response(url: str="https://randomuser.me/api/?results=1") -> dict:
    response = requests.get(url)
    data = response.json()
    results = data["results"][0]

    return results


def data(results: dict) -> dict:
    kafka_data = {}

    kafka_data["full_name"] = f"{results['name']['title']}. {results['name']['first']} {results['name']['last']}"
    kafka_data["gender"] = results["gender"]
    kafka_data["location"] = f"{results['location']['street']['number']}, {results['location']['street']['name']}"
    kafka_data["city"] = results['location']['city']
    kafka_data["country"] = results['location']['country']
    kafka_data["postcode"] = results['location']['postcode']
    kafka_data["latitude"] = float(results['location']['coordinates']['latitude'])
    kafka_data["longitude"] = float(results['location']['coordinates']['longitude'])
    kafka_data["email"] = results["email"]

    return kafka_data
admin_client = KafkaAdminClient(bootstrap_servers=["localhost:9092"])
producer = KafkaProducer(bootstrap_servers = "localhost")
consumer = KafkaConsumer(bootstrap_servers = "localhost")

def create_topics(topic_names):

    existing_topic_list = consumer.topics()
    print(list(consumer.topics()))
    topic_list = []
    for topic in topic_names:
        if topic not in existing_topic_list:
            print('Topic : {} added '.format(topic))
            topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))
        else:
            print(f'Topic : {topic} already exist.')
    try:
        if topic_list:
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print("Topic Created Successfully")
        else:
            print("Topic Exist")
    except TopicAlreadyExistsError as e:
        print("Topic Already Exist")
    except  Exception as e:
        print(e)
topic_list = ["KafkaPipeline"]
create_topics(topic_list)


minutes = float(input("Enter minutes to run : "))
end_time = time.time() + (minutes * 60)

while True:
	if time.time() > end_time:
		break
	kafka_data = data(url_response())
	producer.send("KafkaPipeline",json.dumps(kafka_data).encode('utf-8'))
	print(kafka_data)
	time.sleep(1)
