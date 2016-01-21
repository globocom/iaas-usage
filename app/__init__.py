# Import basic app infrastructure objects
from flask import Flask
from flask_restful import Api
from flask_login import LoginManager

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Import app resources
from app.projects.resource import ProjectResource
from app.users.resource import UserResource
from app.virtualmachines.resource import VirtualMachineResource

# Configurations placed in config.py in root directory
app.config.from_object('config')
logger = app.logger

# Resource URL Mappings
api.add_resource(ProjectResource, '/api/v1/<region>/project/', endpoint='project')
api.add_resource(UserResource, '/api/v1/<region>/current_user/', endpoint='user')
api.add_resource(VirtualMachineResource, '/api/v1/<region>/virtual_machine/', endpoint='virtual_machine')

from app import views
from app.auth import views