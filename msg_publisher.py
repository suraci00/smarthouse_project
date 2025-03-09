import json
from google.auth import jwt
from google.cloud import pubsub_v1
from time import sleep
from secret import project_id, topic_name

service_account_info = json.load(open("credentials.json"))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=audience
)
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(project_id, topic_name)

try:
    topic = publisher.create_topic(request={"name": topic_path})
    print(f"Created topic: {topic.name}")
except Exception as e:
    print(e)


with open('data', 'r') as file:
    for line in file:
        message = line.strip()
        if message:
            data = json.dumps({"sensor_data": message})
            publisher.publish(topic_path, data.encode('utf-8'))
            print(f"Inviato: {message}")
        sleep(5)

