import os
from dateutil.parser import parse
from flask import Flask, request, render_template, jsonify
from google.cloud import firestore
from json import dump, dumps, load, loads, JSONDecodeError
from datetime import datetime


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
    ds = "[\n" + ",\n".join(f"['{datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')}', '{status}']" for date, status in d) + "\n]"
    return render_template('graph.html', data = ds)

@app.route('/map',methods=['GET'])
def map():
    return render_template('map.html')

@app.route('/active_map',methods=['GET'])
def active_map():
    return render_template('active_map.html')

@app.route('/sensors',methods=['GET'])
def sensors():
    s = []

    for entity in db.collection(coll).stream():
        s.append(entity.id)
    return dumps(s),200


@app.route('/active',methods=['GET'])
def active():
    bs = {}
    cutoff = datetime.strptime('2010-01-06 12:45:00.000000', '%Y-%m-%d %H:%M:%S.%f')

    for entity in db.collection(coll).stream():
        bs[entity.id] = []
        doc_ref = db.collection(coll).document(entity.id)
        diz = doc_ref.get().to_dict()['sensors']
        filtered = []

        for k, v in diz.items():
            ts = datetime.strptime(k, '%Y-%m-%d %H:%M:%S.%f')
            if ts > cutoff:
                filtered.append([k, v])

        if filtered:  # SOLO se ha almeno un evento valido
            bs[entity.id] = filtered

    return jsonify(bs), 200


@app.route('/save_markers', methods=['GET', 'POST'])
def save_markers():
    new_data = request.get_json()

    # Se il file esiste, carica i dati attuali
    if os.path.exists('static/data/markers.json'):
        with open('static/data/markers.json', 'r') as f:
            try:
                existing_data = load(f)
            except JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Combina i dati: aggiungi quelli nuovi
    combined_data = existing_data + new_data

    # Salva tutto nel file
    with open('static/data/markers.json', 'w') as f:
        dump(combined_data, f, indent=2)

    return jsonify({'status': 'ok'}), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

