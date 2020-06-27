# -*- coding: utf-8 -*-

from Startup import app,db
from flask_script import Manager, Command
from flask_migrate import Migrate, MigrateCommand

# Create Flask Manager Instance
manager = Manager(app)
# Create Flask Migrate Instance
migrate = Migrate(app, db)

# Create manager command for database activity. ex: init(initialize)、migrate、upgrade(commit)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

    manager.run()
