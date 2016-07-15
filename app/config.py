import ast
import os


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = ast.literal_eval(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False'))

    if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT') is None:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SECRET_KEY = os.getenv('SESSION_SECRET_KEY', '1')
    OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
    OAUTH_AUTH_URL = os.getenv('OAUTH_AUTH_URL')
    OAUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')
    OAUTH_USER_URL = os.getenv('OAUTH_USER_URL')
    OAUTH_LOGOUT_URL = os.getenv('OAUTH_LOGOUT_URL')
    OAUTH_REDIRECT_URL = os.getenv('OAUTH_REDIRECT_URL')
    BACKSTAGE_BAR_ADDRESS = os.getenv('BACKSTAGE_BAR_ADDRESS')

    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')
    ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT')
    ELASTICSEARCH_CLIENT = os.getenv('ELASTICSEARCH_CLIENT')
    ELASTICSEARCH_INDEX = os.getenv('ELASTICSEARCH_INDEX')
    ELASTICSEARCH_TYPE = os.getenv('ELASTICSEARCH_TYPE')
    LOGSTASH_HOST = os.getenv('LOGSTASH_HOST')
    LOGSTASH_PORT = os.getenv('LOGSTASH_PORT')
    USAGE_API_BATCH_SIZE = os.getenv('USAGE_API_BATCH_SIZE', '100')
    USAGE_REGIONS = os.getenv('USAGE_REGIONS', '').split(',')
    USAGE_TIME = os.getenv('USAGE_TIME', '04:00')
    USAGE_CACHE_TIME = int(os.getenv('USAGE_CACHE_TIME', 60*60*24)) # 1 day cache
    USAGE_ENABLED = ast.literal_eval(os.getenv('USAGE_ENABLED', 'False'))
    USAGE_MINIMUM_TIME = os.getenv('USAGE_MINIMUN_TIME', 1) #1 hour
    REGION_LIST = os.getenv('REGION_LIST', '').split(',')

    EVENT_QUEUE_HOST = os.getenv('EVENT_QUEUE_HOST', 'localhost')
    EVENT_QUEUE_EXCHANGE = os.getenv('EVENT_QUEUE_EXCHANGE', 'cloudstack-events')
    EVENT_QUEUE_NAME = os.getenv('EVENT_QUEUE_NAME', 'iaas-usage-events')
    EVENT_ROUTING_KEY_TEMPLATE = os.getenv('EVENT_ROUTING_KEY_TEMPLATE', 'management-server.ActionEvent.%s.*.*')
    EVENT_LIST = [
        'LB-CREATE',
        'LB-DELETE',
        'LB-ASSIGN-TO-RULE',
        'LB-REMOVE-FROM-RULE',
        'LB-HEALTHCHECKPOLICY-CREATE',
        'LB-HEALTHCHECKPOLICY-UPDATE',
        'LB-STICKINESSPOLICY-CREATE',
        'NETWORK-DELETE',
        'NETWORK-CREATE',
        'NETWORK-RESTART',
        'PROJECT-ACCOUNT-ADD',
        'PROJECT-CREATE',
        'PROJECT-DELETE',
        'SERVICE-OFFERING-CREATE',
        'SERVICE-OFFERING-DELETE',
        'VMSNAPSHOT-CREATE',
        'VMSNAPSHOT-DELETE',
        'VMSNAPSHOT-REVERT',
        'TEMPLATE-COPY',
        'TEMPLATE-CREATE',
        'TEMPLATE-DELETE',
        'TEMPLATE-EXTRACT',
        'USER-LOGIN',
        'NIC-CREATE',
        'NIC-DELETE',
        'NIC-UPDATE',
        'AUTOSCALE-SCALEUP',
        'AUTOSCALE-SCALEUP-FAILED',
        'AUTOSCALE-SCALEDOWN',
        'AUTOSCALE-SCALEDOWN-FAILED',
        'AUTOSCALEVMGROUP-CREATE',
        'AUTOSCALEVMGROUP-UPDATE',
        'AUTOSCALEVMGROUP-DELETE',
        'AUTOSCALEVMGROUP-DISABLE',
        'AUTOSCALEVMGROUP-ENABLE',
        'VM-CREATE',
        'VM-DESTROY',
        'VM-MIGRATE',
        'VM-REBOOT',
        'VM-RESTORE',
        'VM-START',
        'VM-STOP',
        'VM-EXPUNGE',
        'VM-UPGRADE',
        'ROUTER-REBOOT',
        'ROUTER-RESTART',
        'ROUTER-STOP',
        'ROUTER-DESTROY',
        'ROUTER-START',
        'ROUTER-MIGRATE',
        'VOLUME-ATTACH',
        'VOLUME-CREATE',
        'VOLUME-DELETE',
        'VOLUME-DETACH'
    ]


class ProdConfig(Config):

    DEBUG = False


class DevConfig(Config):

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/iaas_usage'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestConfig(Config):

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = True