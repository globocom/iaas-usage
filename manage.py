from flask_script import Manager, Command, Option
from app import app

manager = Manager(app)


@manager.command
def create_db():
    """Creates the MySQL database schema"""
    import app.auditing.models
    import app.projects.models
    app.logger.info("Creating database")
    app.db.create_all()


@manager.command
def destroy_db():
    """Drops the MySQL database schema"""
    import app.auditing.models
    import app.projects.models
    app.logger.info("Destroying database")
    app.db.drop_all()


@manager.command
def runserver():
    """"Runs the application on the default port (8080)"""
    app.run(port=8080)


class GunicornServer(Command):
    """Run the app within Gunicorn"""

    def get_options(self):
        from gunicorn.config import make_settings

        settings = make_settings()
        options = []

        for setting, klass in settings.items():
            if klass.cli:
                if klass.const is not None:
                    options.append(Option(*klass.cli, const=klass.const, action=klass.action))
                else:
                    options.append(Option(*klass.cli, action=klass.action))

        return options

    def run(self, *args, **kwargs):
        from gunicorn.app.wsgiapp import WSGIApplication

        app = WSGIApplication()
        app.app_uri = 'manage:app'
        return app.run()


manager.add_command("gunicorn", GunicornServer())

if __name__ == "__main__":
    manager.run()
