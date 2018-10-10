from __future__ import unicode_literals, print_function

import io
import json

from snips_nlu import SnipsNLUEngine
from bottle import route, run, request


nlu_engine = SnipsNLUEngine.from_path("models/current")


# Start server
@route('/parse')
def index():
    text = request.query.q
    return nlu_engine.parse(text)


run(host='0.0.0.0', port=5001)
