# -*- coding: utf-8 -*-

from flask import Flask
from flask_script import Manager, Server, Command
from flask_migrate import Migrate, MigrateCommand
from Server import app
from Server import db
import datetime as dtime

# Create Flask Manager Instance
manager = Manager(app)
# Create Flask Migrate Instance
migrate = Migrate(app, db)

# Create manager command for database activity. ex: init(initialize)、migrate、upgrade(commit)
manager.add_command('db', MigrateCommand)

# 使用flask-script和flask-migrate
# https://blog.csdn.net/qq_33279781/article/details/79803376

# 使用flask-script管理資料庫更動，命令如下：
# python manage.py db init  #初次使用

# python manage.py db migrate

# python mange.py db upgrade

# python mange.py db --help

if __name__ == '__main__':

    manager.run()
