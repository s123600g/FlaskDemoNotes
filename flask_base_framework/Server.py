# -*- coding: utf-8 -*-

from flask import Flask , render_template
from flask_sqlalchemy import SQLAlchemy
from Config import config

import codecs

# 設定專案預設編碼格式
codecs.register(lambda name: codecs.lookup(
    'utf8') if name == 'utf8mb4' else None)

app = Flask(__name__)

# 載入 Flask Config Setting Values，模式為 developermentConfig
app.config.from_object(config['developermentConfig'])

# 載入 Flask Config Setting Values，模式為 productionConfig
# app.config.from_object(config['productionConfig'])

# Create SQLAlchemy Instance
db = SQLAlchemy(app)

'''
----------------------------------------------------------------------
從Model中匯入資料表模型
----------------------------------------------------------------------
'''
from Model import Base_Data
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
網站頁面-404 Not Found實作區塊 
----------------------------------------------------------------------
'''
@app.errorhandler(404)
def page_not_found(e): # 404 Not Found頁面
    return 'NotFound404.html', 404
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
頁面-index 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/index", methods=['GET'])
def index():

    return render_template('index.html')
'''-------------------------------------------------------------------'''


