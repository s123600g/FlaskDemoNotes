# -*- coding: utf-8 -*-

class BaseConfig():

    # Flask 主要目錄設置
    static_url_path = ''
    static_folder = ''
    template_folder = ''


class DevelopermentConfig(BaseConfig):

    DEBUG = True
    SECRET_KEY = "flask1A556j/33X *~X2l!fgN]HelloWorlD/,?RT"


# 環境模式參數設置
config = {
    'developermentConfig': DevelopermentConfig,
}
