# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask
from flask_cors import CORS

import v1


def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)
    app.register_blueprint(
        v1.bp,
        url_prefix='/v1')
    return app


if __name__ == '__main__':
    create_app().run('0.0.0.0', port=5003)
