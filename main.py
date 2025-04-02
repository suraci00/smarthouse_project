from flask import Flask, request, render_template
from google.cloud import firestore
from json import dumps, loads


base_url = 'https://pcloudsmarthouse.ew.r.appspot.com/'
app = Flask(__name__)
db = 'smarthouse'
coll = 'sensors'
db = firestore.Client.from_service_account_json('credentials.json', database = db)


@app.route('/',methods=['GET'])
def main():
    return 'ok'




@app.route('/sensors/pubsub', methods=['POST'])
def add_data(): #spacchettamento messaggi
    dict = loads(request.data.decode('utf-8'))
    print(dict)
    s = dict['message']['attributes']['s']
    date = dict['message']['attributes']['date']
    status = dict['message']['attributes']['status']
    store_data(s, date, status)
    return 'OK', 200

def store_data(s, date, status): #scrittura a db dei dati
    doc_ref = db.collection(coll).document(s)
    if doc_ref.get().exists:
        diz = doc_ref.get().to_dict()['sensors']
        diz[date] = status
        doc_ref.update({'sensors': diz})
    else:
        doc_ref.set({'sensors': {date: status}})



@app.route('/sensors/<s>',methods=['GET'])
def get_data(s):
    doc_ref = db.collection(coll).document(s)
    diz = doc_ref.get().to_dict()['sensors']
    if doc_ref.get().exists:
        #return dumps(db['sensors'][s])
        r = []
        diz = doc_ref.get().to_dict()['sensors']
        for k, v in diz.items():
            r.append([k, v])
        '''r = []
        for doc in db.collection(coll).stream():
            print(f'{doc.id} --> {doc.to_dict()}')
            r.append([doc.to_dict()['date'], doc.to_dict()['status']])'''
        return dumps(r)
    else:
        return 'sensor not found'

@app.route('/graph/<s>',methods=['GET'])
def graph(s):
    print(s)
    d = loads(get_data(s))
    ds = ''
    for date, status in d:
        ds += f"['{date}',{status}],\n"
    return render_template('graph.html', data = ds)

@app.route('/map',methods=['GET'])
def map():
    return render_template('map.html')

@app.route('/sensors',methods=['GET'])
def sensors():
    s = []
    for entity in db.collection(coll).stream():
        s.append(entity.id)
    return dumps(s),200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

