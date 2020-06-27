# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
Initialize Flask SQLAlchemy Instance
'''
db = SQLAlchemy(app)

'''
----------------------------------------------------------------------
註冊資料表模型
----------------------------------------------------------------------
'''
from BaseData.BaseData import Base_Data
'''-------------------------------------------------------------------'''

