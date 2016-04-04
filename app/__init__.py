# Import basic app infrastructure objects
from flask_restful import Api
from flask_login import LoginManager
from flask import Flask
from threading import Thread
import schedule
import time
from flask.ext.cache import Cache

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

# Configurations placed in config.py in root directory
app.config.from_object('config')
logger = app.logger

# Import app resources
from usage_record.reader import UsageRecordReader
from usage_record.resource import UsageRecordResource
from app.projects.resource import ProjectResource
from app.users.resource import UserResource
from app.virtualmachines.resource import VirtualMachineResource
from app.storage.resource import StorageResource

# Resource URL Mappings
api.add_resource(ProjectResource, '/api/v1/<region>/project/', endpoint='project')
api.add_resource(UserResource, '/api/v1/<region>/current_user/', endpoint='user')
api.add_resource(VirtualMachineResource, '/api/v1/<region>/virtual_machine/', endpoint='virtual_machine')
api.add_resource(StorageResource, '/api/v1/<region>/storage/', endpoint='storage')
api.add_resource(UsageRecordResource, '/api/v1/<region>/usage_record/', endpoint='usage_record')

if app.config['USAGE_ENABLED']:
    from app.usage_record.views import index_usage

    for region in app.config['USAGE_REGIONS']:
        if region:
            schedule.every().day.at(app.config['USAGE_TIME']).do(UsageRecordReader(region).index_usage)

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    Thread(target=run_schedule).start()

from app import views
from app.auth import views
