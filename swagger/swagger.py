from flask import Flask, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

from routes.server import appServer

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

app.register_blueprint(appServer, url="")

swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'SmartTrack API'),
        'version': LazyString(lambda: '0.1'),
        'description': LazyString(lambda: 'This document will describe all functionalities from SmartTrack API. (Enjoy) <style>.models {display: none !important}</style>'),
    },
    host = LazyString(lambda: request.host)
)

swagger = Swagger(app, template=swagger_template)