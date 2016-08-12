# Import basic app infrastructure objects
import os
from flask_restful import Api
from flask_login import LoginManager
from flask import Flask
from flask.ext.cache import Cache
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from sqlalchemy.orm import Session

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

app.config.from_object(os.getenv('ENV', 'app.config.DevConfig'))
logger = app.logger
db = SQLAlchemy(app)

@app.teardown_request
def session_clear(exception=None):
    db.session.close()
    if exception and Session.is_active:
        db.session.rollback()

if app.config['SENTRY_DSN']:
    sentry = Sentry(app)

# Import app resources
from usage_record.resource import UsageRecordResource
from app.projects.resource import ProjectResource
from app.users.resource import UserResource
from app.virtualmachines.resource import VirtualMachineResource
from app.storage.resource import StorageResource
from app.capacity.resource import CloudCapacityResource
from app.service_offering.resource import ServiceOfferingResource
from app.auditing.resource import AuditingEventListResource, ListResourceTypeResource, ListActionResource
from app.auditing.resource import AuditingEventResource
from app.region.resource import RegionResource
from app.health.resource import HealthResource

# Resource URL Mappings
api.add_resource(ProjectResource, '/api/v1/<region>/project/', endpoint='project')
api.add_resource(UserResource, '/api/v1/<region>/current_user/', endpoint='user')
api.add_resource(VirtualMachineResource, '/api/v1/<region>/virtual_machine/', endpoint='virtual_machine')
api.add_resource(StorageResource, '/api/v1/<region>/storage/', endpoint='storage')
api.add_resource(UsageRecordResource, '/api/v1/<region>/usage_record/', endpoint='usage_record')
api.add_resource(CloudCapacityResource, '/api/v1/<region>/cloud_capacity/', endpoint='cloud_capacity')
api.add_resource(ServiceOfferingResource, '/api/v1/<region>/service_offering/', endpoint='service_offering')
api.add_resource(AuditingEventListResource, '/api/v1/<region>/auditing_event/', endpoint='auditing_events')
api.add_resource(AuditingEventResource, '/api/v1/<region>/auditing_event/<id>', endpoint='auditing_event')
api.add_resource(ListResourceTypeResource, '/api/v1/auditing_event/resource_type', endpoint='resource_type')
api.add_resource(ListActionResource, '/api/v1/auditing_event/action', endpoint='action')
api.add_resource(RegionResource, '/api/v1/region/', endpoint='region')
api.add_resource(HealthResource, '/health', endpoint='health')

from app import views
from app.auth import views

if app.config['BATCH_NODE']:
    from app.usage_record.views import index_usage
    from app.auditing.views import consume_audit_queue
