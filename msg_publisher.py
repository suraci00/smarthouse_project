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


with open('data', 'r') as f:
    for l in f.readlines():
        values = l.split()
        date = f"{values[0]} {values[1]}"
        if "." not in date:
            date += ".000000"  # Aggiunge i microsecondi mancanti
        #date = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S.%f")
        s = values[2]
        status = values[3]
        print(date, s, status)

        r = publisher.publish(topic_path, b'sensor', s = s, date = date, status = status)
        sleep(1)

print('done')