# -*- coding: utf-8 -*-

from flask import Flask
from Config import config

app = Flask(__name__)

# 載入 Flask Config Setting Values，模式為 developermentConfig
app.config.from_object(config['developermentConfig'])

@app.route("/helloworld", methods=['GET'])
def helloworld():

    return "Hello World!!"
