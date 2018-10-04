from rasa_nlu.model import Interpreter
from bottle import route, run, request

# Load latest model
interpreter = Interpreter.load('models/default/current')


# Start server
@route('/parse')
def index():
    text = request.query.q
    return interpreter.parse(text)


run(host='0.0.0.0', port=5000)
