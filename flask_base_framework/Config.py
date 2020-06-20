# -*- coding: utf-8 -*-

from datetime import timedelta
import os

# 取得目前專案執行路徑位置
current_path = os.getcwd()
# 取得目前專案執行路徑上一層位置
previous_path = current_path.rstrip(os.path.basename(current_path))

full_ProjectName = os.path.basename(previous_path.rstrip('/'))

# print("current_path: {}".format(current_path))
# print("previous_path: {}".format(previous_path))

''' 
Server Basic Config 
'''
class BaseConfig():

    # Flask 主要目錄設置
    static_url_path = '/static'
    static_folder = 'static'
    template_folder = 'templates'

    # Database DB API Arguments Config
    db_config = {
        'db_user': "",  # User
        'db_psw': "",  # User PassWord
        'db_host': "",  # DB Host
        'db_schema': ""  # DB Schema Name
    }

    # Session 生命週期
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

    # # DataBase Config
    # # UserWarning: Neither SQLALCHEMY_DATABASE_URI nor SQLALCHEMY_BINDS is set. Defaulting SQLALCHEMY_DATABASE_URI to "sqlite:///:memory:".
    # # https://segmentfault.com/q/1010000008767533
    # # 設置DB實體連接，以MySQL為例。
    SQLALCHEMY_DATABASE_URI = "mysql://{}:{}@{}/{}".format(
        db_config['db_user'], db_config['db_psw'], db_config['db_host'], db_config['db_schema'])
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLAlCHEMY_COMMIT_ON_TEARDOWN = False


''' Server start up for develop status config '''


class DevelopermentConfig(BaseConfig):

    DEBUG = True
    SECRET_KEY = "FLAskOsw12j/3yX R~Xkl!fgN]baseD/,?TT"


''' Server start up for formal status config '''


class ProductionConfig(BaseConfig):

    DEBUG = False
    SECRET_KEY = "flAsK02385m/4eq s~Xkl!fgN]baseP/,?RL"


# 環境模式參數設置
config = {

    'developermentConfig': DevelopermentConfig,
    'productionConfig': ProductionConfig,

}
