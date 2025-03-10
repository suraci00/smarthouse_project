
from flask import Flask,request
from google.cloud import pubsub_v1
from google.cloud import firestore
from json import loads
from base64 import b64decode
from secret import project_id,topic_name

base_url = 'https://pcloudsmarthouse.ew.r.appspot.com/'
app = Flask(__name__)
'''db = 'smarthouse'
coll = 'sensors'
db = firestore.Client.from_service_account_json('credentials.json', database = db)'''
@app.route('/',methods=['GET'])
def main():
    return 'ok'

@app.route('/pubsub/write',methods=['GET'])
def pubsub_write():
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    r = publisher.publish(topic_path, b'sensor', key1='')
    return r.result()


'''def add_data(s):
    data = request.values['data']
    val = float(request.values['val'])
    doc_ref = db.collection(coll).document(s)
    if doc_ref.get().exists:
        l = doc_ref.get().to_dict()['sensors']
        l.append(data, val)
    else:
        doc_ref.set({'sensors': [(data, val)]})
    return 'OK', 200'''

@app.route('/pubsub/push', methods=['POST'])
def pubsub_push():
    print('ricevuto payload',flush=True)
    dict = loads(request.data.decode('utf-8')) # deserializzazione
    print(dict,flush=True)
    msg = b64decode(dict['message']['data']).decode('utf-8')
    print(msg)
    return 'OK',200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

