from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import APP, DB


manager = Manager(APP)
migrate = Migrate(APP, DB)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
