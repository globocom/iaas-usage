from flask_script import Manager
from app import app

manager = Manager(app)


@manager.command
def create_db():
    """Creates the MySQL database schema"""
    import app.auditing.models
    app.logger.info("Creating database")
    app.db.create_all()


@manager.command
def destroy_db():
    """Drops the MySQL database schema"""
    import app.auditing.models
    app.logger.info("Destroying database")
    app.db.drop_all()


@manager.command
def runserver():
    """"Runs the application on the default port (8080)"""
    app.run(port=8080)


@manager.command
def read_events():
    from app.auditing.event_reader import CloudstackEventReader
    CloudstackEventReader('local').read_events()

if __name__ == "__main__":
    manager.run()
