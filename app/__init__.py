from flask import Flask

# Define the WSGI application object
from flask_restful import Api
from app.projects.resource import ProjectResource
from app.users.resource import UserResource
from app.virtualmachines.resource import VirtualMachineResource
from app.vm_count.resource import VmCountResource

app = Flask(__name__)
api = Api(app)
logger = app.logger

# Configurations placed in config.py in root directory
app.config.from_object('config')

# URL Mappings
api.add_resource(ProjectResource, '/api/v1/<region>/project/', endpoint='project')
api.add_resource(UserResource, '/api/v1/<region>/user/<string:username>', endpoint='user')
api.add_resource(VirtualMachineResource, '/api/v1/<region>/virtual_machine/', endpoint='virtual_machine')
api.add_resource(VmCountResource, '/api/v1/<region>/vm_count/', endpoint='vm_count')

from app import views
