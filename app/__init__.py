# Import flask and template operators
from flask import Flask, render_template

# Define the WSGI application object
from flask_restful import Api
from app.projects.resource import ProjectResource
from app.users.resource import UserResource

app = Flask(__name__)
api = Api(app)
logger = app.logger

# Configurations
app.config.from_object('config')

api.add_resource(ProjectResource, '/api/v1/<region>/project/', endpoint = 'project')
api.add_resource(UserResource, '/api/v1/<region>/user/<string:id>', endpoint = 'user')