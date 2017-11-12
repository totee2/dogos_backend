import flask
from flask import Flask, send_from_directory
import graphlab
import random
from graphlab import SFrame
import json
from pymongo import MongoClient
app = Flask(__name__)

path = ''

model = None
images = None
db = None
has_been_loaded = False


def get_images_from_ids(query_result, images):
    return images.filter_by(query_result['reference_label'], 'id')


def query_model(dogo, model, images):
    neighbours = get_images_from_ids(model.query(dogo, k=20), images)

    image_list = SFrame(data=None)

    shown_dogs = {dogo['images'][0][0]}

    for i in range(0, len(neighbours)):
        if len(shown_dogs) < 6:
            if neighbours[i]['images'][0] not in shown_dogs:
                # neighbours[i]['image'].show()
                dogo_clone = neighbours[i:i+1].copy()
                image_list = image_list.append(SFrame(dogo_clone))
                shown_dogs.add(neighbours[i]['images'][0])
        else:
            break

    return image_list


def make_json(dog_data):
    dog_json = {}
    counter = 0
    for dog in dog_data:
        dog_info = dog['response']['dog0']
        dog_json['dog' + str(counter)] = dog_info
        counter += 1

    return json.dumps(dog_json)


@app.route('/find_your_dog/<int:dog_id>')
def closest_dogs(dog_id):

    if not has_been_loaded:
        load_features()
    if dog_id < db.dogos.count():
        response = db.dogos.find_one({"query": dog_id})
        if response is None:
            # dogo = images[dog_id: dog_id + 1]
            # neighbours = query_model(dogo, model, images)
            # resp = flask.Response(make_json(dogo.append(neighbours)))
            resp = flask.Response(starter_dogs())
        else:
            resp = flask.Response(json.dumps(response['response']))

    else:
        resp = flask.Response(json.dumps({'Warning': 'Stop fiddling around in my backend!!'}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/find_your_dog/start')
def starter_dogs():

    if not has_been_loaded:
        load_features()
    num_dogs = db.dogos.count()
    dog_numbers = random.sample(xrange(num_dogs), 6)
    dog_data = db.dogos.find({'query': {'$in': dog_numbers}})
    return make_json(dog_data)


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


@app.route("/full/<file>")
def serv_file(file=None):
    return send_from_directory('full', file)


def load_features():
    global images, model, db, has_been_loaded

    print 'Loading features'

    # images = graphlab.load_sframe(path + 'my_images')
    # model = graphlab.load_model(path + 'my_model')
    client = MongoClient("localhost")
    db = client.dogos
    has_been_loaded = True


if __name__ == "__main__":
    app.run(host='0.0.0.0')
