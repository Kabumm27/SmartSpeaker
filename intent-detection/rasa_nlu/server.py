import os
import json
from rasa_nlu.model import Interpreter
from bottle import route, run, request

# Load latest model
dirname = os.path.dirname(__file__)
interpreter = Interpreter.load(dirname + '/models/default/current')


# Start server
@route('/parse')
def index():
    text = request.query.q
    return interpreter.parse(text)


run(host='0.0.0.0', port=5000)
