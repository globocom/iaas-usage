# Import flask and template operators
from flask import Flask, render_template

# Define the WSGI application object
from flask_restful import Api
from app.projects.resource import ProjectResource

app = Flask(__name__)
api = Api(app)
logger = app.logger

# Configurations
app.config.from_object('config')

api.add_resource(ProjectResource, '/api/v1/<region>/project/', endpoint = 'project')