# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Api
from Config import config

import codecs

# 設定專案預設編碼格式
codecs.register(lambda name: codecs.lookup(
    'utf8') if name == 'utf8mb4' else None)

'''
Initialize Flask Instance
'''
app = Flask(__name__)

if config['run_mode_dev']:

    # 載入 Flask Config Setting Values，模式為 developermentConfig
    app.config.from_object(config['developermentConfig'])

else:

    # 載入 Flask Config Setting Values，模式為 productionConfig
    app.config.from_object(config['productionConfig'])


'''
Initialize Flask Restful API Instance
'''
api = Api(app)

'''
Import Restful API Module
'''
from Restful_API.FirstAPI import FirstAPI

'''
Register Restful API Module for Router
'''
api.add_resource(FirstAPI, '/firstapi',methods=['GET','POST'])

